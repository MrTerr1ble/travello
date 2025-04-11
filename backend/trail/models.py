from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models  # type: ignore
from users.models import User


class Routers(models.Model):
    name = models.CharField(max_length=256, verbose_name="Название маршрута")
    description = models.CharField(max_length=256, verbose_name="Описание маршрута")
    start_date = models.DateField(verbose_name="Дата начала тура")
    end_date = models.DateField(verbose_name="Дата окончания маршрута")

    is_public = models.BooleanField(verbose_name="Виден для всех?")
    created_at = models.DateField(
        auto_now_add=True, verbose_name="Дата создания маршрута"
    )
    photo = models.ImageField(
        blank=True,
        upload_to="media/routers/",
    )
    author = models.ForeignKey(
        User, related_name="routers", verbose_name="Автор", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Маршрут"
        verbose_name_plural = "Маршруты"

    def __str__(self):
        return self.name


class PointsOfInterest(models.Model):
    name = models.CharField(max_length=256, verbose_name="Название точки интереса")

    description = models.CharField(
        max_length=256, verbose_name="Описание точки интереса"
    )
    latitude = models.DecimalField(
        max_digits=22, decimal_places=16, blank=True, null=True
    )
    longitude = models.DecimalField(
        max_digits=22, decimal_places=16, blank=True, null=True
    )
    category = models.CharField(max_length=256, verbose_name="Категория места")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    photo = models.ImageField(
        blank=True,
        upload_to="media/routers/",
    )

    class Meta:
        verbose_name = "Точка интереса"
        verbose_name_plural = "Точки интереса"

    def __str__(self):
        return self.name


class Reviews(models.Model):
    router = models.ForeignKey(
        Routers,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Маршрут",
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews", verbose_name="Автор"
    )
    text = models.TextField(max_length=256, verbose_name="Текс отзыва")
    score = models.PositiveSmallIntegerField(
        default=1,
        null=False,
        verbose_name="Оценка",
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    pub_date = models.DateField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return self.text[:15]


class Collections(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="collections",
        verbose_name="Владелец коллекции",
    )
    name = models.CharField(max_length=256, verbose_name="Название коллекции")
    description = models.CharField(max_length=256, verbose_name="Описание коллекции")
    is_public = models.BooleanField(verbose_name="Коллекция видна для всех?")
    created_at = models.DateField(
        auto_now_add=True, verbose_name="Дата создания коллекции"
    )

    class Meta:
        verbose_name = "Коллекция"
        verbose_name_plural = "Коллекции"

    def __str__(self):
        return self.name


class RoutePoints(models.Model):
    router = models.ForeignKey(
        Routers, on_delete=models.CASCADE, related_name="router_points"
    )
    point = models.ForeignKey(
        PointsOfInterest, on_delete=models.CASCADE, related_name="router_points"
    )


class CollectionRouters(models.Model):
    collection = models.ForeignKey(
        Collections, on_delete=models.CASCADE, related_name="collection_routers"
    )
    router = models.ForeignKey(
        Routers, on_delete=models.CASCADE, related_name="collection_routers"
    )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorite",
        verbose_name="Избранное",
    )
    router = models.ForeignKey(
        Routers, on_delete=models.CASCADE, related_name="favorite"
    )

    class Meta:
        verbose_name = "Избранный маршрут"
        verbose_name_plural = "Избранные маршруты"
