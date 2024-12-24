from rest_framework import serializers, status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import BlogPost, UserProfile, Comment, User
from rest_framework.response import Response



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

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
        unfollowing_user = validated_data.get('unfollowing', [])

        if following_users:
            user_profile.following.set(following_users)
        if unfollowing_user:
            user_profile.following.remove(unfollowing_user)
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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = UserSerializer(instance.author).data
        return representation

    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)
        if 'author' in data:
            try:
                author = User.objects.get(id=data['author'])
                internal_value['author'] = author
            except User.DoesNotExist:
                raise serializers.ValidationError({'author': 'Invalid author ID.'})
        return internal_value


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'user', 'post', 'created_at', 'updated_at', 'comment')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['post'] = BlogPostSerializer(instance.post).data
        return representation

    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)
        if 'post' in data:
            try:
                post = BlogPost.objects.get(id=data['post'])
                internal_value['post'] = post
            except BlogPost.DoesNotExist:
                raise serializers.ValidationError({'post': 'Invalid post ID.'})
        return internal_value

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