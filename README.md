# 🧬 Pharma GitHub Radar V2

> AI 药物研发技术情报监控系统（GitHub 研发情报雷达）

V2 专业版是一个 **GitHub 研发情报监控系统**，重点不是 AI 制药知识推理，而是：

> **自动监控 GitHub 热门项目、Star 快速增长项目、AI / 药物研发趋势，并生成每日技术情报主页。**

## 功能

- GitHub Trending 监控
- Star 增长速度分析
- AI Drug Discovery 项目发现
- RDKit / Chemistry 项目追踪
- arXiv 论文监控
- 项目智能评分（Pharma Radar Score）
- README 技术方向解析
- 自动生成日报
- Streamlit Dashboard 可视化
- Telegram 通知推送
- GitHub Actions 自动化 + GitHub Pages 展示
- Docker 一键部署

## 技术架构

```
GitHub API / Trending / arXiv
            ↓
       Data Collector
            ↓
       SQLite Database
            ↓
     Scoring Engine (Star / Fork / Growth / Chemistry)
            ↓
     Markdown Report + HTML 情报主页 + Dashboard
            ↓
   GitHub Pages / Telegram / Commit
```

## 目录结构

```
Pharma-GitHub-Radar-V2
├── README.md
├── main.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── config.yaml
├── .env.example
├── collectors/          # 数据采集
├── analyzer/            # 评分 / 分类 / 排名 / README 解析
├── database/            # SQLite + ORM 模型 + 操作
├── report/              # 日报生成
├── notification/        # Telegram 推送
├── dashboard/           # Streamlit 可视化
├── data/                # 数据库与产物
└── .github/workflows/   # 自动化
```

## 启动

安装依赖：

```bash
pip install -r requirements.txt
```

运行采集与生成日报：

```bash
python main.py
```

启动 Dashboard：

```bash
streamlit run dashboard/app.py
```

访问 http://localhost:8501

## GitHub Pages 情报主页

每次运行 `python main.py`（或 GitHub Actions 每日触发）都会在项目根目录生成：

- `index.html` —— 漂亮的可视化情报主页（统计卡片 + Star 排行榜 + 快速增长榜 + 分类分布 + 最新论文），可直接作为 GitHub Pages 站点
- `DAILY_REPORT.md` —— 纯文本日报（兼容 Markdown 阅读）

部署到 GitHub Pages：

1. 仓库 **Settings → Pages → Build and deployment → Source：Deploy from a branch → 选择 `gh-pages`**
2. 推送 `/main` 后，`pages.yml` 工作流会自动把 `index.html` 发布到 `gh-pages` 分支
3. 访问 `https://<user>.github.io/<repo>/` 即可看到每日自动更新的情报主页

> 也可在本地用 `python -m http.server` 直接预览生成的 `index.html`。

## 配置

复制 `.env.example` 为 `.env` 并填写：

- `GITHUB_TOKEN`：GitHub API Token（提高速率限制）
- `TG_TOKEN` / `TG_CHAT_ID`：Telegram 机器人（可选，用于每日推送）

关键词与阈值在 `config.yaml` 中配置。

## Docker 部署

```bash
docker compose up
```

会自动启动采集服务与主页（Dashboard 端口 8501）。
