"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

django_asgi_app = get_asgi_application()

from api.middleware import TokenAuthMiddleware
from api.consumer import LobbyConsumer

application = ProtocolTypeRouter({
	"http": django_asgi_app,
	"websocket": TokenAuthMiddleware(
		URLRouter([
			path("ws/", LobbyConsumer.as_asgi()),
		])
	),
})
