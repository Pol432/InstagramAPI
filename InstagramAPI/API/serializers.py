from rest_framework import serializers
from .models import Comment, Post, FollowerConnection, Account

# Serializers of the App
class AccountSerializer(serializers.ModelSerializer):
    """
    Serializer for the Account model
    """
    class Meta:
        model = Account
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'profile_picture', 'description', 'date_joined']
        read_only_fields = ['date_joined']


class AccountDetailSerializer(AccountSerializer):
    """
    Detailed serializer for the Account model with follower counts
    """
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    
    class Meta(AccountSerializer.Meta):
        fields = AccountSerializer.Meta.fields + ['followers_count', 'following_count']
    
    def get_followers_count(self, obj):
        return obj.followers.count()
    
    def get_following_count(self, obj):
        return obj.following.count()


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for the Post model
    """
    class Meta:
        model = Post
        fields = ['id', 'created_at', 'image', 'likes', 'description']
        read_only_fields = ['created_at', 'likes']


class PostDetailSerializer(PostSerializer):
    """
    Detailed serializer for the Post model with comments
    """
    comments = serializers.SerializerMethodField()
    
    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ['comments']
    
    def get_comments(self, obj):
        comments = obj.comments.all().order_by('-created_at')
        return CommentSerializer(comments, many=True).data


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Comment model
    """
    user = AccountSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'text', 'user', 'post']
        read_only_fields = ['created_at', 'user']
    
    def create(self, validated_data):
        # Set the user from the request context
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class FollowerConnectionSerializer(serializers.ModelSerializer):
    """
    Serializer for the FollowerConnection model
    """
    follower = AccountSerializer(read_only=True)
    following = AccountSerializer(read_only=True)
    
    class Meta:
        model = FollowerConnection
        fields = ['id', 'follower', 'following']
    
    def create(self, validated_data):
        # Set the follower from the request context
        validated_data['follower'] = self.context['request'].user
        return super().create(validated_data)


class FollowerListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing followers of an account
    """
    follower = AccountSerializer(read_only=True)
    
    class Meta:
        model = FollowerConnection
        fields = ['id', 'follower']


class FollowingListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing accounts followed by an account
    """
    following = AccountSerializer(read_only=True)
    
    class Meta:
        model = FollowerConnection
        fields = ['id', 'following']
