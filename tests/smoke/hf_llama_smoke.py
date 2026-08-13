"""Minimal hosted Llama smoke test. Consumes a small amount of HF Inference Providers credit."""
import os
from huggingface_hub import InferenceClient

TOKEN = os.getenv("HF_TOKEN", "").strip()
MODEL = os.getenv("ASSISTANT_MODEL_ID", "meta-llama/Llama-3.1-8B-Instruct")
PROVIDER = os.getenv("ASSISTANT_PROVIDER", "auto")
if not TOKEN:
    raise SystemExit("HF_TOKEN is required for hosted Llama smoke testing")

client = InferenceClient(provider=PROVIDER, token=TOKEN, timeout=45)
try:
    result = client.chat_completion(
        model=MODEL,
        messages=[{"role": "user", "content": "Reply with exactly: CampusPulse Llama API OK"}],
        max_tokens=16,
        temperature=0.0,
    )
    content = str(result.choices[0].message.content or "").strip()
except Exception as exc:
    status = getattr(getattr(exc, "response", None), "status_code", None)
    suffix = f" HTTP {status}" if status else ""
    raise SystemExit(f"Hosted Llama smoke test failed{suffix}. Check token permission, Meta Llama access, provider quota, and network.") from exc
if not content:
    raise SystemExit("Hosted Llama returned an empty response")
print(f"PASS hosted Llama API model={MODEL} provider={PROVIDER}")
print(content[:200])
