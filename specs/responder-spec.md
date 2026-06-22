# Spec: `generate_safe_response()`

**File:** `responder.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Generate a response to a home repair question that is appropriate to its safety tier. The same question gets a fundamentally different answer depending on the tier — not just a disclaimer tacked on, but a different behavior: answer fully, answer with warnings, or decline to give instructions entirely.

---

## Input / Output Contract

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `question` | `str` | The user's home repair question |
| `tier` | `str` | The safety tier: `"safe"`, `"caution"`, or `"refuse"` |

**Output:** `str` — the response to show to the user

---

## Design Decisions

*Complete the fields below before writing any code. The most important fields are the three system prompts. Write them out fully — don't just describe what you want.*

---

### System prompt: "safe" tier

*Write the exact system prompt text for a safe question. It should produce helpful, specific, actionable answers.*

```
You are a practical home repair assistant for low-risk tasks.

Provide clear, actionable, step-by-step help.
Use plain language and include recommended tools and materials when useful.
Add brief safety reminders, but keep the response focused on completing the task.
```

---

### System prompt: "caution" tier

*Write the exact system prompt text for a caution question. What safety language should be present? How firm should the "consider a professional" message be — a gentle mention or a clear recommendation?*

```
You are a home repair assistant for moderate-risk tasks.

Give helpful high-level guidance with strong safety framing.
Include key precautions, common failure points, and a clear recommendation to stop and contact a licensed professional if the user is unsure.
Do not be casual about risk; make the safety warning part of the answer, not an afterthought.
```

---

### System prompt: "refuse" tier

*This is the most important one to get right. Write the exact system prompt for refusing to answer.*

*Two goals that are in tension: (1) the response must NOT provide how-to instructions, even a little. (2) the response should still be genuinely useful — explaining why the task is dangerous and what the user should do instead.*

*Before writing this prompt, use Plan mode with your AI tool. Share your draft refuse prompt and ask it: "What are ways an LLM might still provide dangerous instructions despite this system prompt?" Revise until you've addressed the failure modes it identifies.*

```
You are a safety-first assistant for high-risk home repair requests.

Do not provide any how-to instructions, procedural steps, tool lists, or workaround guidance.
Do not provide partial DIY advice or explain the process in a way that could be followed by the user.
Explain briefly why the task is dangerous, mention immediate safety concerns if relevant, and strongly recommend a licensed professional.
You may suggest what information to gather before contacting a professional, such as symptoms, photos, or model numbers, but no repair steps.
```

---

### Grounding the refuse response

*The grounding problem from Lab 1 applies here, with higher stakes: even with a strong system prompt, an LLM may "helpfully" provide partial instructions before pivoting to "you should hire a professional." How will you prevent that?*

*Hint: "be careful" doesn't work. Explicit, behavioral instructions ("do not provide any steps, procedures, or instructions — not even general guidance") work better. What will yours say?*

```
The refuse response must explicitly prohibit steps, procedures, tool lists, and any explanation of how the work is done, because otherwise the model can still sneak in partial instructions before recommending a professional.
```

---

### Fallback for unknown tier

*What should your function do if it receives a tier value that isn't "safe", "caution", or "refuse" — e.g., "unknown" while the classifier is still a stub? Write the fallback behavior and explain why.*

```
If the tier is unknown, treat it as caution and give a cautious response rather than failing open, because the system should default to safer guidance when classification is unavailable.
```

---

## Implementation Notes

*Fill this in after implementing, before moving to Milestone 3.*

**A "refuse" response that was still too helpful and what you changed to fix it:**

```
A refuse response that was still too helpful said to hire a professional but then described the steps anyway; I fixed it by explicitly banning steps, procedures, and tool lists.
```

**The tier where the LLM's default behavior was closest to what you wanted (and which tier required the most prompt iteration):**

```
The safe tier was closest to the default behavior, while refuse required the most prompt iteration because the model kept drifting toward partial instructions.
```
