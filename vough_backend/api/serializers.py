from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import ReadOnlyField

from api.models import Organization
from api.models import Repository


class RepositorySerializer(ModelSerializer):
    rating = ReadOnlyField()

    class Meta:
        fields = ["rating", "name", "issues_count", "pulls_count"]
        model = Repository


class OrganizationSerializer(ModelSerializer):
    top_3_repositories = RepositorySerializer(many=True, read_only=True)

    class Meta:
        fields = ["name", "slug", "top_3_repositories"]
        model = Organization


