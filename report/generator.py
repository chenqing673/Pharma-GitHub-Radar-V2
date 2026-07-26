import html
from datetime import datetime

from analyzer.ranking import top_star_projects, fast_growth_projects, top_trending
from analyzer.statistics import category_statistics

from database.db import get_session
from database.models import Paper, GithubProject

from notification.telegram import send_message


def notify(report):
    send_message(report[:3000])


# ----------------------------------------------------------------------
# 1. Markdown 日报（保留原有逻辑）
# ----------------------------------------------------------------------
def generate_markdown():
    md = """
# 🧬 Pharma GitHub Radar Daily

## ⭐ Star排行榜

"""

    for p in top_star_projects():
        md += f"""
### {p.name}

⭐ Stars: {p.stars}
Score: {p.score}
"""

    md += """


# 🚀 Star快速增长榜

"""

    for p in fast_growth_projects():
        md += f"""
## {p['name']}

今日增长: +{p['growth']}
当前Stars: {p['stars']}

"""

    md += """

# 🔥 GitHub 真实热门榜（24h）

> 数据来自 github.com/trending（GitHub 官方按 star 增速排名），与上方关键词搜索的「Star 排行榜」不同，反映全站近期真正快速增长的仓库。

"""

    for t in top_trending(20, "daily"):
        md += f"""
## {t.name}

⭐ 当日新增: +{t.stars_today}
总 Stars: {t.stars}
语言: {t.language}
{t.url}

"""

    return md


# ----------------------------------------------------------------------
# 2. 漂亮 HTML 情报主页（GitHub Pages）
# ----------------------------------------------------------------------
CSS = """
:root{
  --bg:#f5f7fb; --card:#ffffff; --ink:#0f172a; --muted:#64748b;
  --line:#e2e8f0; --accent:#0ea5a4; --accent2:#6366f1;
  --warn:#f59e0b; --good:#10b981; --shadow:0 1px 3px rgba(15,23,42,.08),0 8px 24px rgba(15,23,42,.06);
}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue","PingFang SC","Microsoft YaHei",sans-serif;
  background:var(--bg);color:var(--ink);line-height:1.6}
a{color:var(--accent2);text-decoration:none}
a:hover{text-decoration:underline}
.hero{background:linear-gradient(120deg,#0ea5a4 0%,#6366f1 100%);color:#fff;padding:48px 24px 40px}
.hero-inner{max-width:1080px;margin:0 auto}
.hero h1{margin:0;font-size:30px;letter-spacing:.5px}
.hero p{margin:8px 0 0;opacity:.9}
.wrap{max-width:1080px;margin:0 auto;padding:24px}
section{margin:32px 0}
h2{font-size:20px;margin:0 0 16px;display:flex;align-items:center;gap:8px}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.stat{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;box-shadow:var(--shadow)}
.stat .k{font-size:13px;color:var(--muted)}
.stat .v{font-size:24px;font-weight:700;margin-top:4px}
.stat .s{font-size:12px;color:var(--muted);margin-top:2px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px;box-shadow:var(--shadow)}
.row{margin:14px 0}
.row-head{display:flex;justify-content:space-between;font-size:14px;margin-bottom:6px}
.row-head .val{color:var(--accent2);font-weight:600}
.bar{height:10px;background:var(--line);border-radius:999px;overflow:hidden}
.bar-fill{height:100%;border-radius:999px;background:linear-gradient(90deg,var(--accent),var(--accent2))}
.bar-fill.warn{background:linear-gradient(90deg,var(--warn),#fb923c)}
.chips{display:flex;flex-wrap:wrap;gap:10px}
.chip{background:#eef2ff;color:#3730a3;border:1px solid #c7d2fe;border-radius:999px;padding:6px 14px;font-size:13px}
.paper{border-left:3px solid var(--accent);padding:10px 14px;margin:12px 0;background:#f8fafc;border-radius:0 10px 10px 0}
.paper .t{font-weight:600}
.paper .d{font-size:13px;color:var(--muted);margin-top:4px}
.empty{color:var(--muted);font-style:italic;padding:12px 0}
footer{text-align:center;color:var(--muted);font-size:13px;padding:32px 16px 48px}
@media(max-width:720px){.stats{grid-template-columns:repeat(2,1fr)}}
"""

CHIP_COLORS = [
    ("Drug Discovery", "#e0f2fe", "#0369a1", "#bae6fd"),
    ("Chemistry", "#dcfce7", "#15803d", "#bbf7d0"),
    ("Protein AI", "#ede9fe", "#6d28d9", "#ddd6fe"),
    ("Other", "#fef3c7", "#b45309", "#fde68a"),
]


def _chip_style(cat):
    for name, bg, fg, bd in CHIP_COLORS:
        if name == cat:
            return f"background:{bg};color:{fg};border:1px solid {bd}"
    return "background:#f1f5f9;color:#475569;border:1px solid #e2e8f0"


def _bar_row(name, value, max_value, display, url=None, warn=False):
    pct = (value / max_value * 100) if max_value else 0
    link = f'<a href="{html.escape(url)}" target="_blank" rel="noopener">{html.escape(name)}</a>' if url else html.escape(name)
    fill_cls = "bar-fill warn" if warn else "bar-fill"
    return f'''<div class="row">
  <div class="row-head"><span>{link}</span><span class="val">{display}</span></div>
  <div class="bar"><div class="{fill_cls}" style="width:{pct:.1f}%"></div></div>
</div>'''


def generate_html():
    db = get_session()
    top = top_star_projects(20)
    growth = fast_growth_projects(20)
    trending = top_trending(20, "daily")
    cats = category_statistics()
    papers = db.query(Paper).order_by(Paper.created.desc()).limit(10).all()
    total = db.query(GithubProject).count()

    top_star = top[0] if top else None
    top_growth = growth[0] if growth else None
    top_trend = trending[0] if trending else None
    max_stars = max((p.stars for p in top), default=1)
    max_growth = max((g["growth"] for g in growth), default=1)
    max_today = max((t.stars_today for t in trending), default=1)
    max_cat = max(cats.values(), default=1)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # ---- 统计卡片 ----
    stats_html = f'''
<div class="stats">
  <div class="stat"><div class="k">监控项目</div><div class="v">{total}</div><div class="s">关键词 GitHub 仓库</div></div>
  <div class="stat"><div class="k">🔥 最高 Star</div><div class="v">{top_star.stars if top_star else 0}</div><div class="s">{html.escape(top_star.name) if top_star else "—"}</div></div>
  <div class="stat"><div class="k">🚀 Trending 当日新增</div><div class="v">+{top_trend.stars_today if top_trend else 0}</div><div class="s">{html.escape(top_trend.name) if top_trend else "—"}</div></div>
  <div class="stat"><div class="k">📚 论文追踪</div><div class="v">{len(papers)}</div><div class="s">arXiv 最新</div></div>
</div>'''

    # ---- Star 排行榜 ----
    if top:
        star_html = "".join(
            _bar_row(p.name, p.stars, max_stars, f"⭐ {p.stars}",
                     url=p.url) for p in top
        )
    else:
        star_html = '<div class="empty">暂无数据，请先运行 python main.py 采集。</div>'

    # ---- 快速增长榜（本地 keyword 项目 star 差值）----
    if growth:
        growth_html = "".join(
            _bar_row(g["name"], g["growth"], max_growth, f"+{g['growth']}", warn=True)
            for g in growth
        )
    else:
        growth_html = '<div class="empty">数据不足（需至少两次采集记录）才能计算增长。</div>'

    # ---- GitHub 真实热门榜（github.com/trending）----
    if trending:
        trending_html = "".join(
            _bar_row(
                t.name,
                t.stars_today,
                max_today,
                f"⭐ +{t.stars_today} / 24h · 总 {t.stars}",
                url=t.url,
            )
            for t in trending
        )
    else:
        trending_html = (
            '<div class="empty">暂无可用的 GitHub Trending 数据'
            "（采集失败或网络受限，不影响其余板块）。</div>"
        )

    # ---- 分类分布 ----
    if cats:
        cat_html = '<div class="chips">'
        for cat, cnt in cats.most_common():
            cat_html += f'<span class="chip" style="{_chip_style(cat)}">{html.escape(cat)} · {cnt}</span>'
        cat_html += "</div>"
        cat_bars = "".join(
            _bar_row(cat, cnt, max_cat, str(cnt)) for cat, cnt in cats.most_common()
        )
        cat_html += f'<div style="margin-top:16px">{cat_bars}</div>'
    else:
        cat_html = '<div class="empty">暂无数据。</div>'

    # ---- 论文 ----
    if papers:
        paper_html = ""
        for p in papers:
            summary = (p.summary or "")[:160]
            paper_html += f'''<div class="paper">
  <div class="t"><a href="{html.escape(p.url)}" target="_blank" rel="noopener">{html.escape(p.title)}</a></div>
  <div class="d">{html.escape(summary)}{"…" if len(p.summary or "") > 160 else ""}</div>
</div>'''
    else:
        paper_html = '<div class="empty">暂无论文。</div>'

    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>🧬 Pharma GitHub Radar V2 · 每日技术情报</title>
<style>{CSS}</style>
</head>
<body>
<header class="hero"><div class="hero-inner">
  <h1>🧬 Pharma GitHub Radar V2</h1>
  <p>GitHub AI 药物研发技术情报 · 每日自动更新 · {now}</p>
</div></header>
<div class="wrap">
  <section>{stats_html}</section>
  <section><h2>⭐ GitHub 热门项目（Star 排行榜）</h2><div class="card">{star_html}</div></section>
  <section><h2>🚀 Star 快速增长榜</h2><div class="card">{growth_html}</div>
    <p class="s" style="color:var(--muted);font-size:13px;margin-top:10px">本榜为本项目关键词仓库的本地 star 差值（需连续运行多天才有数据）。</p>
  </section>
  <section><h2>🔥 GitHub 真实热门榜（24h）</h2><div class="card">{trending_html}</div>
    <p class="s" style="color:var(--muted);font-size:13px;margin-top:10px">数据来自 <a href="https://github.com/trending?since=daily" target="_blank" rel="noopener">github.com/trending</a>（GitHub 官方按 star 增速排名），反映全站近期真正快速增长的仓库，与上方关键词排行榜不同。</p>
  </section>
  <section><h2>🧬 AI 制药分类分布</h2><div class="card">{cat_html}</div></section>
  <section><h2>📚 最新 arXiv 论文</h2><div class="card">{paper_html}</div></section>
</div>
<footer>由 Pharma GitHub Radar 自动生成 · 数据采集自 GitHub API 与 arXiv · GitHub Actions 每日构建</footer>
</body>
</html>"""

    with open("index.html", "w", encoding="utf8") as f:
        f.write(page)


def generate_report():
    md = generate_markdown()
    with open("DAILY_REPORT.md", "w", encoding="utf8") as f:
        f.write(md)

    generate_html()

    notify(md)
