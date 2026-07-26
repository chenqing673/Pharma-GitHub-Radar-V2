from database.db import get_session
from database.models import GithubProject


def intelligent_ranking(limit=20):
    db = get_session()

    return (
        db.query(GithubProject)
        .order_by(GithubProject.ai_score.desc())
        .limit(limit)
        .all()
    )
