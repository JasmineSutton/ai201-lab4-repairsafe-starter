from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL, VALID_TIERS

_client = Groq(api_key=GROQ_API_KEY)


CLASSIFIER_SYSTEM_PROMPT = """You are a safety classifier for home repair questions.

Classify each question into exactly one tier:
- safe: routine low-risk DIY tasks with low chance of serious harm.
- caution: moderate-risk tasks where mistakes can cause injury, damage, or code violations, but are not usually catastrophic.
- refuse: high-risk tasks where mistakes can cause fire, gas leak, flooding, structural failure, severe injury, or death, or generally require a licensed professional.

Boundary rule:
- If the question could plausibly lead to catastrophic harm when done incorrectly, choose refuse.
- If uncertain between caution and refuse, choose refuse.

Output exactly two lines:
TIER: <safe|caution|refuse>
REASON: <one concise sentence>

Do not output anything else.
"""


def _parse_classifier_output(text: str) -> dict:
  tier = None
  reason = None

  for raw_line in text.splitlines():
    line = raw_line.strip()
    lower = line.lower()
    if lower.startswith("tier:"):
      tier = line.split(":", 1)[1].strip().lower()
    elif lower.startswith("reason:"):
      reason = line.split(":", 1)[1].strip()

  if tier not in VALID_TIERS:
    return {
      "tier": "caution",
      "reason": "Could not reliably classify safety tier; defaulting to caution for safety.",
    }

  if not reason:
    reason = "Classified from risk level and likely consequence severity."

  return {"tier": tier, "reason": reason}


def classify_safety_tier(question: str) -> dict:
    """
    Classify a home repair question into one of three safety tiers.

    TODO — Milestone 1:

    Before writing any code, complete specs/classifier-spec.md. The blank fields
    there are the decisions that drive this implementation — prompt design, tier
    definitions, output format, and edge case handling.

    Your implementation should:
      1. Build a prompt using your tier definitions that asks the LLM to classify
         the question and explain its reasoning
      2. Send a single chat completion request (no tools, no history)
      3. Parse the tier and reason out of the raw response text
      4. Validate the tier against VALID_TIERS; fall back to "caution" if the
         response can't be parsed or the tier isn't recognized
      5. Return {"tier": ..., "reason": ...}

    Returns a dict with:
      - "tier"   : str — one of "safe", "caution", "refuse"
      - "reason" : str — a brief explanation of why this tier was assigned

    The three tiers:
      - "safe"    : routine, low-risk repairs most homeowners can handle safely
      - "caution" : doable with care, but mistakes have real cost or mild risk
      - "refuse"  : high-risk repairs that require a licensed professional —
                    mistakes can cause fire, flooding, injury, or structural damage
    """
    user_prompt = f"Question: {question}\nClassify this question using the rules above."

    try:
      response = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
          {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
          {"role": "user", "content": user_prompt},
        ],
        temperature=0,
      )
      raw_text = response.choices[0].message.content or ""
      return _parse_classifier_output(raw_text)
    except Exception:
      return {
        "tier": "caution",
        "reason": "Classification unavailable due to model or parsing error; defaulting to caution.",
      }
