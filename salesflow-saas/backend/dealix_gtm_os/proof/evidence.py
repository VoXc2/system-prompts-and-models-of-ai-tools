"""Evidence tracking — marks claims as VERIFIED, INFERRED, or UNVERIFIED."""
from enum import Enum

class EvidenceLevel(str, Enum):
    VERIFIED = "verified"
    INFERRED = "inferred"
    UNVERIFIED = "unverified"
    LOW_CONFIDENCE = "low_confidence"

def assess_evidence(claim: str, sources: list[str], confidence: float) -> dict:
    if sources and confidence >= 0.8:
        level = EvidenceLevel.VERIFIED
    elif sources and confidence >= 0.5:
        level = EvidenceLevel.INFERRED
    elif confidence >= 0.3:
        level = EvidenceLevel.LOW_CONFIDENCE
    else:
        level = EvidenceLevel.UNVERIFIED
    return {"claim": claim, "level": level.value, "sources": sources, "confidence": confidence, "source_count": len(sources)}
