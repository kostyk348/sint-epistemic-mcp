from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field, asdict
from typing import Optional

CALIBRATION_DIR = os.path.expanduser("~/.config/opencode/epistemic")
CALIBRATION_FILE = os.path.join(CALIBRATION_DIR, "calibration.json")


@dataclass
class DomainCalibration:
    domain: str
    predictions_count: int = 0
    correct_count: int = 0
    last_updated: float = 0.0

    @property
    def accuracy(self) -> float:
        if self.predictions_count == 0:
            return 0.0
        return self.correct_count / self.predictions_count


class CalibrationStore:
    def __init__(self):
        self._domains: dict[str, DomainCalibration] = {}
        self._load()

    def _load(self):
        if os.path.exists(CALIBRATION_FILE):
            try:
                with open(CALIBRATION_FILE) as f:
                    data = json.load(f)
                for d in data.get("domains", []):
                    dc = DomainCalibration(**d)
                    self._domains[dc.domain] = dc
            except Exception:
                pass

    def _save(self):
        os.makedirs(CALIBRATION_DIR, exist_ok=True)
        data = {
            "domains": [asdict(dc) for dc in self._domains.values()]
        }
        with open(CALIBRATION_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def record_prediction(self, domain: str, correct: bool):
        if domain not in self._domains:
            self._domains[domain] = DomainCalibration(domain=domain)
        dc = self._domains[domain]
        dc.predictions_count += 1
        if correct:
            dc.correct_count += 1
        dc.last_updated = time.time()
        self._save()

    def get_calibration(self, domain: str) -> Optional[DomainCalibration]:
        return self._domains.get(domain)

    def all_calibrations(self) -> dict[str, DomainCalibration]:
        return dict(self._domains)
