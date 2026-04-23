import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KB_PATH = os.path.join(BASE_DIR, "data", "knowledge_base.json")

with open(KB_PATH, "r") as f:
    knowledge_base = json.load(f)


def get_response(user_input: str) -> str:
    user_input = user_input.lower().strip()
    tokens = set(user_input.replace("?", "").replace("!", "").split())

    best_match = None
    best_score = 0

    for faq in knowledge_base["faqs"]:
        score = len(tokens & set(faq["keywords"]))
        if score > best_score:
            best_score = score
            best_match = faq["response"]

    return best_match if best_score > 0 else knowledge_base["default_response"]
