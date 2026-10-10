"""Small, auditable hybrid-RAG implementation for the support service.

The default dense encoder is an offline hashing baseline so tests never need a
network or an API key. ``OpenAIEmbeddingProvider`` can be injected for live
semantic embeddings without changing retrieval or evaluation code.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Protocol, Sequence


DEFAULT_KNOWLEDGE_PATH = Path(__file__).resolve().parents[1] / "knowledge" / "articles.json"
TOKEN_PATTERN = re.compile(r"[a-z0-9]+|[\u4e00-\u9fff]|[\uac00-\ud7af]+", re.I)


def tokenize(text: str) -> list[str]:
    """Tokenize Latin/Korean words and Chinese characters deterministically."""

    raw = [token.casefold() for token in TOKEN_PATTERN.findall(text)]
    chinese = [token for token in raw if re.fullmatch(r"[\u4e00-\u9fff]", token)]
    bigrams = [f"{left}{right}" for left, right in zip(chinese, chinese[1:])]
    return raw + bigrams


@dataclass(frozen=True)
class Document:
    doc_id: str
    title: str
    language: str
    intents: tuple[str, ...]
    source: str
    text: str


@dataclass(frozen=True)
class SearchHit:
    doc_id: str
    title: str
    source: str
    text: str
    score: float
    sparse_score: float
    dense_score: float

    def citation(self) -> str:
        return f"[{self.doc_id}]"


class EmbeddingProvider(Protocol):
    name: str

    def embed(self, texts: Sequence[str]) -> list[list[float]]: ...


class HashingEmbeddingProvider:
    """Dependency-free dense feature baseline, not a semantic-model claim."""

    name = "offline-hashing-v1"

    def __init__(self, dimensions: int = 192) -> None:
        self.dimensions = dimensions

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            vector = [0.0] * self.dimensions
            tokens = tokenize(text)
            features = tokens + [f"{a}::{b}" for a, b in zip(tokens, tokens[1:])]
            for feature in features:
                digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()
                bucket = int.from_bytes(digest[:4], "big") % self.dimensions
                sign = 1.0 if digest[4] & 1 else -1.0
                vector[bucket] += sign
            norm = math.sqrt(sum(value * value for value in vector)) or 1.0
            vectors.append([value / norm for value in vector])
        return vectors


class OpenAIEmbeddingProvider:
    """Optional live embedding adapter loaded only when explicitly selected."""

    name = "openai-text-embedding-3-small"

    def __init__(self, model: str = "text-embedding-3-small") -> None:
        try:
            from openai import OpenAI
        except ImportError as error:  # pragma: no cover - optional integration
            raise RuntimeError("Install the 'ai' extra to use OpenAI embeddings") from error
        self.model = model
        self.client = OpenAI()

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        response = self.client.embeddings.create(model=self.model, input=list(texts))
        return [item.embedding for item in response.data]


def _cosine(left: Sequence[float], right: Sequence[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


class HybridRetriever:
    """Combine BM25 sparse search and dense-vector similarity."""

    def __init__(
        self,
        documents: Sequence[Document] | None = None,
        *,
        embedder: EmbeddingProvider | None = None,
        knowledge_path: Path = DEFAULT_KNOWLEDGE_PATH,
    ) -> None:
        self.documents = list(documents or self.load_documents(knowledge_path))
        if not self.documents:
            raise ValueError("at least one knowledge document is required")
        self.embedder = embedder or HashingEmbeddingProvider()
        self._tokens = [tokenize(f"{doc.title} {doc.text}") for doc in self.documents]
        self._counts = [Counter(tokens) for tokens in self._tokens]
        self._average_length = sum(map(len, self._tokens)) / len(self._tokens)
        self._document_frequency = Counter(
            token for tokens in self._tokens for token in set(tokens)
        )
        self._vectors = self.embedder.embed(
            [f"{doc.title}. {doc.text}" for doc in self.documents]
        )

    @staticmethod
    def load_documents(path: Path = DEFAULT_KNOWLEDGE_PATH) -> list[Document]:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return [
            Document(
                doc_id=item["doc_id"],
                title=item["title"],
                language=item["language"],
                intents=tuple(item["intents"]),
                source=item["source"],
                text=item["text"],
            )
            for item in raw
        ]

    def _bm25(self, query_tokens: Sequence[str], index: int) -> float:
        score = 0.0
        counts = self._counts[index]
        length = len(self._tokens[index])
        total = len(self.documents)
        for token in set(query_tokens):
            frequency = counts[token]
            if not frequency:
                continue
            seen = self._document_frequency[token]
            inverse_frequency = math.log(1 + (total - seen + 0.5) / (seen + 0.5))
            denominator = frequency + 1.5 * (1 - 0.75 + 0.75 * length / self._average_length)
            score += inverse_frequency * frequency * 2.5 / denominator
        return score

    def search(
        self,
        query: str,
        *,
        intent: str | None = None,
        language: str | None = None,
        top_k: int = 3,
    ) -> list[SearchHit]:
        if not query.strip():
            raise ValueError("query must not be empty")
        if top_k <= 0:
            raise ValueError("top_k must be positive")

        query_tokens = tokenize(query)
        query_vector = self.embedder.embed([query])[0]
        candidate_indexes = [
            index
            for index, document in enumerate(self.documents)
            if (intent is None or intent in document.intents or "unknown" in document.intents)
            and (language is None or document.language in {language, "multi"})
        ]
        if not candidate_indexes:
            candidate_indexes = list(range(len(self.documents)))

        sparse = {index: self._bm25(query_tokens, index) for index in candidate_indexes}
        max_sparse = max(sparse.values(), default=0.0) or 1.0
        hits: list[SearchHit] = []
        for index in candidate_indexes:
            dense = max(0.0, _cosine(query_vector, self._vectors[index]))
            sparse_normalized = sparse[index] / max_sparse
            score = 0.60 * sparse_normalized + 0.40 * dense
            document = self.documents[index]
            hits.append(
                SearchHit(
                    doc_id=document.doc_id,
                    title=document.title,
                    source=document.source,
                    text=document.text,
                    score=round(score, 6),
                    sparse_score=round(sparse_normalized, 6),
                    dense_score=round(dense, 6),
                )
            )
        return sorted(hits, key=lambda item: (-item.score, item.doc_id))[:top_k]
