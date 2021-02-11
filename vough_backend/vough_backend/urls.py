from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="API endpoints",
      terms_of_service="https://www.google.com/policies/terms/",
   ),
   public=True,
)
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.routes"), name="api"),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0)),
]
