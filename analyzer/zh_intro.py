"""为 GitHub Trending 真实热门榜的每个项目生成「简单中文简介」。

设计原则
--------
1. 离线兜底（默认启用，CI 每天自动跑）：用 GitHub 官方 API 拿到的
   `description` + `topics`（主题标签）+ `language`，配合一份「英文技术词→中文」
   词表，拼成一句通顺的中文简介。不依赖任何外部付费服务。
2. 高质量增强（可选，需配置密钥）：若设置环境变量 `ZH_INTRO_LLM=1` 且
   `LLM_API_KEY` 存在，则调用 OpenAI 兼容接口，把 README 摘要成 1-2 句中文。
   未配置时自动降级为离线词表方案，不报错、不拖垮主流程。
"""

import os
import re

# requests 在函数内部懒加载，避免纯中文简介逻辑因缺少依赖而报错
# （requests 已在 requirements.txt 中声明，CI 与本地均已安装）。

# ----------------------------------------------------------------------
# 1. 词表：英文技术词 / 短语 -> 中文
#    按长度降序匹配，避免 "go" 误伤 "google" 等短词。
# ----------------------------------------------------------------------
GLOSSARY = {
    # 顶层方向
    "machine learning": "机器学习",
    "deep learning": "深度学习",
    "artificial intelligence": "人工智能",
    "reinforcement learning": "强化学习",
    "large language model": "大语言模型",
    "llm": "大语言模型",
    "natural language processing": "自然语言处理",
    "computer vision": "计算机视觉",
    "speech recognition": "语音识别",
    "generative ai": "生成式 AI",
    "agent": "智能体",
    # 应用领域
    "drug discovery": "药物发现",
    "bioinformatics": "生物信息学",
    "genomics": "基因组学",
    "chemistry": "化学",
    "molecular": "分子",
    "protein": "蛋白质",
    "healthcare": "医疗健康",
    "medical": "医学",
    "robotics": "机器人",
    "blockchain": "区块链",
    "cryptocurrency": "加密货币",
    "game engine": "游戏引擎",
    "game": "游戏",
    # 技术类型
    "framework": "框架",
    "library": "库",
    "tool": "工具",
    "toolkit": "工具包",
    "cli": "命令行工具",
    "command line": "命令行工具",
    "command-line": "命令行工具",
    "sdk": "SDK",
    "api": "API",
    "orm": "对象关系映射",
    "compiler": "编译器",
    "interpreter": "解释器",
    "runtime": "运行时",
    "database": "数据库",
    "cache": "缓存",
    "queue": "消息队列",
    "server": "服务端",
    "client": "客户端",
    "frontend": "前端",
    "backend": "后端",
    "web": "Web",
    "mobile": "移动端",
    "desktop": "桌面端",
    "cloud": "云原生",
    "devops": "DevOps",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "microservice": "微服务",
    "template": "模板",
    "plugin": "插件",
    "extension": "扩展",
    "boilerplate": "脚手架",
    "starter": "起步模板",
    "tutorial": "教程",
    "example": "示例",
    "demo": "演示",
    "utils": "工具函数",
    "utility": "实用工具",
    "helper": "辅助工具",
    "authentication": "认证",
    "authorization": "授权",
    "encryption": "加密",
    "parser": "解析器",
    "scraper": "爬虫",
    "crawler": "爬虫",
    "bot": "机器人",
    "dashboard": "仪表盘",
    "ui": "界面",
    "ui kit": "UI 组件库",
    "component": "组件",
    "state management": "状态管理",
    "testing": "测试",
    "benchmark": "基准测试",
    "simulation": "仿真",
    "visualization": "可视化",
    "chart": "图表",
    "animation": "动画",
    "audio": "音频",
    "video": "视频",
    "image": "图像",
    "text": "文本",
    "search": "搜索引擎",
    "recommendation": "推荐系统",
    "pipeline": "流水线",
    "automation": "自动化",
    "monitoring": "监控",
    "logging": "日志",
    "self-hosted": "自托管",
    "open source": "开源",
    # 具体技术栈
    "react": "React",
    "vue": "Vue",
    "angular": "Angular",
    "svelte": "Svelte",
    "nextjs": "Next.js",
    "nodejs": "Node.js",
    "node": "Node.js",
    "typescript": "TypeScript",
    "javascript": "JavaScript",
    "python": "Python",
    "rust": "Rust",
    "golang": "Go",
    "go": "Go",
    "java": "Java",
    "kotlin": "Kotlin",
    "swift": "Swift",
    "c++": "C++",
    "cpp": "C++",
    "csharp": "C#",
    "c#": "C#",
    "php": "PHP",
    "ruby": "Ruby",
    "django": "Django",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "transformers": "Transformers",
    "langchain": "LangChain",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "redis": "Redis",
    "mongodb": "MongoDB",
    "sqlite": "SQLite",
    "linux": "Linux",
    "windows": "Windows",
    "macos": "macOS",
    "android": "Android",
    "ios": "iOS",
}

# 语言 -> 中文说明（带一点语境，比纯翻译更有信息量）
LANG_ZH = {
    "Python": "Python",
    "JavaScript": "JavaScript（前端/全栈）",
    "TypeScript": "TypeScript",
    "Rust": "Rust",
    "Go": "Go",
    "C++": "C++",
    "C": "C",
    "C#": "C#",
    "Java": "Java",
    "Kotlin": "Kotlin",
    "Swift": "Swift",
    "Objective-C": "Objective-C",
    "PHP": "PHP",
    "Ruby": "Ruby",
    "Shell": "Shell 脚本",
    "HTML": "HTML",
    "CSS": "CSS",
    "Vue": "Vue",
    "Jupyter Notebook": "Jupyter  notebooks（数据科学）",
    "Jupyter": "Jupyter",
    "Dart": "Dart（Flutter）",
    "Scala": "Scala",
    "R": "R（统计计算）",
    "Lua": "Lua",
    "Zig": "Zig",
    "Elixir": "Elixir",
    "Haskell": "Haskell",
}


def _topics_to_zh(topics):
    """topics 是英文标签列表（多为连字符形式，如 machine-learning），
    尽量翻译成中文；无词表项时保留原词。"""
    out = []
    for t in topics or []:
        key = t.lower()
        # 连字符与空格等价，便于匹配词表
        zh = GLOSSARY.get(key) or GLOSSARY.get(key.replace("-", " "))
        out.append(zh if zh else t)
    # 去重保序
    seen = set()
    uniq = []
    for x in out:
        if x not in seen:
            seen.add(x)
            uniq.append(x)
    return uniq


def _lang_to_zh(language):
    if not language:
        return ""
    return LANG_ZH.get(language, language)


def build_intro(name, description, language, topics, stars_today, stars):
    """离线生成一句简单中文简介（不需要任何外部服务）。

    采用「干净的结构化中文」：语言 + 主要技术方向，避免逐词翻译描述产生
    的中英混杂别扭句。完整英文描述由调用方作为「原文」单独展示。
    """
    parts = []

    lang_zh = _lang_to_zh(language)
    if lang_zh:
        parts.append(f"使用 {lang_zh} 开发")

    topic_zh = _topics_to_zh(topics)
    if topic_zh:
        parts.append("主要方向：" + "、".join(topic_zh))

    if not parts:
        body = "开源项目（暂无语言与主题信息，建议直接访问仓库查看原文）。"
    else:
        body = "；".join(parts) + "。"

    return body


# ----------------------------------------------------------------------
# 2. 可选 LLM 增强（OpenAI 兼容接口）
# ----------------------------------------------------------------------
def _llm_intro(name, description, topics, stars_today, stars):
    """调用 OpenAI 兼容接口生成 1-2 句中文简介。失败返回 None。"""
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        return None
    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")

    import requests

    topics_zh = "、".join(_topics_to_zh(topics)) or "未注明"
    prompt = (
        f"请用一句简短中文介绍这个 GitHub 开源项目，不超过 40 字，"
        f"只输出中文简介本身，不要解释、不要加引号。\n"
        f"项目名：{name}\n"
        f"原始描述：{description or '无'}\n"
        f"技术方向：{topics_zh}\n"
        f"语言：{language or '未注明'}"
    )

    try:
        r = requests.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 120,
            },
            timeout=20,
        )
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"].strip()
        return content or None
    except Exception:
        return None


# ----------------------------------------------------------------------
# 3. 抓取 topics（best-effort，失败不影响主流程）
# ----------------------------------------------------------------------
def get_repo_topics(full_name, token=None):
    """通过 GitHub API 获取仓库主题标签；失败返回 []。"""
    if not full_name or "/" not in full_name:
        return []
    try:
        import requests

        headers = {"Accept": "application/vnd.github+json"}
        if token:
            headers["Authorization"] = f"token {token}"
        r = requests.get(
            f"https://api.github.com/repos/{full_name}",
            headers=headers,
            timeout=15,
        )
        if r.status_code == 200:
            return r.json().get("topics", []) or []
    except Exception:
        pass
    return []


# ----------------------------------------------------------------------
# 4. 对外入口：给 trending 列表补充 topics 与 zh_intro
# ----------------------------------------------------------------------
def enrich_trending(trending, token=None, use_llm=False):
    """就地为 trending 每个元素添加 `topics` 与 `zh_intro` 字段。

    trending: collect_github_trending() 返回的列表，元素含
              name/url/description/language/stars/stars_today/since
    """
    use_llm = use_llm and os.getenv("ZH_INTRO_LLM") == "1"

    for t in trending:
        name = t.get("name", "")
        description = t.get("description") or ""
        language = t.get("language") or ""
        stars_today = t.get("stars_today", 0)
        stars = t.get("stars", 0)

        topics = get_repo_topics(name, token)
        t["topics"] = ",".join(topics)

        if use_llm:
            intro = _llm_intro(name, description, topics, stars_today, stars)
            if intro:
                t["zh_intro"] = intro
                continue

        # 离线兜底
        t["zh_intro"] = build_intro(
            name, description, language, topics, stars_today, stars
        )

    return trending
