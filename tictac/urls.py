from django.contrib import admin
from django.urls import path

import mainapp.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', mainapp.views.listing),
    path('login/', mainapp.views.login),
    path('ajax/', mainapp.views.ajax),
    path('tool/', mainapp.views.tool)
]
