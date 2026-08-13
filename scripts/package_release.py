from pathlib import Path
import zipfile

root = Path(__file__).resolve().parents[1]
dist = root / "dist"
dist.mkdir(exist_ok=True)
out = dist / "CampusPulse-AI-HD-Plus-HF-Llama-API-No-Local-AI-AWS-Ready.zip"
out.unlink(missing_ok=True)
exclude_parts = {".env", ".git", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache", ".terraform", "coverage", "htmlcov", "dist"}
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if any(part in exclude_parts for part in rel.parts):
            continue
        if path.suffix in {".pyc", ".pem", ".key"} or rel.name.startswith(".coverage") or rel.name.endswith(".db"):
            continue
        if path.is_file():
            archive.write(path, Path("CAMPUSPULSE-AI") / rel)
    manifest = dist / "RELEASE_MANIFEST.txt"
    if manifest.exists():
        archive.write(manifest, Path("CAMPUSPULSE-AI/dist/RELEASE_MANIFEST.txt"))
print(out)
