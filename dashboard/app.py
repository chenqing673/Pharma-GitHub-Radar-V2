import streamlit as st
import pandas as pd
import plotly.express as px

from database.db import get_session
from database.models import GithubProject, StarHistory, TrendingRepo
from analyzer.ranking import fast_growth_projects, top_star_projects, top_trending
from analyzer.statistics import category_statistics

st.set_page_config(page_title="Pharma GitHub Radar", layout="wide")

st.title("🧬 Pharma GitHub Radar V2")

st.sidebar.title("功能")
page = st.sidebar.selectbox(
    "选择",
    ["Star排行榜", "快速增长榜", "GitHub热门", "趋势分析", "分类统计"],
)

# -----------------------
# Star排行榜
# -----------------------
if page == "Star排行榜":
    st.header("⭐ GitHub热门项目")

    projects = top_star_projects(20)

    data = []
    for p in projects:
        data.append(
            {
                "项目": p.name,
                "Stars": p.stars,
                "Score": p.score,
            }
        )

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

    fig = px.bar(df, x="项目", y="Stars", title="Stars排名")
    st.plotly_chart(fig)

# -----------------------
# 增长榜
# -----------------------
elif page == "快速增长榜":
    st.header("🚀 Star快速增长榜")

    data = fast_growth_projects()

    df = pd.DataFrame(data)

    st.dataframe(df, use_container_width=True)

    fig = px.bar(df, x="name", y="growth", title="每日Star增长")
    st.plotly_chart(fig)

# -----------------------
# GitHub 真实热门榜
# -----------------------
elif page == "GitHub热门":
    st.header("🔥 GitHub 真实热门榜（24h）")
    st.caption("数据来自 github.com/trending（GitHub 官方按 star 增速排名），"
               "与关键词 Star 排行榜不同，反映全站近期真正快速增长的仓库。")

    since = st.radio("周期", ["daily", "weekly", "monthly"], horizontal=True)
    trending = top_trending(20, since)

    if trending:
        df = pd.DataFrame(
            [
                {
                    "项目": t.name,
                    "当日新增": t.stars_today,
                    "总Stars": t.stars,
                    "语言": t.language,
                    "链接": t.url,
                }
                for t in trending
            ]
        )
        st.dataframe(df, use_container_width=True)

        fig = px.bar(df, x="项目", y="当日新增",
                     title=f"GitHub Trending（{since}）当日新增 Star")
        st.plotly_chart(fig)
    else:
        st.info("暂无可用的 GitHub Trending 数据，请先运行 python main.py 采集。")

# -----------------------
# 趋势分析
# -----------------------
elif page == "趋势分析":
    st.header("📈 Star趋势")

    db = get_session()

    history = db.query(StarHistory).all()

    df = pd.DataFrame(
        [
            {
                "项目": x.project,
                "Stars": x.stars,
                "时间": x.record_time,
            }
            for x in history
        ]
    )

    if len(df):
        project = st.selectbox("选择项目", df["项目"].unique())

        data = df[df["项目"] == project]

        fig = px.line(data, x="时间", y="Stars")
        st.plotly_chart(fig)
    else:
        st.info("暂无历史数据，请先运行 python main.py 采集。")

# -----------------------
# 分类统计
# -----------------------
elif page == "分类统计":
    st.header("🧬 AI制药分类排行")

    counter = category_statistics()

    if counter:
        df = pd.DataFrame(
            [
                {"分类": k, "项目数": v}
                for k, v in counter.items()
            ]
        )

        st.dataframe(df, use_container_width=True)

        fig = px.bar(df, x="分类", y="项目数", title="分类分布")
        st.plotly_chart(fig)
    else:
        st.info("暂无项目数据，请先运行 python main.py 采集。")
