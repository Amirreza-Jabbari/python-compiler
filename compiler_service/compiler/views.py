from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import CodeExecution
from .serializers import CodeExecutionSerializer
from .tasks import execute_code_task
from .throttling import CodeExecutionRateThrottle

class CodeExecutionView(generics.CreateAPIView):
    serializer_class = CodeExecutionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [CodeExecutionRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            code_instance = serializer.save(status='pending')
            # Trigger asynchronous execution task
            execute_code_task.delay(code_instance.id)
            return Response({
                "message": "Code execution started",
                "id": code_instance.id,
                "session_id": code_instance.session_id,
            }, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
