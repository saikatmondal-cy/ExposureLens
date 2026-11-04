"""
ExposureLens Semantic Property-Level Exposure Analyzer.

Formulation:
Unifies BOLA (Object-Level Authorization - OWASP API1:2023) with
BOPLA (Object Property-Level Authorization - OWASP API3:2023).

Computes the formal Set-Theoretic Property Exposure Delta:
    Delta_leak = P_delivered \\ P_authorized

Quantifies the unauthorized disclosure of granular semantic attributes:
- PII_DIRECT (Shipping address, contact coordinates, residential details)
- FINANCIAL_METADATA (Card last-4 tokens, transaction amounts, payment methods)
- CONFIDENTIAL_PHI (Diagnostic pathology reports, biopsy findings, executive salary)
"""

import json
from typing import Any, Dict, List, Set
from backend.database import SessionLocal
from backend.models import ExposureRecord, Order, Document


# Formal Semantic Property Weight Registry
PROPERTY_WEIGHTS: Dict[str, Dict[str, Any]] = {
    "shipping_address": {"category": "PII_DIRECT", "weight": 25.0, "risk_label": "Physical Location & Home Address"},
    "address": {"category": "PII_DIRECT", "weight": 25.0, "risk_label": "Personal Residence"},
    "phone": {"category": "PII_DIRECT", "weight": 20.0, "risk_label": "Direct Contact Identifier"},
    "email": {"category": "PII_DIRECT", "weight": 15.0, "risk_label": "Digital Identity"},
    "payment_last4": {"category": "FINANCIAL_METADATA", "weight": 30.0, "risk_label": "Payment Card Token Fragment"},
    "amount": {"category": "FINANCIAL_METADATA", "weight": 20.0, "risk_label": "Commercial Transaction Value"},
    "content_summary": {"category": "CONFIDENTIAL_PHI", "weight": 45.0, "risk_label": "Protected Health & Executive Records"},
    "title": {"category": "INTERNAL_METADATA", "weight": 15.0, "risk_label": "Document Classification Subject"},
    "product": {"category": "COMMERCIAL_SPEC", "weight": 10.0, "risk_label": "Procured Asset Description"}
}

# Baseline properties an external non-owner might legitimately observe (public metadata)
AUTHORIZED_NON_OWNER_BASELINE: Set[str] = {"order_id", "status", "document_id", "category"}


def analyze_semantic_property_exposure(exposure: Dict[str, Any]) -> Dict[str, Any]:
    """Compute field-level semantic exposure delta for an individual exposure incident."""
    exposed_fields = exposure.get("exposed_fields", [])
    if isinstance(exposed_fields, str):
        exposed_fields = json.loads(exposed_fields)

    delivered_set = set(exposed_fields)
    unauthorized_delta = delivered_set - AUTHORIZED_NON_OWNER_BASELINE

    categorized_leak = []
    total_sev_score = 0.0

    for prop in sorted(unauthorized_delta):
        meta = PROPERTY_WEIGHTS.get(prop, {"category": "GENERAL_ATTRIBUTE", "weight": 10.0, "risk_label": "Unclassified Attribute"})
        weight = meta["weight"]
        total_sev_score += weight
        categorized_leak.append({
            "property_name": prop,
            "category": meta["category"],
            "weight": weight,
            "description": meta["risk_label"]
        })

    # Normalized Semantic Exposure Value (0 to 100)
    normalized_sev = min(100.0, round(total_sev_score, 1))

    return {
        "exposure_id": exposure.get("exposure_id"),
        "resource_type": exposure.get("resource_type"),
        "resource_id": exposure.get("resource_id"),
        "total_properties_delivered": len(delivered_set),
        "unauthorized_delta_count": len(unauthorized_delta),
        "unauthorized_delta_fields": list(unauthorized_delta),
        "semantic_breakdown": categorized_leak,
        "semantic_exposure_value": normalized_sev
    }


def compute_macro_semantic_exposure_matrix() -> Dict[str, Any]:
    """Aggregate semantic exposure deltas across all reconstructed exposures in the database."""
    from detector.exposure_reconstructor import get_all_exposures
    exposures = get_all_exposures()

    if not exposures:
        return {
            "total_incidents": 0,
            "total_leaked_properties_count": 0,
            "average_sev": 0.0,
            "category_distribution": {},
            "detailed_incident_deltas": []
        }

    deltas = [analyze_semantic_property_exposure(e) for e in exposures]
    category_counts: Dict[str, int] = {}
    total_properties_leaked = 0

    for d in deltas:
        total_properties_leaked += d["unauthorized_delta_count"]
        for item in d["semantic_breakdown"]:
            cat = item["category"]
            category_counts[cat] = category_counts.get(cat, 0) + 1

    avg_sev = round(sum(d["semantic_exposure_value"] for d in deltas) / len(deltas), 1)

    return {
        "total_incidents": len(exposures),
        "total_leaked_properties_count": total_properties_leaked,
        "average_sev": avg_sev,
        "category_distribution": category_counts,
        "detailed_incident_deltas": deltas
    }


if __name__ == "__main__":
    matrix = compute_macro_semantic_exposure_matrix()
    print("\n=== Semantic Property Exposure Analysis ===")
    print("Total Incidents:", matrix["total_incidents"])
    print("Total Leaked Properties:", matrix["total_leaked_properties_count"])
    print("Average Semantic Exposure Value (SEV):", matrix["average_sev"])
    print("Category Distribution:", matrix["category_distribution"])
