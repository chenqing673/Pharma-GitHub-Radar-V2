# 🧬 Pharma GitHub Radar V2

> AI 药物研发技术情报监控系统（GitHub 研发情报雷达）

🌐 **在线情报主页**：https://chenqing673.github.io/Pharma-GitHub-Radar-V2/

> ⚠️ GitHub Pages 仅对 **public 仓库**免费。若 Settings → Pages 提示 Upgrade / 付费，请先把仓库设为 public（Settings → Danger Zone → Change repository visibility → Make public），再设置 Pages 源为 `gh-pages` 分支。

V2 专业版是一个 **GitHub 研发情报监控系统**，重点不是 AI 制药知识推理，而是：

> **自动监控 GitHub 热门项目、Star 快速增长项目、AI / 药物研发趋势，并生成每日技术情报主页。**

## 功能

- GitHub Trending 监控（github.com/trending 官方增速榜，独立板块「🔥 GitHub 真实热门榜」）
- 真实热门榜**中文简介**（为每个 Trending 项目自动生成简单中文介绍，离线词表方案即可工作；可选 LLM 升级为流畅全文翻译）
- Star 增长速度分析（本项目关键词仓库的本地 star 差值，与 Trending 榜单区分）
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

- `index.html` —— 漂亮的可视化情报主页（统计卡片 + Star 排行榜 + 快速增长榜 + 分类分布 + 最新论文），可直接作为 GitHub Pages 站点。其中「🔥 GitHub 真实热门榜」每个项目都带**简单中文简介**（语言 + 主要技术方向），并附英文原文
- `DAILY_REPORT.md` —— 纯文本日报（兼容 Markdown 阅读），热门榜同样含中文简介与原文

## 如何使用

**只看情报主页（推荐）：** 浏览器直接打开 GitHub Pages 地址即可，无需安装任何东西（见下方部署地址）。

**自己跑 / 看真实数据：**

```bash
pip install -r requirements.txt
python main.py                  # 采集 → 评分 → 入库 → 生成 index.html + DAILY_REPORT.md
streamlit run dashboard/app.py  # 交互式 Dashboard，访问 http://localhost:8501
```

> 生成的 `index.html` 用浏览器直接打开也能看（与 Pages 同一套页面）。

## 部署 GitHub Pages

每次运行 `python main.py`（或 GitHub Actions 每日触发）都会生成上面的 `index.html` 与 `DAILY_REPORT.md`。

1. **首次启用**：仓库需为 **public**（private 仓库启用 Pages 会被要求升级付费）。然后 **Settings → Pages → Build and deployment → Source：Deploy from a branch → 分支选 `gh-pages` / 根目录 → Save**（若打开站点地址是 404，通常是这一步没做）
2. 推送 `/main` 后，`pages.yml` 工作流会自动把 `index.html` 发布到 `gh-pages` 分支
3. 访问 `https://<user>.github.io/<repo>/` 即可看到每日自动更新的情报主页

> 本项目地址：`https://chenqing673.github.io/Pharma-GitHub-Radar-V2/`
> 也可在本地用 `python -m http.server` 直接预览生成的 `index.html`。

### 立即获取真实数据（手动触发）

页面数据来自最近一次 `python main.py` 的运行结果。刚克隆 / 首次推送时页面显示的是**示例数据**，想立刻看到真实 GitHub 数据，无需等待每日定时：

1. 打开仓库 **Actions** 标签页
2. 选择工作流 **Pharma Radar Daily Update**
3. 点击 **Run workflow → Run**

工作流会用 Actions 自带的 `GITHUB_TOKEN` 采集并重新生成 `index.html`，提交后 `pages.yml` 自动重新发布。

### 数据说明

- 报告内容为「最近一次生成的快照」，每天 **UTC 01:00** 由 `daily.yml` 自动刷新
- 首次推送的页面为占位示例数据，首次真实运行后会被真实 GitHub / arXiv 数据覆盖
- Telegram 推送为可选项：在 **Settings → Secrets → Actions** 添加 `TG_TOKEN`、`TG_CHAT_ID` 后才会发送，不影响采集与 Pages
- 关键词与阈值在 `config.yaml` 中配置

## 配置

复制 `.env.example` 为 `.env` 并填写：

- `GITHUB_TOKEN`：GitHub API Token（提高速率限制）
- `TG_TOKEN` / `TG_CHAT_ID`：Telegram 机器人（可选，用于每日推送）

关键词与阈值在 `config.yaml` 中配置。

### 真实热门榜「中文简介」配置

每个 GitHub Trending 项目都会自动生成一句简单中文简介，展示在情报主页、日报与 Dashboard 中：

- **默认（离线词表方案）**：基于 GitHub 返回的 `语言` + `topics` 主题标签，配合内置「英文技术词→中文」词表生成，例如「使用 Python 开发；主要方向：机器学习、大语言模型、智能体。」，并附英文原文。无需任何外部 API，CI 每天自动运行即可。
- **可选（LLM 全文翻译）**：若希望简介更流畅自然，在 `.env` 或仓库 **Secrets** 中设置 `ZH_INTRO_LLM=1` 并提供 `LLM_API_KEY`（以及可选的 `LLM_BASE_URL` / `LLM_MODEL`，兼容 OpenAI 接口），则改用 LLM 把项目摘要成 1-2 句中文。未配置时自动降级为离线方案，不影响主流程。

## Docker 部署

```bash
docker compose up
```

会自动启动采集服务与主页（Dashboard 端口 8501）。
