"""Data Plane — Data quality gates (Great Expectations style)."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class QualityExpectation(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    column: str | None = None
    expectation_type: str  # "not_null", "unique", "in_set", "range", "regex", "custom"
    parameters: dict[str, Any] = Field(default_factory=dict)


class QualityCheckResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    expectation_name: str
    passed: bool
    observed_value: Any = None
    details: str = ""


class QualityReport(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    report_id: str
    dataset: str
    checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    total_expectations: int = 0
    passed: int = 0
    failed: int = 0
    results: list[QualityCheckResult] = Field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        return self.passed / self.total_expectations if self.total_expectations > 0 else 0.0


class DataQualityGate:
    """Validates data against expectations before pipeline progression."""
    
    def __init__(self):
        self._expectations: dict[str, list[QualityExpectation]] = {}
    
    def register_expectations(self, dataset: str, expectations: list[QualityExpectation]) -> None:
        self._expectations[dataset] = expectations
    
    def validate(self, dataset: str, records: list[dict[str, Any]], report_id: str = "") -> QualityReport:
        import uuid as _uuid
        expectations = self._expectations.get(dataset, [])
        results: list[QualityCheckResult] = []
        
        for exp in expectations:
            passed = True
            details = ""
            
            if exp.expectation_type == "not_null":
                nulls = sum(1 for r in records if r.get(exp.column) is None)
                passed = nulls == 0
                details = f"{nulls} null values found" if not passed else "OK"
            
            elif exp.expectation_type == "unique":
                values = [r.get(exp.column) for r in records]
                dupes = len(values) - len(set(values))
                passed = dupes == 0
                details = f"{dupes} duplicate values" if not passed else "OK"
            
            elif exp.expectation_type == "in_set":
                allowed = set(exp.parameters.get("values", []))
                violations = sum(1 for r in records if r.get(exp.column) not in allowed)
                passed = violations == 0
                details = f"{violations} values not in allowed set" if not passed else "OK"
            
            elif exp.expectation_type == "range":
                min_val = exp.parameters.get("min", float("-inf"))
                max_val = exp.parameters.get("max", float("inf"))
                violations = sum(
                    1 for r in records
                    if r.get(exp.column) is not None and not (min_val <= r[exp.column] <= max_val)
                )
                passed = violations == 0
                details = f"{violations} values out of range [{min_val}, {max_val}]" if not passed else "OK"
            
            results.append(QualityCheckResult(
                expectation_name=exp.name,
                passed=passed,
                details=details,
            ))
        
        return QualityReport(
            report_id=report_id or str(_uuid.uuid4()),
            dataset=dataset,
            total_expectations=len(results),
            passed=sum(1 for r in results if r.passed),
            failed=sum(1 for r in results if not r.passed),
            results=results,
        )


data_quality_gate = DataQualityGate()
