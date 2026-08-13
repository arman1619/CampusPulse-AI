import re
from dataclasses import dataclass


@dataclass(frozen=True)
class GuardrailResult:
    blocked: bool = False
    direct_answer: str | None = None
    safety_notice: str | None = None


EMERGENCY_PATTERNS = [
    r"\b(active )?fire\b", r"\bgas leak\b", r"\bweapon\b", r"\bshooting\b",
    r"\bviolence\b", r"\bviolent (incident|attack)\b", r"\bstructural collapse\b", r"\bsevere injury\b", r"\bexposed (electrical )?wire",
]
PROMPT_INJECTION_PATTERNS = [
    r"\b(ignore|disregard|override)\b.{0,60}\b(instructions|rules|system)\b",
    r"\b(reveal|show|print|dump|expose)\b.{0,60}\b(system prompt|secret|jwt|password|credential|environment variable|configuration)\b",
    r"\bact as (the )?system\b",
    r"\bhidden configuration\b",
]


def evaluate_user_message(message: str) -> GuardrailResult:
    lowered = message.lower()
    if any(re.search(pattern, lowered) for pattern in PROMPT_INJECTION_PATTERNS):
        return GuardrailResult(
            blocked=True,
            direct_answer="I can help with CampusPulse and campus issue-management questions, but I cannot reveal system instructions, credentials, tokens, or other protected configuration.",
        )
    if any(re.search(pattern, lowered) for pattern in EMERGENCY_PATTERNS):
        return GuardrailResult(
            direct_answer=(
                "This may describe an immediate safety hazard. Move away from the danger, warn nearby people if it is safe to do so, "
                "and contact campus security/emergency staff or local emergency services. You can also record the issue in CampusPulse, "
                "but the chatbot and issue-management workflow are not substitutes for emergency response."
            ),
            safety_notice="Potential immediate safety hazard detected; human emergency response takes priority over chatbot assistance.",
        )
    return GuardrailResult()
