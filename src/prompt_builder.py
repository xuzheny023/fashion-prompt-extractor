def generate_prompt(keywords):
    parts = [v for k, v in keywords.items()]
    return ", ".join(parts) + ", fashion design"
