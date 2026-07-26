from database.db import get_session
from database.models import GithubProject, StarHistory, Paper


def save_projects(projects):
    db = get_session()

    for p in projects:
        old = db.query(GithubProject).filter_by(name=p["name"]).first()

        if old:
            old.stars = p["stars"]
            old.forks = p["forks"]
            old.score = p.get("score", old.score)
            if "ai_score" in p:
                old.ai_score = p["ai_score"]
            if "category" in p:
                old.category = p["category"]
            if "tech_tags" in p:
                old.tech_tags = p["tech_tags"]
            if "readme_summary" in p:
                old.readme_summary = p["readme_summary"]
        else:
            obj = GithubProject(
                name=p["name"],
                url=p["url"],
                stars=p["stars"],
                forks=p["forks"],
                score=p.get("score", 0.0),
                description=p.get("description") or "",
                category=p.get("category", "Other"),
                ai_score=p.get("ai_score", 0.0),
                tech_tags=p.get("tech_tags", ""),
                readme_summary=p.get("readme_summary", ""),
            )
            db.add(obj)

        db.add(StarHistory(project=p["name"], stars=p["stars"]))

    db.commit()


def save_papers(papers):
    db = get_session()
    for p in papers:
        db.add(
            Paper(
                title=p["title"],
                url=p["url"],
                summary=p["summary"],
            )
        )

    db.commit()
