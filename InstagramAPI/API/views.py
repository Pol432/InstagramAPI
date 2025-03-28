from django.contrib.auth import login, logout
from django.core.exceptions import ValidationError

from rest_framework.views import APIView
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .serializers import *
from .models import *
from .helpers import *

# Views of the App
class StoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing stories
    """
    serializer_class = StorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return stories that are less than 24 hours old.
        For list actions, return stories from users the current user follows
        plus their own stories.
        """
        # Only show stories less than 24 hours old
        # twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
        # queryset = Story.objects.filter(created_at__gt=twenty_four_hours_ago)
        queryset = Story.objects.all()

        if self.action == 'list':
            # For the main list, show stories from followed users and own stories
            following_users = self.request.user.following.values_list('following', flat=True)
            return queryset.filter(
                models.Q(user__in=following_users) | models.Q(user=self.request.user)
            ).order_by('-created_at')
        
        return queryset
    
    def perform_create(self, serializer):
        """
        Assign the current user when creating a story
        """
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_stories(self, request):
        """
        Return all of the current user's active stories
        """
        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
        stories = Story.objects.filter(
            user=request.user,
            created_at__gt=twenty_four_hours_ago
        ).order_by('-created_at')
        
        serializer = self.get_serializer(stories, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def user_stories(self, request):
        """
        Return all stories for a specific user (if provided in query params)
        """
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {"error": "user_id query parameter is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
        stories = Story.objects.filter(
            user_id=user_id,
            created_at__gt=twenty_four_hours_ago
        ).order_by('-created_at')
        
        serializer = self.get_serializer(stories, many=True)
        return Response(serializer.data)


class PostViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows posts to be viewed or edited.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        like, created = Likes.objects.get_or_create(user=request.user, post=post)
        if not created:
            like.delete()
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def comment(self, request, pk=None):
        post = self.get_object()
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def seen(self, request, pk=None):
        post = self.get_object()
        seen, created = SeenPost.objects.get_or_create(user=request.user, post=post)
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def feed(self, request):
        posts = Post.objects.filter(user__followers__follower=request.user)
        return self._paginated_response(posts)

    @action(detail=False, methods=['get'])
    def my_posts(self, request):
        posts = Post.objects.filter(user=request.user)
        return self._paginated_response(posts)

    @action(detail=False, methods=['get'])
    def my_feed(self, request):
        following_users = request.user.following.values_list('following', flat=True)
        posts = Post.objects.filter(user__in=following_users)
        return self._paginated_response(posts)

    @action(detail=False, methods=['get'])
    def my_comments(self, request):
        comments = Comment.objects.filter(user=request.user)
        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = CommentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_likes(self, request):
        liked_posts = Post.objects.filter(likes__user=request.user)
        return self._paginated_response(liked_posts)
        
    def _paginated_response(self, queryset):
        """Helper method to handle pagination for post responses"""
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
        
    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'retrieve':
            return PostDetailSerializer
        return super().get_serializer_class()


class UserRegister(APIView):
    """
    API endpoint for user registration
    """
    permission_classes = [permissions.AllowAny,]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.create(serializer.validated_data)
            return Response({
                'message': 'User registered successfully',
                'user_id': user.id,
                'username': user.username
            }, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({
                'error': 'Registration failed',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class UserLogin(APIView):
    """
    API endpoint for user login
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = [SessionAuthentication]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.check_user(serializer.validated_data)
            login(request, user)
            return Response({
                'message': 'Login successful',
                'user_id': user.id,
                'username': user.username,
            }, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({
                'error': 'Login failed',
                'details': str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)


class UserLogout(APIView):
    """
    API endpoint for user logout
    """
    permission_classes = [permissions.AllowAny,]

    def post(self, request):
        logout(request)
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
