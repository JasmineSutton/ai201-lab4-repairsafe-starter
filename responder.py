from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL

_client = Groq(api_key=GROQ_API_KEY)


SAFE_SYSTEM_PROMPT = """You are a practical home repair assistant for low-risk tasks.

Provide clear, actionable, step-by-step help.
Use plain language and include recommended tools/materials when useful.
Add brief safety reminders, but keep the response focused on completing the task.
"""


CAUTION_SYSTEM_PROMPT = """You are a home repair assistant for moderate-risk tasks.

Give high-level guidance with strong safety framing.
Include key precautions, common failure points, and when to stop and call a licensed professional.
Avoid overconfident instructions for steps that involve electrical, gas, structural, or major plumbing risk.
If uncertainty exists, prioritize safer alternatives and professional evaluation.
"""


REFUSE_SYSTEM_PROMPT = """You are a safety-first assistant for high-risk home repair requests.

Do NOT provide any how-to instructions, procedural steps, tool lists, or workaround guidance.
Do NOT provide partial DIY advice.
Explain briefly why the task is dangerous, list immediate safety actions if relevant, and strongly recommend a licensed professional.
You may suggest what information to gather before contacting a professional (for example symptoms, photos, model numbers), but no repair steps.
"""


def generate_safe_response(question: str, tier: str) -> str:
    """
    Generate a response to a home repair question, calibrated to its safety tier.

    TODO — Milestone 2:

    Before writing any code, complete specs/responder-spec.md. The most important
    fields are the three system prompts — one per tier. Write them out fully before
    generating any code; a vague description produces a vague prompt.

    `tier` is one of "safe", "caution", or "refuse" — returned by classify_safety_tier().

    Your implementation should use a different system prompt for each tier:
      - "safe"    : answer helpfully and directly; the user can proceed
      - "caution" : answer but include clear safety warnings and recommend
                    professional review for anything they're unsure about
      - "refuse"  : do NOT provide how-to instructions; explain why the repair
                    is dangerous and strongly recommend a licensed professional

    The refuse case is the hardest to get right. An LLM that says "you should hire
    a professional, but here's how to do it anyway" has defeated the entire purpose
    of the safety layer. Your system prompt needs to be explicit enough to prevent
    that — see specs/responder-spec.md for the design decision field on grounding.

    If tier is unrecognized (e.g., "unknown" from an unimplemented classifier),
    treat it as "caution" to fail safe rather than fail open.

    Return the response as a plain string.
    """
    normalized_tier = (tier or "").strip().lower()

    system_prompt_by_tier = {
      "safe": SAFE_SYSTEM_PROMPT,
      "caution": CAUTION_SYSTEM_PROMPT,
      "refuse": REFUSE_SYSTEM_PROMPT,
    }

    if normalized_tier not in system_prompt_by_tier:
      normalized_tier = "caution"

    try:
      response = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
          {"role": "system", "content": system_prompt_by_tier[normalized_tier]},
          {"role": "user", "content": question},
        ],
        temperature=0.2,
      )
      return (response.choices[0].message.content or "").strip()
    except Exception:
      if normalized_tier == "refuse":
        return (
          "This repair appears high-risk and I cannot provide DIY instructions. "
          "Please contact a licensed professional for a safe assessment."
        )

      return (
        "I could not generate a full response right now. "
        "Please proceed cautiously and consult a licensed professional if anything is unclear."
      )
