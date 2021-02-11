from datetime import datetime

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.openapi import Parameter
from drf_yasg.openapi import IN_QUERY
from drf_yasg.openapi import IN_PATH
from drf_yasg.openapi import TYPE_STRING

from api.models import Organization
from api.models import Repository
from api.serializers import OrganizationSerializer
from api.integrations.github import GithubApi


class OrganizationView(ListModelMixin, GenericViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    @swagger_auto_schema(operation_summary="Listar todas as organizações.")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrganizationCreateView(GenericAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    initial_date_parameter = Parameter(
        'initial_date', IN_QUERY, 'Querystring initial_date', format='YYYY-MM-DD', type=TYPE_STRING, required=False
    )
    end_date_parameter = Parameter(
        'end_date', IN_QUERY, 'Querystring end_date', format='YYYY-MM-DD', type=TYPE_STRING, required=False
    )
    slug_parameter = Parameter(
        'slug', IN_PATH, 'Nome da empresa a ser operada.', type=TYPE_STRING, required=True
    )

    @swagger_auto_schema(operation_summary="Deletar organização.", manual_parameters=[slug_parameter])
    def delete(self, request, slug: str):
        if organization := Organization.objects.filter(slug=slug).first():
            organization.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(data={"error": "Org não cadastrada!"}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_summary=(
            "Buscar organização dentro da API do github e retorna suas informações e top 3 projetos."
        ),
        manual_parameters=[initial_date_parameter, end_date_parameter, slug_parameter]
    )
    def get(self, request, slug: str):
        if not (organization := Organization.objects.filter(slug=slug).first()):
            github_api = GithubApi()
            projects, status_code = github_api.get_organization_projects(slug)

            if status.is_success(status_code):
                if not(initial_date := request.GET.get("initial_date") and (end_date := request.GET.get("end_date"))):
                    initial_date, end_date = "2020-07-01", "2020-12-31"
                try:
                    initial_date = datetime.strptime(initial_date, "%Y-%m-%d")
                    end_date = datetime.strptime(end_date, "%Y-%m-%d")
                except ValueError:
                    return Response(
                        data={"error": "Utilizar as datas initial_date e end_date no padrão YYYY-MM-DD."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                name = github_api.get_organization_name(slug)

                organization = Organization.objects.create(name=name, slug=slug)

                for project_data in self.get_top_3_projects(projects, slug, initial_date, end_date, github_api):
                    Repository.objects.create(**{"organization": organization, **project_data})
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(organization)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_top_3_projects(self, projects: list, slug: str, initial_date, end_date, github_api: GithubApi):
        projects_out = []
        for project in projects:
            project_name = project["name"]

            issues_count = github_api.get_project_issues_count(slug, project_name, initial_date, end_date)
            pulls_count = github_api.get_project_pulls_requests_count(slug, project_name, initial_date, end_date)

            projects_out.append(
                {
                    "name": project_name,
                    "issues_count": issues_count,
                    "pulls_count": pulls_count,
                }
            )

        return sorted(
            projects_out,
            key=lambda proj: Repository.rating_calc(proj["pulls_count"], proj["issues_count"]),
            reverse=True
        )[:3]




