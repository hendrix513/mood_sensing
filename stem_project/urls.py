from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('mood_capture/', include('mood_capture.urls')),
    path('admin/', admin.site.urls),
]