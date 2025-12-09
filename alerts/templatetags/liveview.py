"""
Django LiveView template tags.
"""
import uuid
from django import template

register = template.Library()


@register.simple_tag
def liveview_room_uuid():
    """
    Generate a random UUID for WebSocket room identifier.

    Usage:
        {% load liveview %}
        <html data-room="{% liveview_room_uuid %}">
    """
    return str(uuid.uuid4())
