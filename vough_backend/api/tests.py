import json
from unittest.mock import patch

from rest_framework import status

from api.models import Organization
from api.serializers import OrganizationSerializer


class TestView:
    def test_list_organization(self, api_client, organization_with_top_3_repositories):
        response = api_client.get('/api/orgs/')
        expected_org = OrganizationSerializer(organization_with_top_3_repositories)

        assert len(response.data) == 1
        assert json.dumps([expected_org.data]) == json.dumps(response.json())
        assert response.status_code == status.HTTP_200_OK

    def test_delete_organization(self, api_client, organization_with_top_3_repositories):
        assert Organization.objects.count() == 1

        api_client.delete(f'/api/orgs/{organization_with_top_3_repositories.slug}/')

        assert Organization.objects.count() == 0

    @patch('api.views.GithubApi.get_project_pulls_requests_count')
    @patch('api.views.GithubApi.get_project_issues_count')
    @patch('api.views.GithubApi.get_organization_name')
    @patch('api.views.GithubApi.get_organization_projects')
    def test_get_organization_without_cache(
            self,
            mock_get_organization_projects,
            mock_get_organization_name,
            mock_get_project_issues_count,
            mock_get_project_pulls_requests_count,
            api_client,
            fake,
            organization_name,
            projects_data
    ):
        mock_get_organization_projects.return_value = [{'name': p['name']} for p in projects_data], status.HTTP_200_OK
        mock_get_project_issues_count.side_effect = [p['issues_count'] for p in projects_data]
        mock_get_project_pulls_requests_count.side_effect = [p['pulls_count'] for p in projects_data]
        mock_get_organization_name.return_value = organization_name

        response = api_client.get(f'/api/orgs/{organization_name}/')

        assert response.status_code == status.HTTP_200_OK


