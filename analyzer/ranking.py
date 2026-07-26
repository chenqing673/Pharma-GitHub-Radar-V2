from database.db import get_session
from database.models import GithubProject, StarHistory


def top_star_projects(limit=20):
    db = get_session()
    return (
        db.query(GithubProject)
        .order_by(GithubProject.stars.desc())
        .limit(limit)
        .all()
    )


def fast_growth_projects(limit=20):
    db = get_session()

    projects = db.query(GithubProject).all()

    result = []

    for p in projects:
        history = (
            db.query(StarHistory)
            .filter_by(project=p.name)
            .order_by(StarHistory.record_time.desc())
            .limit(2)
            .all()
        )

        if len(history) == 2:
            growth = history[0].stars - history[1].stars

            result.append(
                {
                    "name": p.name,
                    "growth": growth,
                    "stars": p.stars,
                }
            )

    result.sort(key=lambda x: x["growth"], reverse=True)

    return result[:limit]
