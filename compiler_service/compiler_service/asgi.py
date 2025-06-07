import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from django.urls import path
from compiler.consumers import CompilerConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'compiler_service.settings')
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/compiler/", CompilerConsumer.as_asgi()),
        ])
    ),
})
