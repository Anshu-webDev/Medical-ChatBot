import json
import os
import re
from difflib import SequenceMatcher

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KB_PATH = os.path.join(BASE_DIR, "data", "knowledge_base.json")

with open(KB_PATH, "r") as f:
    knowledge_base = json.load(f)

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "i", "me", "my", "we", "our", "you", "your", "it", "its",
    "do", "does", "did", "can", "could", "will", "would", "should",
    "have", "has", "had", "this", "that", "these", "those",
    "of", "in", "on", "at", "to", "about", "and", "or", "but",
    "so", "if", "any", "some", "tell", "give", "please", "want", "know", "get"
}

# Minimum fuzzy similarity to consider a word as matching
FUZZY_THRESHOLD = 0.78

# Minimum score to return a match instead of default response
MIN_CONFIDENCE = 0.45


def clean(text: str) -> str:
    return re.sub(r"[^a-z0-9\s]", "", text.lower()).strip()


def tokenize(text: str) -> list:
    tokens = clean(text).split()
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]


def fuzzy_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def phrase_similarity(user_input: str, keyword: str) -> float:
    """
    Compare user input against a keyword phrase using two strategies:
    1. Whole phrase similarity (good for multi-word keywords)
    2. Token-level fuzzy match (good for partial / misspelled input)
    Returns the higher of the two scores.
    """
    cleaned_input = clean(user_input)
    cleaned_keyword = clean(keyword)

    # Strategy 1: full phrase similarity
    phrase_score = fuzzy_similarity(cleaned_input, cleaned_keyword)

    # Strategy 2: token-level match — each keyword token vs each input token
    input_tokens = tokenize(user_input)
    keyword_tokens = [t for t in cleaned_keyword.split() if len(t) > 1]

    if not input_tokens or not keyword_tokens:
        return phrase_score

    token_scores = []
    for kt in keyword_tokens:
        best = max(fuzzy_similarity(it, kt) for it in input_tokens)
        if best >= FUZZY_THRESHOLD:
            token_scores.append(best)

    if token_scores:
        coverage = len(token_scores) / len(keyword_tokens)
        avg = sum(token_scores) / len(token_scores)
        token_score = avg * coverage
    else:
        token_score = 0.0

    return max(phrase_score, token_score)


def score_faq(user_input: str, keywords: list) -> float:
    if not keywords:
        return 0.0

    # Score each keyword phrase and take the best match
    scores = [phrase_similarity(user_input, kw) for kw in keywords]
    return max(scores)


def get_response(user_input: str) -> str:
    user_input = user_input.strip()
    if not user_input:
        return knowledge_base["default_response"]

    best_match = None
    best_score = 0.0

    for faq in knowledge_base["faqs"]:
        score = score_faq(user_input, faq["keywords"])
        if score > best_score:
            best_score = score
            best_match = faq["response"]

    return best_match if best_score >= MIN_CONFIDENCE else knowledge_base["default_response"]
