from datetime import datetime

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.models import Organization
from api.models import Repository
from api.serializers import OrganizationSerializer
from api.integrations.github import GithubApi


class OrganizationView(ListModelMixin, GenericViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer


class OrganizationCreateView(GenericAPIView):

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    def delete(self, request, slug: str):
        if organization := Organization.objects.filter(slug=slug).first():
            organization.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(data={"error": "Org não cadastrada!"}, status=status.HTTP_404_NOT_FOUND)

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




