# app/services/autograder/models.py
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

class ShortAnswerGraderModel:
    """
    Mock model wrapper – simulates a fine-tuned text grading model.
    Returns soft scores between 0 and 1.
    """
    def __init__(self, model_name: str = "distilbert-base-uncased"):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name,
            num_labels=1  # regression output
        )

    def predict(self, answer_text: str, context: str = "") -> float:
        inputs = self.tokenizer(
            f"{context} {answer_text}",
            truncation=True,
            padding="max_length",
            max_length=256,
            return_tensors="pt"
        )
        with torch.no_grad():
            outputs = self.model(**inputs)
            score = torch.sigmoid(outputs.logits).item() * 5.0  # scale 0–5
        return round(score, 2)
