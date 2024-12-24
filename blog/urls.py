from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter

# router = DefaultRouter()
# router.register(r"auth/register", views.UserAPIViewSet)
# router.register(r"posts", views.PostAPIViewSet)
# router.register(r"comments", views.CommentAPIViewSet)

urlpatterns = [
    path('auth/login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', views.LogoutAPIView.as_view(), name='logout'),
    path('auth/register/', views.UserCreateAPIView.as_view(), name='user_create'),
    path('auth/user/list/', views.UserListAPIView.as_view(), name='user_create'),
    path('auth/post/list/', views.BlogPostCreateAPIView.as_view(), name='post_create'),
    path('auth/user/detail/<int:pk>', views.UserRetrieveAPIView.as_view(), name='user_detail'),
    path('auth/user/update/<int:pk>', views.UserUpdateAPIView.as_view(), name='user_update'),
    path('auth/user/delete/<int:pk>', views.UserDestroyAPIView.as_view(), name='user_delete'),
    path('auth/post/detail/<int:pk>', views.BlogPostRetrieveAPIView.as_view(), name='post_detail'),
    path('auth/post/update/<int:pk>', views.BlogPostUpdateAPIView.as_view(), name='post_update'),
    path('auth/post/delete/<int:pk>', views.BlogPostDestroyAPIView.as_view(), name='post_delete'),
    # path('', include(router.urls))
]
