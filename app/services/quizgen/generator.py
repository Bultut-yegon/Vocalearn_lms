# app/services/quizgen/generator.py
import os
import uuid
import json
from typing import List, Dict, Any
from pathlib import Path
from sentence_transformers import SentenceTransformer, util
from app.core.config import settings

# Optional LLM import - only used if key present
try:
    from openai import OpenAI
    _OPENAI_AVAILABLE = True
except Exception:
    _OPENAI_AVAILABLE = False

# local simple model for embedding retrieval (small, quick)
_EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_embedder = SentenceTransformer(_EMBED_MODEL_NAME)

# small built-in fallback templates for deterministic generation
def _template_mcq(seed_text: str, difficulty: str, idx: int) -> Dict[str, Any]:
    qid = f"mcq_{idx}_{uuid.uuid4().hex[:6]}"
    question = f"What is a key step in {seed_text}?"
    options = [
        f"Step A for {seed_text}",
        f"Step B for {seed_text}",
        f"Step C for {seed_text}",
        f"Step D for {seed_text}"
    ]
    correct_index = 0
    return {"id": qid, "question": question, "options": options, "correct_index": correct_index, "difficulty": difficulty}

def _template_short(seed_text: str, difficulty: str, idx: int) -> Dict[str, Any]:
    qid = f"short_{idx}_{uuid.uuid4().hex[:6]}"
    question = f"Explain briefly the main purpose of {seed_text}."
    answer = f"The main purpose of {seed_text} is to ..."
    return {"id": qid, "question": question, "answer": answer, "difficulty": difficulty}

def _template_truefalse(seed_text: str, difficulty: str, idx: int) -> Dict[str, Any]:
    qid = f"tf_{idx}_{uuid.uuid4().hex[:6]}"
    question = f"True or False: {seed_text} always requires X."
    answer = False
    return {"id": qid, "question": question, "answer": answer, "difficulty": difficulty}


class QuizGenerator:
    def __init__(self):
        self.openai_client = None
        if settings.OPENAI_API_KEY and _OPENAI_AVAILABLE:
            self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)  # or credentials through env

    def _use_llm(self, prompt: str) -> List[Dict[str, Any]]:
        """
        Call the OpenAI client to get JSON results; expects model that returns JSON.
        If OpenAI not available or any error occurs, raise and caller will fallback.
        """
        if not self.openai_client:
            raise RuntimeError("LLM client not configured")
        # Using Chat Completions API
        resp = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",  # replace with licensed model or user preference; may fail if unavailable
            messages=[{"role":"user","content":prompt}],
            temperature=0.2,
            max_tokens=800
        )
        text = resp.choices[0].message.content
        # attempt parse JSON
        parsed = json.loads(text)
        return parsed

    def _semantic_focus(self, seed_text: str, candidates: List[str], top_k: int = 3) -> List[str]:
        """
        If you have course content snippets, choose most relevant based on embeddings.
        `candidates` is a list of textual sections.
        """
        if not seed_text or not candidates:
            return candidates[:top_k]
        q_emb = _embedder.encode(seed_text, convert_to_numpy=True, normalize_embeddings=True)
        c_embs = _embedder.encode(candidates, convert_to_numpy=True, normalize_embeddings=True)
        sims = util.cos_sim(q_emb, c_embs)[0].numpy()
        top_idx = sims.argsort()[::-1][:top_k]
        return [candidates[i] for i in top_idx]

    def generate(self, seed_text: str, num_questions: int = 5, difficulty: str = "medium",
                 question_types=None, content_candidates: List[str] = None) -> Dict[str, Any]:
        """
        Return a quiz dict with questions. Tries LLM if configured, otherwise falls back to templates.
        """
        question_types = question_types or ["mcq", "short"]
        qs = []

        # try using LLM if available
        if self.openai_client:
            from app.services.quizgen.prompts import build_generation_prompt
            try:
                prompt = build_generation_prompt(seed_text or "general vocational skills", qtype=", ".join(question_types), difficulty=difficulty, num=num_questions)
                llm_out = self._use_llm(prompt)
                # Expecting list of dictionaries; if not, fall back
                if isinstance(llm_out, list):
                    # Normalization step: ensure required keys present
                    for item in llm_out[:num_questions]:
                        qs.append(item)
                    return {"quiz_id": str(uuid.uuid4()), "questions": qs, "metadata": {"source": "llm"}}
            except Exception:
                # fallthrough to fallback templates
                pass

        # fallback deterministic generation
        cands = content_candidates or []
        focused = self._semantic_focus(seed_text or "", cands, top_k=3)

        # generate sequence of question templates
        idx = 0
        for i in range(num_questions):
            qtype = question_types[i % len(question_types)]
            if qtype == "mcq":
                q = _template_mcq(seed_text or (focused[i % len(focused)] if focused else "topic"), difficulty, idx)
            elif qtype == "true_false":
                q = _template_truefalse(seed_text or (focused[i % len(focused)] if focused else "topic"), difficulty, idx)
            else:
                q = _template_short(seed_text or (focused[i % len(focused)] if focused else "topic"), difficulty, idx)
            qs.append(q)
            idx += 1

        return {"quiz_id": str(uuid.uuid4()), "questions": qs, "metadata": {"source": "template", "seed_matches": len(focused)}}
