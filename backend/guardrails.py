# backend/guardrails.py
import re

# --- Patterns ---
EMERGENCY_PATTERNS = [
    r"\b(chest pain|pressure in chest|tightness in chest)\b",
    r"\b(trouble breathing|shortness of breath|can't breathe|cannot breathe)\b",
    r"\b(stroke|face droop|slurred speech|one[- ]sided weakness|sudden numbness)\b",
    r"\b(severe bleeding|bleeding won't stop|profuse bleeding)\b",
    r"\b(suicidal|kill myself|end my life|self[- ]harm|harm myself)\b",
    r"\b(anaphylaxis|throat closing|severe allergic reaction)\b",
]
BANNED_PATTERNS = [
    r"\b(prescribe|prescription|controlled substances?)\b",
    r"\b(dose|dosage)\b.*\b(baby|infant|newborn|pregnan\w*)",
]

# --- Messages ---
EMERGENCY_MSG = (
    "If you’re experiencing symptoms like chest pain, trouble breathing, stroke signs, "
    "severe bleeding, anaphylaxis, or thoughts of self-harm, call your local emergency "
    "number immediately. I can only provide general educational information, not medical advice."
)

REFUSAL_MSG = (
    "I can’t help with that request. I’m not a clinician and can’t provide dosing, prescriptions, "
    "or controlled-substance guidance. I can share general educational information instead."
)

# --- Helpers ---
def needs_emergency_escalation(text: str) -> bool:
    t = (text or "").lower()
    return any(re.search(p, t) for p in EMERGENCY_PATTERNS)

def needs_refusal(text: str) -> bool:
    t = (text or "").lower()
    return any(re.search(p, t) for p in BANNED_PATTERNS)
