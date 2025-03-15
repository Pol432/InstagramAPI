from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PostViewSet,
    StoryViewSet,
    UserRegister, 
    UserLogin, 
    UserLogout,
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'stories', StoryViewSet, basename='story')

# Define URL patterns
urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Authentication URLs
    path('register', UserRegister.as_view(), name='user-register'),
    path('login', UserLogin.as_view(), name='user-login'),
    path('logout', UserLogout.as_view(), name='user-logout'),
    
    # Add other URL patterns as needed
    # path('stories/', StoryList.as_view(), name='story-list'),
]
