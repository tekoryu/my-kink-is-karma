from django.contrib import admin
from django.urls import path, include
from .views import health_check

urlpatterns = [
    # ... other app urls
    path('health/', health_check, name='health_check'), # Add the health check URL
]