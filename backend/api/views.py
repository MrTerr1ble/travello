from api.forms import CollectionForm, PointsOfInterestForm, RouterForm
from api.serializers import (
    CollectionsSerializer,
    CustomUserSerializer,
    FavoriteSerializer,
    PointsOfInterestSerializer,
    ReviewsSerializer,
    RoutersSerializer,
)
from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect, render
from djoser.views import UserViewSet
from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from trail.models import (
    CollectionRouters,
    Collections,
    Favorite,
    PointsOfInterest,
    Reviews,
    RoutePoints,
    Routers,
)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]

    def list(self, request, *args, **kwargs):
        if request.accepted_renderer.format == "html":
            return render(request, "includes/profile.html", {"routers": self.queryset})
        return super().list(request, *args, **kwargs)


class CustomLoginView(LoginView):
    template_name = "includes/login.html"

    def get_success_url(self):
        return "/api/routers/"


class CustomLogoutView(LogoutView):

    def post(self, request, *args, **kwargs):
        # Дополнительная логика, которая выполняется перед выходом
        # Например, можно добавить сообщение о выходе
        messages.success(request, "Вы успешно вышли из системы.")
        # Вызов стандартного механизма выхода
        logout(request)
        # Перенаправление после выхода
        return redirect("login")


class RoutersViewSet(viewsets.ModelViewSet):
    queryset = Routers.objects.prefetch_related("router_points__point").all()
    serializer_class = RoutersSerializer
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]

    def list(self, request, *args, **kwargs):
        routers = self.queryset.all()
        if request.accepted_renderer.format == "html":
            return render(request, "includes/routers_list.html", {"routers": routers})
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        router = self.get_object()
        points = router.router_points.all()
        if request.accepted_renderer.format == "html":
            return render(
                request,
                "includes/router_detail.html",
                {"router": router, "points": points},
            )
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        if request.accepted_renderer.format == "html":
            return self.handle_html_post_create(request)
        return super().create(request, *args, **kwargs)

    def handle_html_post_create(self, request):
        form = RouterForm(
            request.POST or None, request.FILES or None, user=request.user
        )
        if request.method == "POST":
            if form.is_valid():
                # Создаем маршрут без сохранения в базе данных
                router = form.save(commit=False)
                # Устанавливаем текущего пользователя как автора
                router.author = request.user

                # Сохраняем маршрут (он теперь сохраняется в БД)
                router.save()

                # Сохраняем точки интереса
                points = form.cleaned_data.get("points_of_interest")
                if points:
                    for point in points:
                        RoutePoints.objects.create(router=router, point=point)

                # Перенаправляем на список маршрутов
                return redirect("api:router-list")

        return render(request, "includes/router_create.html", {"form": form})


class PointsOfInterestViewSet(viewsets.ModelViewSet):
    queryset = PointsOfInterest.objects.all()
    serializer_class = PointsOfInterestSerializer
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]  # JSON + HTML

    def list(self, request, *args, **kwargs):
        points = self.queryset.all()
        if request.accepted_renderer.format == "html":
            return render(request, "includes/points_list.html", {"points": points})
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        point = self.get_object()

        # Получаем все связанные точки маршрута
        # Проверяем формат запроса
        if request.accepted_renderer.format == "html":
            # Передаем объект router и связанные points в контекст шаблона
            return render(request, "includes/point_detail.html", {"point": point})

        # Для API-запросов возвращаем стандартный ответ
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        if request.accepted_renderer.format == "html":
            return self.handle_html_post_create(request)
        return super().create(request, *args, **kwargs)

    def handle_html_post_create(self, request):
        form = PointsOfInterestForm(request.POST or None, request.FILES or None)
        if request.method == "POST":
            if form.is_valid():
                # Устанавливаем текущего пользователя как автора
                router = form.save(commit=False)
                router.author = request.user
                router.save()
                return redirect("api:point-list")
        return render(request, "includes/point_create.html", {"form": form})


class ReviewsViewSet(viewsets.ModelViewSet):
    queryset = Reviews.objects.all()
    serializer_class = ReviewsSerializer
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]  # JSON + HTML

    def list(self, request, *args, **kwargs):
        reviews = self.queryset.all()
        if request.accepted_renderer.format == "html":
            return render(request, "includes/reviews_list.html", {"reviews": reviews})
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        return Reviews.objects.select_related("author", "router").filter(
            router_id=self.kwargs["router_id"]
        )

    def perform_create(self, serializer):
        router = get_object_or_404(Routers, id=self.kwargs["router_id"])
        serializer.save(author=self.request.user, router=router)


class CollectionsViewSet(viewsets.ModelViewSet):
    queryset = Collections.objects.prefetch_related(
        "collection_routers__router"
    ).filter(is_public__exact=1)
    serializer_class = CollectionsSerializer
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]  # JSON + HTML

    def list(self, request, *args, **kwargs):
        collections = self.queryset.all()
        if request.accepted_renderer.format == "html":
            return render(
                request, "includes/collections_list.html", {"collections": collections}
            )
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        collection = self.get_object()
        if request.accepted_renderer.format == "html":
            return render(
                request, "includes/collection_detail.html", {"collection": collection}
            )
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        if request.accepted_renderer.format == "html":
            return self.handle_html_post_create(request)
        return super().create(request, *args, **kwargs)

    def handle_html_post_create(self, request):
        form = CollectionForm(request.POST or None, user=request.user)
        if request.method == "POST":
            if form.is_valid():
                # Создаем коллекцию без сохранения в базе данных
                collection = form.save(commit=False)
                collection.author = request.user
                collection.save()  # сохраняем коллекцию

                # Обработка выбранных маршрутов
                routers = form.cleaned_data.get("routers")
                if routers:
                    for router in routers:
                        CollectionRouters.objects.create(
                            collection=collection, router=router
                        )

                return redirect("api:collection-list")
        return render(request, "includes/collection_create.html", {"form": form})


class FavoritesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FavoriteSerializer
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        if request.accepted_renderer.format == "html":
            return render(
                request, "includes/favorites.html", {"favorites": self.get_queryset()}
            )
        return super().list(request, *args, **kwargs)
