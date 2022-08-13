from django.urls import include, path
from rest_framework.authtoken import views as token_views
from rest_framework.routers import DefaultRouter
from .views import (
    CommentViewSet,
    FollowViewSet,
    GroupViewSet,
    PostViewSet,
    UserViewSet,
)


v1_router = DefaultRouter()
v1_router.register(r'posts/(?P<post_id>\d+)/comments', CommentViewSet)
v1_router.register(r'groups', GroupViewSet)
v1_router.register(r'follow', FollowViewSet, basename='follow')
v1_router.register(r'posts', PostViewSet)
v1_router.register(r'users', UserViewSet)

urlpatterns = [
    path('v1/api-token-auth/', token_views.obtain_auth_token),
    path('v1/', include(v1_router.urls)),
    path('v1/', include('djoser.urls')),
    path('v1/', include('djoser.urls.jwt')),
]
