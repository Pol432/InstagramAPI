from django.contrib import admin

from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin
from .models import *

# Register of models for the Admin panel
class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ['created_at', 'user']

class LikesInline(admin.TabularInline):
    model = Likes
    extra = 0
    readonly_fields = ['user']

class SeenPostInline(admin.TabularInline):
    model = SeenPost
    extra = 0
    readonly_fields = ['user']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'description_preview', 'post_image', 'likes_count', 'comments_count']
    list_filter = ['created_at', 'user']
    search_fields = ['description', 'user__username']
    readonly_fields = ['created_at', 'post_image', 'likes_count', 'comments_count']
    inlines = [CommentInline, LikesInline, SeenPostInline]
    date_hierarchy = 'created_at'
    
    def description_preview(self, obj):
        """Return a truncated description"""
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_preview.short_description = 'Description'
    
    def post_image(self, obj):
        """Display thumbnail of the post image"""
        if obj.image:
            return format_html('<img src="{}" width="100" height="auto" />', obj.image.url)
        return "No Image"
    post_image.short_description = 'Image'
    
    def likes_count(self, obj):
        """Count the likes on a post"""
        return obj.likes.count()
    likes_count.short_description = 'Likes'
    
    def comments_count(self, obj):
        """Count the comments on a post"""
        return obj.comments.count()
    comments_count.short_description = 'Comments'


class FollowerConnectionInline(admin.TabularInline):
    model = FollowerConnection
    fk_name = 'following'
    verbose_name = 'Follower'
    verbose_name_plural = 'Followers'
    extra = 0

class FollowingConnectionInline(admin.TabularInline):
    model = FollowerConnection
    fk_name = 'follower'
    verbose_name = 'Following'
    verbose_name_plural = 'Following'
    extra = 0


class AccountAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'profile_picture_preview', 'followers_count', 'posts_count']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = ['profile_picture_preview', 'date_joined', 'last_login', 'followers_count', 'posts_count']
    fieldsets = UserAdmin.fieldsets + (
        ('Profile Info', {'fields': ('profile_picture', 'profile_picture_preview', 'description')}),
        ('Stats', {'fields': ('followers_count', 'posts_count')}),
    )
    inlines = [FollowerConnectionInline, FollowingConnectionInline]
    
    def profile_picture_preview(self, obj):
        """Display thumbnail of profile picture"""
        if obj.profile_picture:
            return format_html('<img src="{}" width="50" height="auto" />', obj.profile_picture.url)
        return "No Image"
    profile_picture_preview.short_description = 'Profile Picture'
    
    def followers_count(self, obj):
        """Count followers"""
        return obj.followers.count()
    followers_count.short_description = 'Followers'
    
    def posts_count(self, obj):
        """Count posts"""
        return obj.posts.count()
    posts_count.short_description = 'Posts'

admin.site.register(Account, AccountAdmin)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'post', 'text_preview', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['text', 'user__username']
    readonly_fields = ['created_at']
    
    def text_preview(self, obj):
        """Return a truncated text"""
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Text'


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'story_image']
    list_filter = ['created_at', 'user']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'story_image']
    
    def story_image(self, obj):
        """Display thumbnail of the story image"""
        if obj.image:
            return format_html('<img src="{}" width="100" height="auto" />', obj.image.url)
        return "No Image"
    story_image.short_description = 'Image'


@admin.register(Likes)
class LikesAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'post']
    list_filter = ['user']
    search_fields = ['user__username', 'post__description']


@admin.register(SeenPost)
class SeenPostAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'post']
    list_filter = ['user']
    search_fields = ['user__username', 'post__description']


@admin.register(FollowerConnection)
class FollowerConnectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'follower', 'following']
    list_filter = ['follower', 'following']
    search_fields = ['follower__username', 'following__username']
