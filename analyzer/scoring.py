def calculate_score(project):
    score = 0

    score += project["stars"] * 0.01
    score += project["forks"] * 0.05

    if project["stars"] > 5000:
        score += 50

    return round(score, 2)
