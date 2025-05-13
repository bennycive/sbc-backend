# users_api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import CustomUserViewSet, ProfileViewSet


router = DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'profiles', ProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
   
]





