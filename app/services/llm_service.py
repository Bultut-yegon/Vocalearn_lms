import os
import logging
from typing import Optional

from openai import OpenAI

logger = logging.getLogger(__name__)

class LLMService:

    def __init__(self):
        self.enabled = os.getenv("ENABLE_LLM", "false").lower() == "true"

        if self.enabled:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            logger.info("LLM service enabled.")
        else:
            logger.info("LLM service disabled.")

    async def generate_explanation(self, topic_recommendations, study_plan, strengths):
        if not self.enabled:
            return None

        prompt = f"""
        Act as an expert learning coach. Be realistic and avoid hallucinations.
        Explain the recommendations below in a helpful, motivational way:

        Topic Recommendations: {topic_recommendations}
        Study Plan: {study_plan}
        Strengths: {strengths}

        Give a single, friendly paragraph.
        """

        try:
            completion = self.client.responses.create(
                model="gpt-4.1-mini",
                input=prompt
            )

            explanation = completion.output_text
            return explanation

        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return None
