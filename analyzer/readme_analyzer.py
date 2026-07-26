import requests


def get_readme(repo):
    # 依次尝试 main / master 两个默认分支
    for branch in ("main", "master"):
        url = f"https://raw.githubusercontent.com/{repo}/{branch}/README.md"
        r = requests.get(url)
        if r.status_code == 200:
            return r.text

    return ""


def analyze_readme(text):
    result = {
        "AI": False,
        "chemistry": False,
        "keywords": [],
    }

    keywords = [
        "AI",
        "machine learning",
        "deep learning",
        "RDKit",
        "SMILES",
        "molecule",
        "drug",
    ]

    for k in keywords:
        if k.lower() in text.lower():
            result["keywords"].append(k)

    if len(result["keywords"]) > 2:
        result["AI"] = True

    if "RDKit" in result["keywords"]:
        result["chemistry"] = True

    return result
