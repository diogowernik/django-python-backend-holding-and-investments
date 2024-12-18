# core/urls.py

from django.contrib import admin
from django.urls import path, include, re_path
from admin_commands.admin import admin_site 
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from djoser.views import (TokenCreateView)
from .views import home
from django.conf import settings
import os
from django.http import HttpResponse


SECRET_ADMIN_PATH = os.getenv("SECRET_ADMIN_PATH")

def robots_txt(request):
    content = "User-agent: *\nDisallow: /"
    return HttpResponse(content, content_type="text/plain")


schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(AllowAny,) if settings.DEBUG else (IsAuthenticated,),
)

urlpatterns = [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path(f'{SECRET_ADMIN_PATH}/commands/', admin_site.urls),
    path(f'{SECRET_ADMIN_PATH}/', admin.site.urls),
    path("robots.txt", robots_txt),


    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/token/login/', TokenCreateView.as_view(), name='login'),
    path('auth/', include('wtree.urls')),
    path('api/portfolios/', include('portfolios.urls')),
    path('api/brokers/', include('brokers.urls')),
    path('api/investments/', include('investments.urls')),
    path('api/radar/', include('radar.urls')),
    path('api/cashflow/', include('cashflow.urls')),
    path('api/kids/', include('kids.urls')),

    path('', home, name='home'),
]
