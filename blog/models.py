from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.hashers import make_password, check_password
from .managers import CustomUserManager


class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150,  blank=True, null=True)
    password = models.CharField(max_length=128)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)


    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def set_password(self, raw_password):
        """ Hash the password before saving """
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """ Check the password hash """
        return check_password(raw_password, self.password)

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
