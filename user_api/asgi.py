import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import authentication.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "user_api.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            authentication.routing.websocket_urlpatterns
        )
    ),
})
