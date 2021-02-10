from django.db.models import CASCADE
from django.db.models import CharField
from django.db.models import ForeignKey
from django.db.models import Model
from django.db.models import IntegerField


class Organization(Model):
    name = CharField(max_length=256, blank=False, null=False)
    slug = CharField(max_length=256, blank=False, null=False)

    def __str__(self):
        return f"{self.id} - {self.name}"


class Repository(Model):
    organization = ForeignKey(Organization, related_name="top_3_repositories", on_delete=CASCADE)
    name = CharField(max_length=256, blank=False, null=False)
    issues_count = IntegerField(default=0)
    pulls_count = IntegerField(default=0)

    def __str__(self):
        return f"{self.id} - {self.name}"

    @property
    def rating(self):
        return self.rating_calc(self.pulls_count, self.issues_count)

    @staticmethod
    def rating_calc(pulls_count: int, issues_count: int):
        return pulls_count * 2 + issues_count

