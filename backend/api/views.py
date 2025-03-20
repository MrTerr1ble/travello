from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from trail.models import Routers, PointsOfInterest, Reviews, Collections
from api.serializers import CustomUserSerializer, RoutersSerializer, PointsOfInterestSerializer, ReviewsSerializer, CollectionsSerializer

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer


class RoutersViewSet(viewsets.ModelViewSet):
    queryset = Routers.objects.all()
    serializer_class = RoutersSerializer


class PointsOfInterestViewSet(viewsets.ModelViewSet):
    queryset = PointsOfInterest.objects.all()
    serializer_class = PointsOfInterestSerializer


class ReviewsViewSet(viewsets.ModelViewSet):
    queryset = Reviews.objects.all()
    serializer_class = ReviewsSerializer


class CollectionsViewSet(viewsets.ModelViewSet):
    queryset = Collections.objects.all()
    serializer_class = CollectionsSerializer
