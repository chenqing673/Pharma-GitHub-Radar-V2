from database.db import get_session
from database.models import GithubProject
from collections import Counter


def category_statistics():
    db = get_session()
    projects = db.query(GithubProject).all()

    categories = []

    for p in projects:
        categories.append(p.category)

    return Counter(categories)
