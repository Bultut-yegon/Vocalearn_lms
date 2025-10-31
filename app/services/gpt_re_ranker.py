import os
import json
import time
from app.core.config import settings
import openai

openai.api_key = settings.OPENAI_API_KEY

# safe JSON parsing helper
def _safe_parse(text):
    try:
        return json.loads(text)
    except Exception:
        # last-resort: attempt to extract JSON from code block or first {...}
        import re
        m = re.search(r"(\{.*\}|\[.*\])", text, re.S)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                return None
        return None

def re_rank_with_gpt(user_profile: str, baseline_recs: list, model="gpt-4o-mini", temperature=0.2, max_recs=10):
    """
    baseline_recs: list of dicts with keys title, tags, difficulty (and content_id)
    Returns: list of dicts: content_id, title, reason (string)
    """
    # build candidate list string
    candidates_text = ""
    for i, item in enumerate(baseline_recs[:max_recs]):
        candidates_text += f"{i+1}. id:{item['content_id']} title:{item['title']} tags:{item.get('tags','')[:120]} difficulty:{item.get('difficulty','')}\n"

    prompt = f"""
Learner profile:
{user_profile}

Candidates (top {min(len(baseline_recs), max_recs)}):
{candidates_text}

Task:
1. Re-rank the candidates by relevance to the learner.
2. For each candidate return a JSON array of objects with keys:
   - content_id (int)
   - title (string)
   - reason (short string < 120 chars)

Return ONLY JSON array. Example:
[{{"content_id": 12, "title":"...", "reason":"..."}}, ...]
    """

    try:
        resp = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role":"system","content":"You are an educational recommender assistant."},
                {"role":"user","content":prompt}
            ],
            temperature=temperature,
            max_tokens=800
        )
        text = resp["choices"][0]["message"]["content"]
        parsed = _safe_parse(text)
        if parsed:
            return parsed
    except Exception as e:
        # log in production
        # fallback: return baseline as-is with simple reasons
        pass

    # fallback: baseline with default reasons
    fallback = []
    for item in baseline_recs[:max_recs]:
        fallback.append({
            "content_id": item["content_id"],
            "title": item["title"],
            "reason": "Recommended based on baseline hybrid score"
        })
    return fallback
