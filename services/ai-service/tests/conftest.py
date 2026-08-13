import os

os.environ["AI_BACKEND"] = "deterministic"
os.environ["AI_REQUIRE_LLM"] = "false"
os.environ.pop("HF_TOKEN", None)
