from django import forms
from django.contrib.auth.forms import UserCreationForm
from trail.models import (
    CollectionRouters,
    Collections,
    PointsOfInterest,
    RoutePoints,
    Routers,
)
from users.models import User


class RouterForm(forms.ModelForm):
    points_of_interest = forms.ModelMultipleChoiceField(
        queryset=PointsOfInterest.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "form-select"}),
        required=False,
        label="Точки интереса",
    )

    class Meta:
        model = Routers
        fields = [
            "name",
            "description",
            "start_date",
            "end_date",
            "is_public",
            "photo",
            "points_of_interest",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
            "start_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "end_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "is_public": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "photo": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)

        if self.user:
            instance.author = (
                self.user
            )  # Устанавливаем текущего пользователя как автора

        if commit:
            instance.save()

            # Удалим старые связи, если редактируем
            RoutePoints.objects.filter(router=instance).delete()

            # Сохраняем новые связи
            points = self.cleaned_data.get("points_of_interest")
            if points:
                for point in points:
                    RoutePoints.objects.create(router=instance, point=point)

        return instance


class PointsOfInterestForm(forms.ModelForm):
    class Meta:
        model = PointsOfInterest
        fields = "__all__"
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
            "latitude": forms.NumberInput(attrs={"class": "form-control"}),
            "longitude": forms.NumberInput(attrs={"class": "form-control"}),
            "category": forms.TextInput(attrs={"class": "form-control"}),
            "photo": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


class CollectionForm(forms.ModelForm):
    routers = forms.ModelMultipleChoiceField(
        queryset=Routers.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "form-select"}),
        required=False,
        label="Маршруты",
    )

    class Meta:
        model = Collections
        fields = ["name", "description", "is_public", "routers"]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите название коллекции",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите описание коллекции",
                    "rows": 3,
                }
            ),
            "is_public": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "routers": forms.CheckboxSelectMultiple(
                attrs={"class": "form-check-input"}
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.user = self.user

        if commit:
            instance.save()

            # Очищаем старые связи (если редактируем)
            CollectionRouters.objects.filter(collection=instance).delete()

            # Создаем новые связи
            routers = self.cleaned_data.get("routers")
            if routers:
                for router in routers:
                    CollectionRouters.objects.create(collection=instance, router=router)

        return instance


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")
