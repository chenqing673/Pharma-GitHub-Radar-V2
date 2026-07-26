import feedparser


def collect_arxiv():
    url = (
        "https://export.arxiv.org/api/query?"
        "search_query=all:"
        "drug discovery AI"
        "&max_results=10"
    )

    feed = feedparser.parse(url)

    papers = []
    for p in feed.entries:
        papers.append(
            {
                "title": p.title,
                "url": p.link,
                "summary": p.summary,
            }
        )

    return papers
