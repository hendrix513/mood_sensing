from django.urls import path

from . import views

urlpatterns = [
    path('capture_mood', views.capture_mood, name='capture-mood'),
    path('mood_frequency_distribution', views.mood_frequency_distribution, name='mood-frequency-distribution'),
    path('closest_happy_location', views.closest_happy_location, name='closest-happy-location'),
]