import sys
import time
import uuid
import traceback
import resource
import signal
from celery import shared_task
from django.core.cache import cache
from django.conf import settings
from .models import CodeExecution

# Define timeout handler
class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Code execution timed out")

class CacheStdout:
    """
    A file‐like stdout replacement that writes complete lines
    into Redis under key code_output_<session_id>.
    """
    def __init__(self, session_id):
        self.session_id = session_id
        self._buffer = ""

        # Clear any old output
        cache.set(f"code_output_{self.session_id}", "", timeout=3600)

    def write(self, s):
        self._buffer += s
        if "\n" in self._buffer:
            parts = self._buffer.split("\n")
            # all complete lines
            for line in parts[:-1]:
                # append line + newline
                prev = cache.get(f"code_output_{self.session_id}") or ""
                cache.set(f"code_output_{self.session_id}", prev + line + "\n", timeout=3600)
            # keep the remainder
            self._buffer = parts[-1]

    def flush(self):
        # on flush, push any remaining text
        if self._buffer:
            prev = cache.get(f"code_output_{self.session_id}") or ""
            cache.set(f"code_output_{self.session_id}", prev + self._buffer, timeout=3600)
            self._buffer = ""

@shared_task
def execute_code_task(code_execution_id):
    try:
        code_instance = CodeExecution.objects.get(id=code_execution_id)
        code = code_instance.code
        session_id = str(code_instance.session_id)

        def custom_input(prompt=""):
            cache.set(f"code_prompt_{session_id}", prompt, timeout=300)
            user_input = None
            for _ in range(300):
                user_input = cache.get(f"code_input_{session_id}")
                if user_input is not None:
                    cache.delete(f"code_input_{session_id}")
                    break
                time.sleep(1)
            return user_input if user_input is not None else ""

        # resource limits
        max_mem = getattr(settings, 'CODE_EXECUTION_MAX_MEMORY', 100) * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (max_mem, max_mem))
        max_time = getattr(settings, 'CODE_EXECUTION_MAX_TIME', 5)
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(max_time)

        # replace stdout with our streaming writer
        old_stdout = sys.stdout
        sys.stdout = CacheStdout(session_id)

        local_vars = {}
        global_vars = {
            '__builtins__': __builtins__,
            'input': custom_input,
        }

        try:
            exec(code, global_vars, local_vars)
        except TimeoutException:
            sys.stdout.write("Error: Code execution timed out. Your code took too long to run.\n")
        except MemoryError:
            sys.stdout.write("Error: Memory limit exceeded. Your code used too much memory.\n")
        finally:
            # cleanup
            signal.alarm(0)
            sys.stdout.flush()
            sys.stdout = old_stdout

        # fetch everything we streamed
        full_output = cache.get(f"code_output_{session_id}") or ""
        code_instance.output = full_output
        code_instance.status = 'completed'
        code_instance.save()

    except Exception:
        traceback_str = traceback.format_exc()
        # ensure we capture errors
        cache.set(f"code_output_{code_instance.session_id}", traceback_str, timeout=3600)
        code_instance.output = traceback_str
        code_instance.status = 'failed'
        code_instance.save()
