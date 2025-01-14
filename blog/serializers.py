from django.contrib.auth import authenticate
from rest_framework import serializers, status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import BlogPost, UserProfile, Comment, User



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create(
            username = validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        # Bu yo'li ham bor:

        # user = User.objects.create_user(email=validated_data['email'], username=validated_data['username'], password=validated_data['password'])

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
    username_field = 'email'

    def validate(self, attrs):
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            'password': attrs['password'],
        }
        try:
            authenticate_kwargs['request'] = self.context['request']
        except KeyError:
            raise serializers.ValidationError("Email not found")

        user = authenticate(**authenticate_kwargs)

        if user is None or not user.is_active:
            raise serializers.ValidationError(
                'No active account found with the given credentials'
            )

        data = super().validate(attrs)
        return data