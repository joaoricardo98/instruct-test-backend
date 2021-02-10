import os
import requests
from datetime import datetime


class GithubApi:
    API_URL = os.environ.get("GITHUB_API_URL", "https://api.github.com")
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
    HEADER = {"Authorization": f"token {GITHUB_TOKEN}"}

    def get_organization_projects(self, login: str) -> (dict, int):
        """Busca uma organização no Github

        :param login: login da organização no Github
        :returns: uma tupla com os repositorios, e o status code.
        """
        git_request = requests.get(f"{self.API_URL}/orgs/{login}/repos", headers=self.HEADER)
        return git_request.json(), git_request.status_code

    def get_organization_name(self, login: str) -> str:
        """Buscar o nome da organização

        :param login: login da organização no Github
        :return: Nome da organização
        """
        return requests.get(f"{self.API_URL}/users/{login}").json()["name"]

    def get_project_issues_count(self, login: str, project: str, initial_date, end_date) -> int:
        """Retorna a quantidade de issues do projeto de acordo com o filtro

        :param login: login da organização no Github
        :param project: Projeto do github
        :param initial_date: Data de inicio do filtro
        :param end_date: Data de fim do filtro
        :return: total de issues
        """
        issues = requests.get(
            f"{self.API_URL}/repos/{login}/{project}/issues", params={"state": "all"}, headers=self.HEADER
        )
        issues_count = len(
            [
                issue for issue in issues.json()
                if initial_date <= datetime.strptime(issue["created_at"], "%Y-%m-%dT%H:%M:%SZ") <= end_date
            ]
        )
        return issues_count

    def get_project_pulls_requests_count(self, login: str, project: str, initial_date, end_date) -> int:
        """Retorna a quantidade de pulls_requests do projeto de acordo com o filtro

        :param login: login da organização no Github
        :param project: Projeto do github
        :param initial_date: Data de inicio do filtro
        :param end_date: Data de fim do filtro
        :return: total de PRs
        """
        pulls_requests = requests.get(
            f"{self.API_URL}/repos/{login}/{project}/pulls", params={"state": "all"}, headers=self.HEADER
        )
        pulls_count = len(
            [
                pr for pr in pulls_requests.json()
                if initial_date <= datetime.strptime(pr["created_at"], "%Y-%m-%dT%H:%M:%SZ") <= end_date
            ]
        )
        return pulls_count

