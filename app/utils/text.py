def make_user_text(interests=None, weaknesses=None, recent_content=None):
    parts = []
    if interests:
        parts.append("Interests: " + ", ".join(interests))
    if weaknesses:
        parts.append("Weaknesses: " + ", ".join(weaknesses))
    if recent_content:
        parts.append("Recent: " + ", ".join(recent_content))
    return ". ".join(parts) if parts else "General vocational training"
