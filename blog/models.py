from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    following = models.ManyToManyField('self',
        symmetrical=False,
        related_name='followers',
        blank=True)
    profile_image = models.ImageField(upload_to='User_image/', blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    image = models.ImageField(upload_to='Post_images/', null=True)

class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
