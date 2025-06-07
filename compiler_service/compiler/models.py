import uuid
from django.db import models

class CodeExecution(models.Model):
    code = models.TextField()
    output = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, default='pending')
    session_id = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Execution {self.id} ({self.status})"
