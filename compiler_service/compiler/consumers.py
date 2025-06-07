import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache

class CompilerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.session_id = None
        self._stream_task = None
        self._last_sent = 0

    async def disconnect(self, close_code):
        # cancel streaming loop if running
        if self._stream_task:
            self._stream_task.cancel()

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        if action == "set_session":
            # bind this WS to a session ID, then start streaming
            self.session_id = data.get("session_id")
            self._last_sent = 0
            # clear any old prompt
            cache.delete(f"code_prompt_{self.session_id}")
            # start background streamer
            self._stream_task = asyncio.create_task(self._stream_output())
        elif action == "user_input":
            if not self.session_id:
                await self.send(json.dumps({"error": "Session not set"}))
                return
            user_input = data.get("input", "")
            cache.set(f"code_input_{self.session_id}", user_input, timeout=300)
        elif action == "get_prompt":
            if not self.session_id:
                await self.send(json.dumps({"error": "Session not set"}))
                return
            prompt = cache.get(f"code_prompt_{self.session_id}") or ""
            await self.send(json.dumps({"prompt": prompt}))
        else:
            await self.send(json.dumps({"error": f"Unknown action '{action}'"}))

    async def _stream_output(self):
        """
        Periodically check the Redis cache for new output
        and send any new chunk to the client.
        """
        try:
            while True:
                await asyncio.sleep(0.5)
                full = cache.get(f"code_output_{self.session_id}") or ""
                if len(full) > self._last_sent:
                    new_chunk = full[self._last_sent:]
                    await self.send(json.dumps({"output": new_chunk}))
                    self._last_sent = len(full)
                # optional: you could break when you detect completion
                # by checking a cache flag or the CodeExecution.status
        except asyncio.CancelledError:
            # normal on disconnect()
            pass
