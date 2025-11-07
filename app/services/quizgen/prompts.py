# app/services/quizgen/prompts.py

def build_generation_prompt(seed_text: str, qtype: str, difficulty: str, num: int):
    """
    Build a compact prompt to instruct an LLM to generate `num` questions
    of type `qtype` and `difficulty` focused on `seed_text`.
    Keep prompt short and deterministic-ish so fallback templates are easy to mirror.
    """
    return (
        f"Create {num} {qtype} questions for vocational training (TVET) students at {difficulty} level.\n"
        f"Focus on: {seed_text}\n\n"
        "For each question provide:\n"
        "- id (short unique id)\n"
        "- question text\n"
        "- for MCQs provide 4 options and indicate the correct option index (0-based)\n"
        "- for short answers provide the concise correct answer\n\n"
        "Return the results in JSON array format only."
    )
