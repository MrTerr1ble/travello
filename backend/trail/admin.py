from django.contrib import admin

from .models import (
    CollectionRouters,
    Collections,
    PointsOfInterest,
    Reviews,
    RoutePoints,
    Routers,
)


class RoutePointsInline(admin.TabularInline):
    model = RoutePoints
    extra = 1


class CollectionRoutersInline(admin.TabularInline):
    model = CollectionRouters
    extra = 1


@admin.register(Routers)
class RoutersAdmin(admin.ModelAdmin):
    list_display = ("name", "author")
    inlines = [RoutePointsInline]


@admin.register(PointsOfInterest)
class PointsOfInterestAdmin(admin.ModelAdmin):
    list_display = ("name", "category")


@admin.register(Reviews)
class ReviewsAdmin(admin.ModelAdmin):
    list_display = ("author", "router")


@admin.register(Collections)
class CollectionsAdmin(admin.ModelAdmin):
    list_display = ("name", "user")
    inlines = [CollectionRoutersInline]
