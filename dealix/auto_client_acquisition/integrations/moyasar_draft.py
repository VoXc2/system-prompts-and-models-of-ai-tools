"""Moyasar payment resource draft — halalas validation only, no API calls."""

from __future__ import annotations

from typing import Any

# SAR minor units per Moyasar docs (amount in halalas / smallest currency unit).


def build_moyasar_payment_draft(params: dict[str, Any]) -> dict[str, Any]:
    """
    Validates ``amount`` as integer halalas (>= 100 typical minimum for tests).
    Returns a create-payment shaped dict without calling Moyasar.
    """
    raw = params.get("amount_halalas", params.get("amount"))
    errors: list[str] = []
    amount: int | None = None
    try:
        if raw is None:
            errors.append("amount_halalas_required")
        else:
            amount = int(raw)
            if amount < 1:
                errors.append("amount_must_be_positive_integer_halalas")
    except (TypeError, ValueError):
        errors.append("amount_must_be_integer_halalas")
        amount = None

    if errors:
        return {"approval_required": True, "valid": False, "errors": errors, "payload": None, "payment_link_draft": None}

    currency = str(params.get("currency") or "SAR").upper()
    invoice_ref = str(params.get("invoice_reference") or params.get("invoice_id") or f"INV-DEMO-{amount}")
    # Shape-only checkout URL — replace base with real merchant page when integrating.
    base = str(params.get("payment_link_base") or "https://api.moyasar.com/v1/payments")
    payment_link_draft = f"{base}?amount={amount}&currency={currency}&description={invoice_ref}"

    payload: dict[str, Any] = {
        "amount": amount,
        "currency": currency,
        "source": params.get("source") if isinstance(params.get("source"), dict) else {"type": "creditcard"},
        "description": str(params.get("description_ar") or params.get("description") or "Dealix draft"),
        "metadata": {"invoice_reference": invoice_ref},
    }
    return {
        "approval_required": True,
        "valid": True,
        "errors": [],
        "payload": payload,
        "payment_link_draft": payment_link_draft,
        "invoice_reference": invoice_ref,
        "note_ar": "مسودة تحقق فقط — لا يُنشأ دفع عبر Moyasar في MVP؛ الرابط للعرض الشكلي فقط.",
    }
