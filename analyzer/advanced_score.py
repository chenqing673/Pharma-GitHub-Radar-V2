import math


def star_score(stars):
    return min(math.log10(stars + 1) * 20, 40)


def fork_score(forks):
    return min(math.log10(forks + 1) * 10, 20)


def growth_score(growth):
    if growth <= 0:
        return 0

    return min(growth * 2, 20)


def chemistry_score(text):
    keywords = [
        "drug",
        "chemistry",
        "molecule",
        "rdkit",
        "protein",
        "reaction",
        "retrosynthesis",
        "docking",
    ]

    score = 0
    if text is None:
        return 0
    text = text.lower()

    for k in keywords:
        if k in text:
            score += 3

    return min(score, 20)


def pharma_score(project):
    score = (
        star_score(project.get("stars", 0))
        + fork_score(project.get("forks", 0))
        + chemistry_score(project.get("description") or "")
    )

    return round(score, 2)
