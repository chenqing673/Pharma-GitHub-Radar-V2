import feedparser
import requests


def collect_arxiv(max_results=10):
    """Query arXiv API for drug-discovery + AI papers.

    Uses requests with params dict so the library handles URL encoding
    (spaces and special chars in search_query must be percent-encoded).
    Falls back to an empty list on any network/parse error so that an
    arXiv outage never crashes the radar pipeline.
    """
    url = "https://export.arxiv.org/api/query"
    params = {
        "search_query": "all:drug discovery AI",
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }

    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)
    except Exception as e:
        print(f"[arxiv] fetch failed: {e}")
        return []

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