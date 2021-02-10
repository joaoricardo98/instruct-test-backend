from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from api.views import OrganizationView
from api.views import OrganizationCreateView


routers = DefaultRouter()
routers.register("orgs", OrganizationView, basename="Organizacoes")

urlpatterns = [
    path("", include(routers.urls)),
    path("orgs/<str:slug>/", OrganizationCreateView.as_view())
]
