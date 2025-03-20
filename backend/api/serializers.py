import base64


from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer

from django.core.files.base import ContentFile

from trail.models import Routers, PointsOfInterest, Reviews, Collections

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            img_format, img_str = data.split(';base64,')
            ext = img_format.split('/')[-1]
            data = ContentFile(base64.b64decode(img_str), name=f'image.{ext}')
        return super().to_internal_value(data)


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(allow_null=True, required=False)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )


class CustomUserCreateSerializer(UserCreateSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)


class RoutersSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer()

    class Meta:
        model = Routers
        fields = (
            'name',
            'description',
            'start_date',
            'end_date',
            'is_public',
            'created_at',
            'author',
        )


class PointsOfInterestSerializer(serializers.ModelSerializer):
    class Meta:
        modedel = PointsOfInterest
        fields = (
            'name',
            'description',
            'location',
            'category',
            'is_public',
            'created_at',
        )


class ReviewsSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer()
    router = RoutersSerializer(many=True)

    class Meta:
        model = Reviews
        fields = (
            'router',
            'author',
            'text',
            'score',
            'pub_date',
        )


class CollectionsSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = Collections
        fields = (
            'user',
            'name',
            'description',
            'is_public',
            'created_at',
        )
