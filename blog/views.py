from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, BasePermission, IsAdminUser
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from . import serializers

# Generics dan foydanlib qilmoqchi bo'ganim:

class AuthorValidateAPIView(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user

class BaseUserAPIView(APIView):
    queryset = serializers.UserProfile.objects.all()
    serializer_class = serializers.UserProfileSerializer

class BaseBlogAPIView(APIView):
    queryset = serializers.BlogPost.objects.all()
    serializer_class = serializers.BlogPostSerializer

class BaseCommentAPIView(APIView):
    queryset = serializers.Comment.objects.all()
    serializer_class = serializers.CommentSerializer


class UserCreateAPIView(CreateAPIView):
    """
    User yaratish uchun APIView.
    """
    queryset = serializers.User.objects.all()
    serializer_class = serializers.UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response({
            "message": "Foydalanuvchi muvaffaqiyatli ro'yxatdan o'tdi",
            "user_id": user.id
        }, status=status.HTTP_201_CREATED, headers=headers)

class UserListAPIView(BaseUserAPIView, ListAPIView):
    """
    User ro'yxatini olish uchun APIView.
    """

class UserRetrieveAPIView(BaseUserAPIView, RetrieveAPIView):
    """
    User ni detalni ko'rish uchun uchun APIView.
    """

class UserUpdateAPIView(BaseUserAPIView, UpdateAPIView):
    """
    User ni yangilash uchun APIView.
    """
    permission_classes = [AuthorValidateAPIView or IsAdminUser]


class UserDestroyAPIView(DestroyAPIView):
    """
    User ni o'chirish uchun APIView.
    """
    queryset = serializers.User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [AuthorValidateAPIView or IsAdminUser]

class BlogPostCreateAPIView(CreateAPIView, BaseBlogAPIView):
    """
    Post ni yaratish uchun APIView.
    """
    permission_classes = [IsAuthenticated or IsAdminUser]

class BlogPostListAPIView(ListAPIView, BaseBlogAPIView):
    """
    Postlarni ro'yxatini ko'rish uchun APIView.
    """

class BlogPostRetrieveAPIView(RetrieveAPIView, BaseBlogAPIView):
    """
    Post ni ko'rish uchun APIView.
    """

class BlogPostUpdateAPIView(UpdateAPIView, BaseBlogAPIView):
    """
    Post ni yangilash uchun APIView.
    """
    permission_classes = [AuthorValidateAPIView or IsAdminUser]

class BlogPostDestroyAPIView(DestroyAPIView, BaseBlogAPIView):
    """
    Post ni o'chirish uchun APIView.
    """
    permission_classes = [AuthorValidateAPIView or IsAdminUser]

class CommentCreateAPIView(CreateAPIView, BaseCommentAPIView):
    """
    Comment ni yaratish uchun APIView.
    """
    permission_classes = [IsAuthenticated or IsAdminUser]

class CommentListAPIView(ListAPIView, BaseCommentAPIView):
    """
    Comment larni ro'yxatini olish uchun APIView.
    """

class CommentUpdateAPIView(UpdateAPIView, BaseCommentAPIView):
    """
    Comment ni yangilsh uchun APIView.
    """
    permission_classes = [AuthorValidateAPIView or IsAdminUser]

class CommentDestroyAPIView(DestroyAPIView, BaseCommentAPIView):
    """
    Comment ni o'chirish uchun APIView.
    """
    permission_classes = [AuthorValidateAPIView or IsAdminUser]


# class UserAPIViewSet(viewsets.ModelViewSet):
#     queryset = get_user_model().objects.all()
#     serializer_class = serializers.UserSerializer
#     authentication_classes = [JWTAuthentication]
#
#     def get_object(self):
#         obj = super().get_object()
#         print("Current user:", self.request.user)  # Debug uchun
#         print("Auth:", self.request.auth)  # Debug uchun
#         return obj
#
#     def perform_update(self, serializer):
#         user = self.get_object()
#         print("Request user:", self.request.user)  # Debug uchun
#         print("Target user:", user)  # Debug uchun
#
#         if user != self.request.user and not self.request.user.is_staff:
#             raise PermissionDenied("You can only edit your own data.")
#         serializer.save()
#
#     def perform_destroy(self, instance):
#         user = self.get_object()
#         if user != self.request.user and not self.request.user.is_staff:
#             raise PermissionDenied("You can only delete your own account.")
#         instance.delete()
#
# class PostAPIViewSet(viewsets.ModelViewSet):
#     queryset = serializers.BlogPost.objects.all()
#     serializer_class = serializers.BlogPostSerializer
#
#     def perform_update(self, serializer):
#         post = self.get_object()
#         if post.author != self.request.user and not self.request.user.is_staff:
#             raise PermissionDenied("You can only edit your posts.")
#         serializer.save()
#
#     def perform_destroy(self, instance):
#         post = self.get_object()
#         if post.author != self.request.user and not self.request.user.is_staff:
#             raise PermissionDenied("You can only edit your posts.")
#         instance.delete()
#
# class CommentAPIViewSet(viewsets.ModelViewSet):
#     queryset = serializers.Comment.objects.all()
#     serializer_class = serializers.CommentSerializer
#
#     def perform_update(self, serializer):
#         comment = self.get_object()
#         if comment.user != self.request.user and not self.request.user.is_staff:
#             raise PermissionDenied("You can only edit your comments.")
#         serializer.save()
#
#     def perform_destroy(self, instance):
#         comment = self.get_object()
#         if comment.user != self.request.user and not self.request.user.is_staff:
#             raise PermissionDenied("You can only edit your comments.")
#         instance.delete()

class SearchPostAPIViewSet(APIView):
    queryset = serializers.BlogPost.objects.all()

    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('q', None)

        if search_query is None:
            posts = self.queryset
        else:
            posts = self.queryset.filter(
                title__icontains=search_query
            ) | self.queryset.filter(
                content__icontains=search_query
            )

        serializer = serializers.BlogPostSerializer(posts, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Successfully logged out."})
        except KeyError:
            return Response({"detail": "Refresh token required."})

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = serializers.CustomTokenObtainPairSerializer
