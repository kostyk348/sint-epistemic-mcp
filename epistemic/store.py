from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Optional

from .status import EpistemicStatus

CLAIMS_DIR = os.path.expanduser("~/.config/opencode/epistemic")
CLAIMS_FILE = os.path.join(CLAIMS_DIR, "claims.json")


@dataclass
class Claim:
    id: str
    claim: str
    status: str
    confidence: float
    source: str
    domain: str
    timestamp: float
    outcome: Optional[bool] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> Claim:
        return cls(**d)


class ClaimStore:
    def __init__(self):
        self._claims: dict[str, Claim] = {}
        self._load()

    def _load(self):
        if os.path.exists(CLAIMS_FILE):
            try:
                with open(CLAIMS_FILE) as f:
                    data = json.load(f)
                for c in data.get("claims", []):
                    claim = Claim.from_dict(c)
                    self._claims[claim.id] = claim
            except Exception:
                pass

    def _save(self):
        os.makedirs(CLAIMS_DIR, exist_ok=True)
        data = {
            "claims": [c.to_dict() for c in self._claims.values()]
        }
        with open(CLAIMS_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def add(self, claim_text: str, status: str, confidence: float,
            source: str, domain: str) -> Claim:
        claim = Claim(
            id=str(uuid.uuid4()),
            claim=claim_text,
            status=status,
            confidence=confidence,
            source=source,
            domain=domain,
            timestamp=time.time(),
        )
        self._claims[claim.id] = claim
        self._save()
        return claim

    def get(self, claim_id: str) -> Optional[Claim]:
        return self._claims.get(claim_id)

    def search(self, query: str = "", domain: str = "") -> list[Claim]:
        results = list(self._claims.values())
        if query:
            q = query.lower()
            results = [c for c in results if q in c.claim.lower()]
        if domain:
            results = [c for c in results if c.domain == domain]
        return sorted(results, key=lambda c: c.timestamp, reverse=True)

    def by_domain(self, domain: str) -> list[Claim]:
        return [c for c in self._claims.values() if c.domain == domain]

    def all(self) -> list[Claim]:
        return list(self._claims.values())

    def domains(self) -> set[str]:
        return {c.domain for c in self._claims.values()}

    def record_outcome(self, claim_id: str, correct: bool) -> Optional[Claim]:
        claim = self._claims.get(claim_id)
        if claim is None:
            return None
        claim.outcome = correct
        self._save()
        return claim
