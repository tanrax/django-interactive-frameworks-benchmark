import os

import django
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Import handlers to ensure they are registered (must be after django.setup())
import alerts.liveview_components.alerts  # noqa: E402, F401
from liveview.consumers import LiveViewConsumer  # noqa: E402

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path('ws/liveview/<str:room_name>/', LiveViewConsumer.as_asgi()),
        ])
    ),
})
