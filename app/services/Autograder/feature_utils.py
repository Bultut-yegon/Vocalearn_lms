# app/services/autograder/feature_utils.py
from transformers import AutoTokenizer

class TextPreprocessor:
    def __init__(self, model_name: str = "distilbert-base-uncased"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

    def encode(self, text: str):
        """Tokenize and prepare model input"""
        return self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=256,
            return_tensors="pt"
        )
