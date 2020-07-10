from django.urls import re_path, path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/mainapp/$', consumers.TableConsumer),
    path('ws/room/<str:room_id>/', consumers.TableConsumer),
    path('ws/rooms/', consumers.RoomListConsumer),
]
