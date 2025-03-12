from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _

# Models of the App
class Comment(models.Model):
    """
    Comment details model
    """
    created_at = models.DateTimeField(
        _("Created at"),
        auto_now_add=True,
    )
    text = models.CharField(
        _("Text"),
        max_length=255,
    )
    user = models.ForeignKey(
        "Account",
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        related_name="comments",
    )
    post = models.ForeignKey(
        "Post",
        verbose_name=_("Post"),
        on_delete=models.CASCADE,
        related_name="comments",
    )

class Post(models.Model):
    """
    Post details model
    """
    created_at = models.DateTimeField(
        _("Created at"),
        auto_now_add=True,
    )
    image = models.ImageField(
        _("Image"),
        upload_to="posts/",
        validators=[FileExtensionValidator(["png", "jpg", "jpeg"])],
    )

    likes = models.PositiveIntegerField(
        _("Likes"),
        default=0,
    )
    description = models.TextField(
        _("Description"),
    )


class FollowerConnection(models.Model):
    """
    Follower connection model
    """
    follower = models.ForeignKey(
        "Account",
        verbose_name=_("Follower"),
        on_delete=models.CASCADE,
        related_name="following",
    )
    following = models.ForeignKey(
        "Account",
        verbose_name=_("Following"),
        on_delete=models.CASCADE,
        related_name="followers",
    )


class Account(AbstractUser):
    """
    User account model
    """  
    profile_picture = models.ImageField(
        _("Profile picture"),
        upload_to="profile_pictures/",
        validators=[FileExtensionValidator(["png", "jpg", "jpeg"])],
        blank=True,
    )
    description = models.TextField(
        _("Description"),
        blank=True,
    )

