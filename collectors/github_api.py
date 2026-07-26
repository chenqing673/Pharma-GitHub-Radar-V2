import requests
import os

TOKEN = os.getenv("GITHUB_TOKEN")
headers = {}
if TOKEN:
    headers = {"Authorization": f"token {TOKEN}"}


def search_repo(keyword):
    url = "https://api.github.com/search/repositories"
    params = {
        "q": keyword,
        "sort": "stars",
        "order": "desc",
        "per_page": 20,
    }

    r = requests.get(url, params=params, headers=headers)
    return r.json().get("items", [])


def collect_github():
    keywords = [
        "drug discovery",
        "AI chemistry",
        "RDKit",
        "molecular generation",
        "retrosynthesis",
    ]

    result = []
    for k in keywords:
        repos = search_repo(k)
        for repo in repos:
            result.append(
                {
                    "name": repo["full_name"],
                    "url": repo["html_url"],
                    "stars": repo["stargazers_count"],
                    "forks": repo["forks_count"],
                    "description": repo.get("description") or "",
                }
            )

    return result
