# asgi.py
import os
import django
from channels.routing import get_default_application

# Set Django settings module first
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "user_api.settings")

# Configure Django BEFORE importing any models or DRF
django.setup()

# Now import everything else AFTER django.setup()
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

# Import your routing after Django is configured
import authentication.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            authentication.routing.websocket_urlpatterns
        )
    ),
})