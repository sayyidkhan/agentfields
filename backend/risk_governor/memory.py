from __future__ import annotations

import json
import math
import re
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from typing import Any, Optional

import numpy as np


_TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+")


def _json_dumps(obj: Any) -> str:
    return json.dumps(obj, separators=(",", ":"), sort_keys=True, default=str)


def _json_loads(s: str) -> Any:
    return json.loads(s)


def embed_text_deterministic(text: str, dim: int = 256) -> list[float]:
    """
    Deterministic embedding: feature hashing + signed counts + L2 normalization.

    This is intentionally non-LLM and stable across runs/machines.
    """
    vec = np.zeros(dim, dtype=np.float32)
    tokens = _TOKEN_RE.findall(text.lower())
    if not tokens:
        return vec.tolist()

    for tok in tokens:
        h = sha256(tok.encode("utf-8")).digest()
        idx = int.from_bytes(h[:4], "little") % dim
        sign = -1.0 if (h[4] & 1) else 1.0
        vec[idx] += sign

    norm = float(np.linalg.norm(vec))
    if norm > 0:
        vec = vec / norm
    return vec.astype(float).tolist()


def cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = 0.0
    na = 0.0
    nb = 0.0
    for i in range(len(a)):
        ai = float(a[i])
        bi = float(b[i])
        dot += ai * bi
        na += ai * ai
        nb += bi * bi
    if na <= 0 or nb <= 0:
        return 0.0
    return dot / (math.sqrt(na) * math.sqrt(nb))


@dataclass
class MemoryRead:
    scope: str
    key: str
    hit: bool


@dataclass
class MemoryWrite:
    scope: str
    key_or_id: str
    kind: str  # kv|vector


class SqliteMemory:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    # ---- KV ----
    def get(self, scope: str, key: str) -> Optional[dict[str, Any]]:
        row = self.conn.execute(
            "SELECT v_json FROM memory_kv WHERE scope=? AND k=?",
            (scope, key),
        ).fetchone()
        if row is None:
            return None
        return _json_loads(row["v_json"])

    def set(self, scope: str, key: str, value: dict[str, Any]) -> None:
        now = datetime.utcnow().isoformat()
        self.conn.execute(
            """
            INSERT INTO memory_kv(scope, k, v_json, updated_at)
            VALUES(?,?,?,?)
            ON CONFLICT(scope,k) DO UPDATE SET
              v_json=excluded.v_json,
              updated_at=excluded.updated_at
            """,
            (scope, key, _json_dumps(value), now),
        )

    # ---- Vector ----
    def add_vector(
        self,
        scope: str,
        text: str,
        *,
        metadata: Optional[dict[str, Any]] = None,
        vector_id: Optional[str] = None,
    ) -> str:
        vid = vector_id or f"vec_{uuid.uuid4().hex}"
        emb = embed_text_deterministic(text)
        now = datetime.utcnow().isoformat()
        self.conn.execute(
            """
            INSERT INTO memory_vectors(vector_id, scope, text, embedding_json, metadata_json, created_at)
            VALUES(?,?,?,?,?,?)
            """,
            (vid, scope, text, _json_dumps(emb), _json_dumps(metadata or {}), now),
        )
        return vid

    def search(
        self,
        scope: str,
        query: str,
        *,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        q = embed_text_deterministic(query)
        rows = self.conn.execute(
            "SELECT vector_id, text, embedding_json, metadata_json, created_at FROM memory_vectors WHERE scope=?",
            (scope,),
        ).fetchall()
        scored: list[tuple[float, sqlite3.Row]] = []
        for r in rows:
            emb = _json_loads(r["embedding_json"])
            scored.append((cosine(q, emb), r))
        scored.sort(key=lambda x: x[0], reverse=True)
        out = []
        for score, r in scored[: max(0, top_k)]:
            out.append(
                {
                    "vector_id": r["vector_id"],
                    "score": float(score),
                    "text": r["text"],
                    "metadata": _json_loads(r["metadata_json"]),
                    "created_at": r["created_at"],
                }
            )
        return out


# -----------------------------
# Convenience functions (explicit deliverable surface)
# -----------------------------


def memory_get(memory: SqliteMemory, scope: str, key: str) -> Optional[dict[str, Any]]:
    return memory.get(scope, key)


def memory_set(memory: SqliteMemory, scope: str, key: str, value: dict[str, Any]) -> None:
    memory.set(scope, key, value)


def memory_add_vector(
    memory: SqliteMemory,
    scope: str,
    text: str,
    *,
    metadata: Optional[dict[str, Any]] = None,
    vector_id: Optional[str] = None,
) -> str:
    return memory.add_vector(scope, text, metadata=metadata, vector_id=vector_id)


def memory_search(
    memory: SqliteMemory,
    scope: str,
    query: str,
    *,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    return memory.search(scope, query, top_k=top_k)

