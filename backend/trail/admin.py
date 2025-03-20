from django.contrib import admin
from .models import Routers, PointsOfInterest, Reviews, Collections


@admin.register(Routers)
class RoutersAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author'
    )


@admin.register(PointsOfInterest)
class PointsOfInterestAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category'
    )


@admin.register(Reviews)
class ReviewsAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'router'
    )


@admin.register(Collections)
class CollectionsAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'user'
    )
