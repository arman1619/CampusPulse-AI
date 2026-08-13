from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
import json
import math
from pathlib import Path
import re

from .config import settings

_TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)


@dataclass(frozen=True)
class KnowledgeChunk:
    id: str
    title: str
    content: str
    audience: tuple[str, ...]


def _tokens(text: str) -> list[str]:
    return [token.lower() for token in _TOKEN_RE.findall(text)]


class KnowledgeRetriever:
    """Small dependency-free TF-IDF/cosine retriever for the bundled knowledge corpus.

    This is retrieval logic, not a locally hosted language model. Keeping it in pure Python
    avoids shipping NumPy/SciPy/scikit-learn into the hosted-LLM assistant image.
    """

    def __init__(self, path: str):
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        self.chunks = [
            KnowledgeChunk(item["id"], item["title"], item["content"], tuple(item.get("audience", ["ALL"])))
            for item in raw
        ]
        self._doc_counts = [Counter(_tokens(f"{chunk.title} {chunk.content}")) for chunk in self.chunks]
        document_frequency: Counter[str] = Counter()
        for counts in self._doc_counts:
            document_frequency.update(counts.keys())
        n_docs = max(len(self.chunks), 1)
        self._idf = {term: math.log((n_docs + 1) / (df + 1)) + 1.0 for term, df in document_frequency.items()}
        self._doc_vectors = [self._vectorize(counts) for counts in self._doc_counts]
        self._doc_norms = [self._norm(vector) for vector in self._doc_vectors]

    def _vectorize(self, counts: Counter[str]) -> dict[str, float]:
        return {
            term: (1.0 + math.log(count)) * self._idf.get(term, 1.0)
            for term, count in counts.items()
            if count > 0
        }

    @staticmethod
    def _norm(vector: dict[str, float]) -> float:
        return math.sqrt(sum(value * value for value in vector.values())) or 1.0

    def retrieve(self, query: str, role: str, top_k: int = 3) -> list[dict]:
        query_counts = Counter(_tokens(query))
        query_vector = self._vectorize(query_counts)
        query_norm = self._norm(query_vector)
        scored: list[tuple[float, int]] = []
        for idx, document_vector in enumerate(self._doc_vectors):
            dot = sum(weight * document_vector.get(term, 0.0) for term, weight in query_vector.items())
            score = dot / (query_norm * self._doc_norms[idx]) if query_vector else 0.0
            scored.append((score, idx))
        scored.sort(reverse=True)

        results: list[dict] = []
        for score, idx in scored:
            chunk = self.chunks[idx]
            if "ALL" not in chunk.audience and role not in chunk.audience:
                continue
            if score < 0.02:
                continue
            results.append({"id": chunk.id, "title": chunk.title, "content": chunk.content, "score": round(score, 4)})
            if len(results) >= top_k:
                break
        return results


@lru_cache(maxsize=1)
def get_retriever() -> KnowledgeRetriever:
    return KnowledgeRetriever(settings.knowledge_path)
