"""Claim validator — blocks fake or overclaimed statements."""
FORBIDDEN = ["مضمون", "guaranteed", "100%", "أفضل في السوق", "بدون منافس", "SOC 2", "ISO 27001", "bank-grade", "military-grade", "zero risk", "ربح مضمون", "دخل مضمون", "نتائج مضمونة"]

def validate_claim(text: str) -> dict:
    violations = [f for f in FORBIDDEN if f.lower() in text.lower()]
    return {"valid": len(violations) == 0, "violations": violations, "severity": "critical" if violations else "none"}
