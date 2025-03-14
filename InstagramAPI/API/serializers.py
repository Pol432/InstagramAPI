from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .models import *

# Serializers of the App
Account = get_user_model()


class AccountSerializer(serializers.ModelSerializer):
    """Serializer for the user account model"""
    
    class Meta:
        model = Account
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile_picture', 'description']
        read_only_fields = ['id']


class FollowerConnectionSerializer(serializers.ModelSerializer):
    """Serializer for follower connections"""
    
    class Meta:
        model = FollowerConnection
        fields = ['id', 'follower', 'following']
        read_only_fields = ['id']


class UserBriefSerializer(serializers.ModelSerializer):
    """Minimal serializer for user information in nested contexts"""
    
    class Meta:
        model = Account
        fields = ['id', 'username', 'profile_picture']


class PostSerializer(serializers.ModelSerializer):
    """Serializer for posts"""
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    seen_count = serializers.SerializerMethodField()
    user = UserBriefSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 
            'created_at', 
            'image', 
            'description', 
            'user',
            'likes_count', 
            'comments_count', 
            'seen_count',
            'is_liked'
        ]
        read_only_fields = ['id', 'created_at', 'user', 'likes_count', 'comments_count', 'seen_count', 'is_liked']
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_comments_count(self, obj):
        return obj.comments.count()
    
    def get_seen_count(self, obj):
        return obj.seen_by.count()
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False


class PostDetailSerializer(PostSerializer):
    """Detailed serializer for posts with comments and likes"""
    comments = serializers.SerializerMethodField()
    
    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ['comments']
    
    def get_comments(self, obj):
        from .serializers import CommentSerializer  # Import here to avoid circular import
        comments = obj.comments.all().order_by('-created_at')
        return CommentSerializer(comments, many=True, context=self.context).data


class PostDetailSerializer(PostSerializer):
    """Detailed serializer for posts with comments and likes"""
    comments = serializers.SerializerMethodField()
    
    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ['comments']
    
    def get_comments(self, obj):
        comments = obj.comments.all().order_by('-created_at')
        return CommentSerializer(comments, many=True).data


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments"""
    user = serializers.StringRelatedField()
    
    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'text', 'user', 'post']
        read_only_fields = ['id', 'created_at', 'user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class LikesSerializer(serializers.ModelSerializer):
    """Serializer for likes"""
    
    class Meta:
        model = Likes
        fields = ['id', 'user', 'post']
        read_only_fields = ['id', 'user']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class StorySerializer(serializers.ModelSerializer):
    """Serializer for stories"""
    user = AccountSerializer(read_only=True)
    
    class Meta:
        model = Story
        fields = ['id', 'created_at', 'image', 'user']
        read_only_fields = ['id', 'created_at', 'user']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class SeenPostSerializer(serializers.ModelSerializer):
    """Serializer for seen posts"""
    
    class Meta:
        model = SeenPost
        fields = ['id', 'user', 'post']
        read_only_fields = ['id', 'user']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AccountDetailSerializer(AccountSerializer):
    """Detailed serializer for user accounts with additional information"""
    posts_count = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    
    class Meta(AccountSerializer.Meta):
        fields = AccountSerializer.Meta.fields + ['posts_count', 'followers_count', 'following_count']
    
    def get_posts_count(self, obj):
        return Post.objects.filter(user=obj).count()
    
    def get_followers_count(self, obj):
        return obj.followers.count()
    
    def get_following_count(self, obj):
        return obj.following.count()

class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    class Meta:
        model = Account
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
        extra_kwargs = {'email': {'required': True}}
    
    def validate(self, data):
        """Validate that passwords match"""
        if data['password'] != data['password_confirm']:
            raise ValidationError(_("Passwords don't match."))
        return data
        
    def validate_email(self, value):
        """Validate email is unique"""
        if Account.objects.filter(email=value).exists():
            raise ValidationError(_("A user with this email already exists."))
        return value
    
    def validate_username(self, value):
        """Validate username is unique"""
        if Account.objects.filter(username=value).exists():
            raise ValidationError(_("A user with this username already exists."))
        return value
    
    def create(self, validated_data):
        """Create a new user with encrypted password"""
        # Remove password_confirm as it's not needed for creating the user
        validated_data.pop('password_confirm')
        
        # Create the user with create_user to properly handle password hashing
        user = Account.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    
    def validate(self, data):
        """Validate user credentials"""
        username = data.get('username', '')
        password = data.get('password', '')
        
        if not username or not password:
            raise ValidationError(_("Must provide both username and password."))
        
        return data
    
    def check_user(self, validated_data):
        """Authenticate user with provided credentials"""
        username = validated_data.get('username')
        password = validated_data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if not user:
            raise ValidationError(_("Invalid credentials. Please try again."))
        
        if not user.is_active:
            raise ValidationError(_("This user has been deactivated."))
            
        return user
