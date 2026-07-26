from collectors.github_api import collect_github
from collectors.github_trending import collect_github_trending
from collectors.arxiv import collect_arxiv

from analyzer.scoring import calculate_score
from analyzer.advanced_score import pharma_score
from analyzer.category import classify
from analyzer.readme_analyzer import get_readme, analyze_readme

from database.db import init_db
from database.operations import save_projects, save_papers, save_trending

from report.generator import generate_report
from notification.telegram import send_message


def main():
    init_db()

    projects = collect_github()

    for p in projects:
        p["score"] = calculate_score(p)
        p["ai_score"] = pharma_score(p)
        p["category"] = classify(p["name"], p.get("description") or "")

        # 可选：解析 README 技术方向（失败不影响主流程）
        try:
            readme = get_readme(p["name"])
            analysis = analyze_readme(readme)
            p["tech_tags"] = ",".join(analysis["keywords"])
            p["readme_summary"] = readme[:2000] if readme else ""
        except Exception:
            p["tech_tags"] = ""
            p["readme_summary"] = ""

    save_projects(projects)

    # GitHub 官方 Trending 真实热门榜（区别于上面的 keyword Star 排行榜）
    trending = collect_github_trending("daily")
    save_trending(trending, "daily")

    papers = collect_arxiv()
    save_papers(papers)

    generate_report()

    send_message("🧬 Pharma Radar 更新完成")

    print("Radar updated")


if __name__ == "__main__":
    main()
