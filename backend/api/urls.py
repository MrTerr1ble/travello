from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (CustomUserViewSet, RoutersViewSet, ReviewsViewSet, PointsOfInterestViewSet, CollectionsViewSet)

app_name = 'api'

router = DefaultRouter()
router.register(
    r'users', CustomUserViewSet, basename='users'
)

router.register(
    r'routers', RoutersViewSet, basename='routers'
)
router.register(
    r'points', PointsOfInterestViewSet, basename='points'
)
router.register(
    r'collections', CollectionsViewSet, basename='collections'
)
router.register(
    r'reviews', ReviewsViewSet, basename='reviews'
)


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
