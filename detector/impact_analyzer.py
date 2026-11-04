"""
ExposureLens Transparent Risk & Impact Assessment Engine.

Scoring Methodology:
The risk score (0-100) measures the security and business consequence of a confirmed
BOLA exposure event based on four explainable, deterministic pillars:

1. Base Data Sensitivity (S_base):
   - CRITICAL (PHI, Medical, Executive Comp, Tax Assets): 40 pts
   - HIGH (PII, Financial Orders, Home Address, Card Last4): 30 pts
   - MEDIUM (Commercial orders, non-sensitive specifications): 20 pts
   - LOW (Telemetry, public metadata): 10 pts

2. Multi-Tenant Isolation Breach Multiplier (M_tenant):
   - Cross-Tenant Breach: 1.5x multiplier (Violates strict logical data boundary)
   - Intra-Tenant Breach: 1.0x multiplier (Internal authorization failure)

3. Sensitive Attribute Exposure Weight (W_attr):
   - Checks presence of direct privacy/financial vectors (payment metadata, full address, diagnostic text)
   - Adds 10-15 pts depending on sensitive fields exposed.

4. Attack Velocity & Scope Penalty (P_scope):
   - Systemic enumeration / mass scraping pattern: +15 pts

Formula:
   CalculatedScore = min(100.0, round((S_base * M_tenant) + W_attr + P_scope, 1))

Severity Mapping:
   - CRITICAL: >= 80.0
   - HIGH:     60.0 - 79.9
   - MEDIUM:   35.0 - 59.9
   - LOW:      < 35.0
"""

from typing import Any, Dict, List


def calculate_exposure_risk(
    sensitivity: str,
    is_cross_tenant: bool,
    exposed_fields: List[str],
    is_enumeration: bool
) -> Dict[str, Any]:
    """Compute transparent risk score and provide step-by-step breakdown."""

    # 1. Base sensitivity
    sens_upper = (sensitivity or "MEDIUM").upper()
    sensitivity_weights = {
        "CRITICAL": 40.0,
        "HIGH": 30.0,
        "MEDIUM": 20.0,
        "LOW": 10.0
    }
    base_score = sensitivity_weights.get(sens_upper, 20.0)

    # 2. Cross-tenant multiplier
    tenant_multiplier = 1.5 if is_cross_tenant else 1.0
    tenant_weighted_base = base_score * tenant_multiplier

    # 3. Attribute penalty
    high_risk_keys = {"payment_last4", "shipping_address", "content_summary", "email", "phone"}
    found_keys = [k for k in exposed_fields if k in high_risk_keys]
    attr_penalty = min(15.0, len(found_keys) * 5.0)

    # 4. Enumeration penalty
    enum_penalty = 15.0 if is_enumeration else 0.0

    raw_score = tenant_weighted_base + attr_penalty + enum_penalty
    final_score = min(100.0, round(raw_score, 1))

    if final_score >= 80.0:
        severity = "CRITICAL"
    elif final_score >= 60.0:
        severity = "HIGH"
    elif final_score >= 35.0:
        severity = "MEDIUM"
    else:
        severity = "LOW"

    breakdown = {
        "base_sensitivity": sens_upper,
        "base_score": base_score,
        "cross_tenant_multiplier": tenant_multiplier,
        "tenant_weighted_base": tenant_weighted_base,
        "sensitive_attributes_found": found_keys,
        "attribute_penalty": attr_penalty,
        "is_enumeration_pattern": is_enumeration,
        "enumeration_penalty": enum_penalty,
        "final_risk_score": final_score,
        "severity": severity,
        "rationale": (
            f"Base sensitivity '{sens_upper}' ({base_score} pts) "
            f"with {tenant_multiplier}x tenant boundary factor, "
            f"+{attr_penalty} pts for sensitive fields ({', '.join(found_keys) if found_keys else 'none'}), "
            f"and +{enum_penalty} pts for enumeration velocity."
        )
    }

    return breakdown


def summarize_overall_threat(exposure_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate organizational risk metrics across all reconstructed exposures."""
    if not exposure_records:
        return {
            "total_exposures": 0,
            "average_risk_score": 0.0,
            "max_risk_score": 0.0,
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0,
            "cross_tenant_count": 0,
            "affected_victims_count": 0,
            "active_attackers_count": 0,
            "composite_threat_level": "NOMINAL"
        }

    total = len(exposure_records)
    scores = [e.get("risk_score", 0.0) for e in exposure_records]
    avg_score = round(sum(scores) / total, 1)
    max_score = round(max(scores), 1)

    critical_count = sum(1 for e in exposure_records if e.get("risk_severity") == "CRITICAL")
    high_count = sum(1 for e in exposure_records if e.get("risk_severity") == "HIGH")
    medium_count = sum(1 for e in exposure_records if e.get("risk_severity") == "MEDIUM")
    low_count = sum(1 for e in exposure_records if e.get("risk_severity") == "LOW")
    cross_tenant_count = sum(1 for e in exposure_records if e.get("is_cross_tenant"))

    victims = {e.get("victim_user_id") for e in exposure_records if e.get("victim_user_id")}
    attackers = {e.get("requester_user_id") for e in exposure_records if e.get("requester_user_id")}

    if critical_count > 0 or cross_tenant_count >= 2 or avg_score >= 70.0:
        threat_level = "CRITICAL_BREACH"
    elif high_count > 0 or avg_score >= 50.0:
        threat_level = "ELEVATED_THREAT"
    elif medium_count > 0:
        threat_level = "MODERATE_RISK"
    else:
        threat_level = "LOW_RISK"

    return {
        "total_exposures": total,
        "average_risk_score": avg_score,
        "max_risk_score": max_score,
        "critical_count": critical_count,
        "high_count": high_count,
        "medium_count": medium_count,
        "low_count": low_count,
        "cross_tenant_count": cross_tenant_count,
        "affected_victims_count": len(victims),
        "active_attackers_count": len(attackers),
        "composite_threat_level": threat_level
    }
