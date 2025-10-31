from api.forms import CustomUserCreationForm
from api.views import (
    CollectionsViewSet,
    CustomLoginView,
    CustomLogoutView,
    CustomPasswordChangeView,
    CustomUserViewSet,
    PointsOfInterestViewSet,
    ReviewsViewSet,
    RoutersViewSet,
)
from django.urls import include, path, reverse_lazy
from django.views.generic.edit import CreateView

app_name = "api"

user_list = CustomUserViewSet.as_view({"get": "list", "post": "create"})
user_detail = CustomUserViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
)

user_collection = CustomUserViewSet.as_view(
    {
        "get": "list",
    }
)

user_favorites = CustomUserViewSet.as_view(
    {
        "get": "list",
    }
)

router_list = RoutersViewSet.as_view({"get": "list", "post": "create"})
router_detail = RoutersViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
)
router_create = RoutersViewSet.as_view({"get": "create", "post": "create"})

point_list = PointsOfInterestViewSet.as_view({"get": "list", "post": "create"})
point_detail = PointsOfInterestViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
)
point_create = PointsOfInterestViewSet.as_view({"get": "create", "post": "create"})

collection_list = CollectionsViewSet.as_view({"get": "list", "post": "create"})
collection_detail = CollectionsViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
)

collection_create = CollectionsViewSet.as_view({"get": "create", "post": "create"})

review_list = ReviewsViewSet.as_view({"get": "list", "post": "create"})
review_detail = ReviewsViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
)

urlpatterns = [
    path("users/", user_list, name="user-list"),
    path("users/<int:pk>/", user_detail, name="user-detail"),
    path("users/collections/", user_collection, name="user-collections"),
    path("users/favorites/", user_favorites, name="user-favorites"),
    path("routers/", router_list, name="router-list"),
    path("routers/create/", router_create, name="router-create"),
    path("routers/<int:pk>/", router_detail, name="router-detail"),
    path("points/", point_list, name="point-list"),
    path("points/create/", point_create, name="point-create"),
    path("points/<int:pk>/", point_detail, name="point-detail"),
    path("collections/", collection_list, name="collection-list"),
    path("collections/<int:pk>/", collection_detail, name="collection-detail"),
    path("collections/create/", collection_create, name="collection-create"),
    path("routers/<int:router_id>/reviews/", review_list, name="review-list"),
    path(
        "routers/<int:router_id>/reviews/<int:pk>/", review_detail, name="review-detail"
    ),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
    path("login/", CustomLoginView.as_view(), name="login"),
    path(
        "logout/", CustomLogoutView.as_view(next_page="api:router-list"), name="logout"
    ),
    path(
        "password/change/",
        CustomPasswordChangeView.as_view(),
        name="password-change",
    ),
    path(
        "auth/registration/",
        CreateView.as_view(
            template_name="registration/registration_form.html",
            form_class=CustomUserCreationForm,
            success_url=reverse_lazy("api:router-list"),
        ),
        name="registration",
    ),
]
