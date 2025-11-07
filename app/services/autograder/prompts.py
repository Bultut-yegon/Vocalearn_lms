# app/services/autograder/prompts.py
def build_feedback_prompt(answer, rubric, scores, context):
    return f"""
    Evaluate the following student answer based on the rubric:
    Context: {context}
    Answer: {answer}
    Scores: {scores}
    Rubric: {rubric}
    Provide constructive feedback in 2 sentences.
    """
