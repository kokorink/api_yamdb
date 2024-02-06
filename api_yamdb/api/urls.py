from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views

router_v1 = SimpleRouter()

router_v1.register('users', views.UsersViewSet, basename='users')
router_v1.register('categories', views.CategoryViewSet, basename='categories')
router_v1.register('titles', views.TitleViewSet, basename='titles')
router_v1.register('genres', views.GenreViewSet, basename='genres')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    views.ReviewViewSet,
    basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    views.CommentViewSet,
    basename='comments'
)

auth_patterns_v1 = [
    path('signup/', views.SignUpView.as_view()),
    path('token/', views.TokenView.as_view())
]

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/', include(auth_patterns_v1)),
]
