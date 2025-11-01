import base64
import re

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import PasswordSerializer, UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.serializers import CurrentUserDefault, HiddenField
from trail.models import Collections, Favorite, PointsOfInterest, Reviews, Routers

User = get_user_model()

from .password_validators import (
    PASSWORD_DIGIT_LETTER_DIGIT_MESSAGE,
    is_digit_letter_digit_password,
)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            img_format, img_str = data.split(";base64,")
            ext = img_format.split("/")[-1]
            data = ContentFile(base64.b64decode(img_str), name=f"image.{ext}")
        return super().to_internal_value(data)


class CustomUserSerializer(UserSerializer):
    avatar = Base64ImageField(allow_null=True, required=False)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "avatar",
        )


class CustomUserCreateSerializer(UserCreateSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
        )

    def validate_password(self, value):
        if not re.fullmatch(r"\d+[A-Za-zА-Яа-яЁё]+\d+", value):
            raise serializers.ValidationError(
                "Пароль должен состоять из цифр, затем букв и снова цифр."
            )
        return super().validate_password(value)

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class CustomPasswordSerializer(PasswordSerializer):
    def validate_new_password(self, value):
        if not is_digit_letter_digit_password(value):
            raise serializers.ValidationError(PASSWORD_DIGIT_LETTER_DIGIT_MESSAGE)
        return super().validate_new_password(value)


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = User
        fields = ("avatar",)


class PointsOfInterestSerializer(serializers.ModelSerializer):
    photo = Base64ImageField(allow_null=True, required=False)

    class Meta:
        model = PointsOfInterest
        fields = (
            "name",
            "description",
            "latitude",
            "longitude",
            "category",
            "photo",
            "created_at",
        )


class RoutersSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    photo = Base64ImageField(allow_null=True, required=False)
    points = serializers.SerializerMethodField()

    class Meta:
        model = Routers
        fields = (
            "name",
            "description",
            "start_date",
            "end_date",
            "is_public",
            "created_at",
            "photo",
            "author",
            "points",
        )

    def get_points(self, obj):
        # Получаем все связанные записи RoutePoints для текущего маршрута
        route_points = obj.router_points.all()
        # Извлекаем связанные точки PointsOfInterest
        points_of_interest = [rp.point for rp in route_points]
        # Сериализуем точки
        return PointsOfInterestSerializer(points_of_interest, many=True).data


class ShortRoutersSerializer(RoutersSerializer):
    class Meta:
        model = Routers
        fields = (
            "name",
            "description",
            "start_date",
            "end_date",
            "is_public",
            "created_at",
            "photo",
        )


class ReviewsSerializer(serializers.ModelSerializer):
    author = HiddenField(default=CurrentUserDefault())
    router = ShortRoutersSerializer(read_only=True)

    class Meta:
        model = Reviews
        fields = (
            "router",
            "author",
            "text",
            "score",
            "pub_date",
        )


class CollectionsSerializer(serializers.ModelSerializer):
    user = HiddenField(default=CurrentUserDefault())
    routers = serializers.SerializerMethodField()

    class Meta:
        model = Collections
        fields = (
            "user",
            "name",
            "description",
            "routers",
            "is_public",
            "created_at",
        )

    def get_routers(self, obj):
        # Получаем все связанные записи CollectionRouters для текущей коллекции
        collection_routers = obj.collection_routers.all()
        # Извлекаем связанные маршруты Routers
        routers = [cr.router for cr in collection_routers]
        # Сериализуем маршруты
        return RoutersSerializer(routers, many=True).data


class FavoriteSerializer(serializers.ModelSerializer):
    user = HiddenField(default=CurrentUserDefault())
    routers = serializers.SerializerMethodField()

    class Meta:
        model = Favorite
        fields = (
            "user",
            "routers",
        )
