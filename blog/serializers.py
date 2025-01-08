from rest_framework import serializers, status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import BlogPost, UserProfile, Comment, User



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create(
            username = validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()

        UserProfile.objects.create(
            user=user
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    profile_image = serializers.ImageField(required=False, allow_null=True)
    following = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False)
    followers = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False)

    class Meta:
        model = UserProfile
        fields = ('id', 'profile_image', 'following', 'followers', 'user')

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user_instance = instance.user
            for attr, value in user_data.items():
                setattr(user_instance, attr, value)
                user_instance.set_password(value)
            user_instance.save()
        following_data = validated_data.get('following', None)
        if following_data is not None:
            instance.following.remove(*following_data['unfollowed'])
            instance.following.add(*following_data['followed'])

        return instance

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     representation['user'] = UserSerializer(instance.user).data
    #     return representation

    # def to_internal_value(self, data):
    #     internal_value = super().to_internal_value(data)
    #     if 'user' in data:
    #         try:
    #             user = User.objects.get(id=data['user'])
    #             internal_value['user'] = user
    #         except User.DoesNotExist:
    #             raise serializers.ValidationError({'user': 'Invalid user ID.'})
    #     return internal_value

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
        email = attrs.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('Email not found')

        self.user = user
        data = super().validate(attrs)
        data['user_id'] = user.id
        if user.is_superuser:
            data['role'] = 'admin'
        else:
            data['role'] = 'user'
        return data