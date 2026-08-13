"""One real hosted-Llama triage smoke request. Consumes a small amount of HF credit."""
import os
import json
from huggingface_hub import InferenceClient

TOKEN = os.getenv("HF_TOKEN", "").strip()
MODEL = os.getenv("AI_MODEL_ID", "meta-llama/Llama-3.1-8B-Instruct")
PROVIDER = os.getenv("AI_PROVIDER", "auto")
if not TOKEN:
    raise SystemExit("HF_TOKEN is required for hosted Llama triage smoke testing")

client = InferenceClient(provider=PROVIDER, token=TOKEN, timeout=45)
prompt = (
    'Return ONLY JSON: {"sentiment":{"label":"NEGATIVE","confidence":0.9},'
    '"category":{"label":"IT","confidence":0.9},"priority":{"label":"MEDIUM","confidence":0.8}} '
    'for this complaint: Library Wi-Fi disconnects every few minutes.'
)
try:
    result = client.chat_completion(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
        temperature=0.0,
    )
    content = str(result.choices[0].message.content or "").strip()
    start, end = content.find("{"), content.rfind("}")
    parsed = json.loads(content[start:end+1]) if start >= 0 and end > start else None
except Exception as exc:
    status = getattr(getattr(exc, "response", None), "status_code", None)
    suffix = f" HTTP {status}" if status else ""
    raise SystemExit(f"Hosted Llama triage smoke failed{suffix}. Check token permission, Meta model access, quota, and network.") from exc
if not parsed or not all(k in parsed for k in ("sentiment", "category", "priority")):
    raise SystemExit("Hosted Llama triage smoke returned an invalid structure")
print(f"PASS hosted Llama triage API model={MODEL} provider={PROVIDER}")
