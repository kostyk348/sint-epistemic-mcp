from enum import Enum
from typing import Literal


StatusLiteral = Literal["VERIFIED", "INFERRED", "ASSUMED", "UNCERTAIN"]


class EpistemicStatus(str, Enum):
    VERIFIED = "VERIFIED"
    INFERRED = "INFERRED"
    ASSUMED = "ASSUMED"
    UNCERTAIN = "UNCERTAIN"

    @classmethod
    def valid(cls) -> list[str]:
        return [s.value for s in cls]

    @classmethod
    def validate(cls, s: str) -> bool:
        return s in cls.valid()
