from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

# from django.conf.urls import url

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

schema_view = get_schema_view(
    openapi.Info(
        title='Travel API',
        default_version='v1',
        description="Документация",

    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# urlpatterns += [
#     url(r'^swagger(?P<format>\.json|\.yaml)$',
#         schema_view.without_ui(cache_timeout=0), name='schema-json'),
#     url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0),
#         name='schema-swagger-ui'),
#     url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0),
#         name='schema-redoc'),
# ]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    import debug_toolbar
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
