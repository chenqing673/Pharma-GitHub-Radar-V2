import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

VALID_SINCE = ("daily", "weekly", "monthly")


def _parse_int(text):
    """把 '1,234' / '12.3k' / '1.2m' 解析成整数。"""
    if text is None:
        return 0
    text = text.lower().replace(",", "").strip()
    m = re.search(r"([\d.]+)\s*(k|m)?", text)
    if not m:
        return 0
    num = float(m.group(1))
    unit = m.group(2)
    if unit == "k":
        num *= 1_000
    elif unit == "m":
        num *= 1_000_000
    return int(num)


def collect_github_trending(since="daily"):
    """抓取 GitHub Trending（github.com/trending）真实热门榜。

    这是 GitHub 官方按 star 增速排名的榜单，与本项目 keyword 搜索得到的
    'Star 排行榜' 不同 —— 它反映的是全站近期真正快速增长的仓库。

    since: daily / weekly / monthly
    返回: [{name, url, description, language, stars, stars_today, since}, ...]
    """
    if since not in VALID_SINCE:
        since = "daily"

    url = f"https://github.com/trending?since={since}"

    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
    except Exception:
        # 网络受限 / 被限流时不拖垮主流程
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    results = []

    for article in soup.select("article.Box-row"):
        a = article.select_one("h2 a")
        if not a:
            continue
        href = (a.get("href") or "").strip()
        if not href.startswith("/"):
            continue

        name = href.strip("/")
        repo_url = "https://github.com" + href

        desc_el = article.select_one("p")
        description = desc_el.get_text(strip=True) if desc_el else ""

        stars = 0
        star_a = article.select_one('a[href$="/stargazers"]')
        if star_a:
            stars = _parse_int(star_a.get_text(" ", strip=True))

        stars_today = 0
        today_span = article.select_one("span.float-sm-right")
        if today_span:
            stars_today = _parse_int(today_span.get_text(" ", strip=True))

        lang_el = article.select_one('span[itemprop="programmingLanguage"]')
        language = lang_el.get_text(strip=True) if lang_el else ""

        results.append(
            {
                "name": name,
                "url": repo_url,
                "description": description,
                "language": language,
                "stars": stars,
                "stars_today": stars_today,
                "since": since,
            }
        )

    return results
