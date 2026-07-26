import requests
from bs4 import BeautifulSoup


def get_trending():
    url = "https://github.com/trending"

    html = requests.get(url).text

    soup = BeautifulSoup(html, "html.parser")

    repos = []
    for article in soup.select("article.Box-row"):
        title = article.h2.text.strip()
        repos.append(title)

    return repos
