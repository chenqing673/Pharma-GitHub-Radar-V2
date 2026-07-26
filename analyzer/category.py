def classify(name, description):
    text = (name + str(description)).lower()

    if "rdkit" in text:
        return "Chemistry"

    if "protein" in text:
        return "Protein AI"

    if "drug" in text:
        return "Drug Discovery"

    return "Other"
