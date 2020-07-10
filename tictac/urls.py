from django.contrib import admin
from django.urls import path, include

from mainapp.views import main_foo, my_api, login_page, room_page, room_list

urlpatterns = [
    # path('chat/', include('chat.urls')),
    path('mainapp/', main_foo),

    path('rooms/', room_list),
    path('room/<int:room_id>', room_page),

    path('login/', login_page),
    path('my_api/', my_api),
    path('admin/', admin.site.urls),
]
