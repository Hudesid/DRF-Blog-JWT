from rest_framework import serializers, status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import BlogPost, UserProfile, Comment, User
from rest_framework.response import Response



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()

        user_profile = UserProfile.objects.create(
            user=user,
            profile_image=validated_data.get('profile_image', None),
        )
        following_users = validated_data.get('following', [])
        if following_users:
            user_profile.following.set(following_users)
        return user_profile, Response({
            "message": "Foydalanuvchi muvaffaqiyatli ro'yxatdan o'tdi",
            "user_id": user.id
        }, status=status.HTTP_201_CREATED)


class BlogPostSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = ('id', 'title', 'author', 'content', 'image', 'created_at', 'updated_at', 'is_published', 'count')

    def get_count(self, obj):
        return len(obj.title)

    def create(self, validated_data):
        user = self.context['request'].user
        posts = BlogPost.objects.create(
            author = user,
            **validated_data
        )
        posts.save()
        return posts

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = UserSerializer(instance.author).data
        return representation


class CommentSerializer(serializers.ModelSerializer):
    post = BlogPostSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'user', 'post', 'created_at', 'updated_at', 'comment')

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data['user_id'] = user.id
        if user.is_superuser:
            data['role'] = 'admin'
        else:
            data['role'] = 'user'
        return data