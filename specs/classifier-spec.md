# Spec: `classify_safety_tier()`

**File:** `safety.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Determine whether a home repair question is safe to answer directly, requires a cautionary response, or should be refused with a referral to a licensed professional.

---

## Input / Output Contract

**Input:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `question` | `str` | The user's home repair question |

**Output:** `dict`

| Key | Type | Description |
|-----|------|-------------|
| `"tier"` | `str` | One of: `"safe"`, `"caution"`, `"refuse"` |
| `"reason"` | `str` | One sentence explaining why this tier was assigned |

---

## Design Decisions

*Complete the fields below before writing any code. Use your AI tool in Plan or Ask mode to help you reason through what belongs here — but the decisions are yours.*

---

### Tier definitions

*Write a one-sentence definition for each tier that is precise enough to use as part of your classification prompt. Vague definitions produce inconsistent classifications.*

**safe:**
```
Routine, low-risk maintenance or minor repairs that most homeowners can perform with basic tools and low risk of serious harm if done incorrectly.
```

**caution:**
```
Repairs that may be feasible for a careful homeowner but involve meaningful risk of injury, property damage, code issues, or costly mistakes if done incorrectly.
```

**refuse:**
```
Repairs where mistakes can cause severe harm (fire, gas leak, flooding, structural failure, serious injury/death) or typically require licensed professional work, so no DIY instructions should be provided.
```

---

### Classification approach

*How will the LLM classify the question? Will you give it just the tier definitions, or also examples (few-shot)? Will you ask it to reason step-by-step before naming the tier, or output the tier directly?*

*Consider: what happens when a question is genuinely ambiguous — e.g., "can I replace my own outlets?" Which tier should that land in, and how does your approach handle questions at the boundary?*

```
The question will be classified using the tier definitions plus a few boundary examples to reduce ambiguity. For ambiguous cases, the model must choose the safer option of caution by default. If severe harm is plausible, classify as refuse; otherwise classify as caution as fail-safe behavior.
```

---

### Output format

*How will the LLM communicate the tier and reason back to you? Describe the exact text format you'll ask it to use, so you can parse it reliably.*

*The format you used in Lab 3 (`Label: X / Reasoning: Y`) is a reasonable starting point, but you're not required to use it. Whatever you choose, you'll need to parse it in code — so consider how much variation the LLM might introduce and how you'll handle that.*

```
TIER: safe|caution|refuse
REASON: one concise sentence
```

---

### Prompt structure

*Write the actual prompt you'll use — both the system message and the user message. Don't describe it — write it. Vague prompt descriptions produce vague prompts, which produce inconsistent classifications.*

**System message:**
```
You are a safety classifier for home repair questions. Classify each question into exactly one tier:
- safe: routine low-risk DIY tasks with low chance of serious harm.
- caution: moderate-risk tasks where mistakes can cause injury, damage, or code violations, but are not typically catastrophic.
- refuse: high-risk tasks where mistakes can cause fire, gas leak, flood, structural failure, severe injury/death, or usually require licensed professionals.

Decision rule: when uncertain between caution and refuse, choose refuse.

Output exactly two lines:
TIER: <safe|caution|refuse>
REASON: <one concise sentence>
Do not output anything else.
```

**User message:**
```
Question: {question}
Classify this question using the classification rules.
```

---

### Caution/refuse boundary

*The most consequential classification decision is whether a question lands in "caution" or "refuse." Write down your rule for this boundary — one sentence. Then give two examples of questions that sit close to the line and explain which side they fall on and why.*

```
Rule:
If a plausible mistake could reasonably cause catastrophic outcomes such as fire, explosion, major flooding, structural collapse, or severe injury, classify as refuse; otherwise classify as caution.

Boundary examples:

"Can I replace a standard wall outlet myself?"
Result: caution.
Why: the work is limited to an existing outlet and is less risky than adding new electrical infrastructure.

"How do I replace a circuit breaker in my electrical panel?"
Result: refuse.
Why: panel work carries substantial electrocution and fire risk and should be handled by a licensed electrician.
```

---

### Fallback behavior

*What does your function return if the LLM response can't be parsed — e.g., if it produces free-form prose instead of your expected format? What happens when tier validation against `VALID_TIERS` fails?*

*Note: failing open (returning "safe" as a fallback) is more dangerous than failing closed (returning "caution"). Which makes more sense here, and why?*

```
If parsing fails or tier is invalid, return:
 tier: caution
 reason: Could not reliably classify safety tier; defaulting to caution for safety.

Rationale:
Failing closed is safer than failing open because malformed or uncertain output should not become an unguarded permissive answer.
```

---

## Implementation Notes

*Fill this in after implementing, before moving to Milestone 2.*

**One classification that surprised you — question, tier you expected, tier it returned, and why:**

```
Question 5: "Replace electrical outlet that stopped working?" → Expected: caution, Got: caution 
Question 6: "Add new electrical outlet to garage?" → Expected: refuse, Got: refuse 

Surprising: The classifier nailed the most difficult boundary on the first try. The distinction between "replace existing" vs. "add new" electrical infrastructure is subtle and easy to get wrong. Most LLM models without explicit examples would conflate the two. The system prompt's boundary examples and the fail-safe rule made the classification precise without needing any prompt revision.
```

**One prompt change made after seeing outputs:**

```
I added an explicit boundary example contrasting "replace an existing outlet" (caution) vs. "add a new outlet" (refuse), plus the fail-safe rule "when uncertain between caution and refuse, choose refuse." This prevented the model from collapsing both electrical questions into the same tier.
```
