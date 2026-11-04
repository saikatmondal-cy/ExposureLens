"""
ExposureLens Automated Regulatory Compliance & Legal Breach Notification Engine.

Maps reconstructed BOLA data exposures to statutory notification requirements:
1. Digital Personal Data Protection (DPDP) Act 2023 (India)
2. CERT-In Cyber Security Directions (6-Hour Incident Reporting Directive)
3. Health Insurance Portability and Accountability Act (HIPAA) - Breach Notification Rule (45 CFR §§ 164.400-414)
4. General Data Protection Regulation (GDPR) - Articles 33 & 34

Generates formal regulatory breach disclosure filings and calculates statutory reporting deadlines.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List
from backend.database import SessionLocal
from backend.models import ExposureRecord, Tenant, User


def assess_regulatory_impact(exposure_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluate all active exposures against major cybersecurity & data privacy regulations.
    Computes applicable frameworks, compliance penalties, statutory deadlines, and risk tiers.
    """
    if not exposure_records:
        return {
            "applicable_frameworks": [],
            "max_statutory_fine_tier": "None",
            "cert_in_mandatory": False,
            "dpdp_mandatory": False,
            "hipaa_mandatory": False,
            "gdpr_mandatory": False,
            "reporting_deadlines": [],
            "affected_data_subjects_count": 0,
            "sensitive_categories_exposed": []
        }

    # Extract distinct categories & tenants
    tenants_involved = {e.get("victim_tenant_name") for e in exposure_records}
    sensitivities = {e.get("sensitivity_level") for e in exposure_records}
    all_fields = set()
    for e in exposure_records:
        for f in e.get("exposed_fields", []):
            all_fields.add(f)

    victims = {e.get("victim_user_id") for e in exposure_records if e.get("victim_user_id")}

    has_medical = any("HealthFirst" in t or "Diagnostic" in t for t in tenants_involved) or "CRITICAL" in sensitivities
    has_financial = any("FinServe" in t for t in tenants_involved) or "payment_last4" in all_fields or "amount" in all_fields
    has_pii = any(f in all_fields for f in ["shipping_address", "phone", "email", "address"])

    frameworks = []
    deadlines = []
    now = datetime.now()

    # 1. CERT-In (India Cyber Security Incident Mandate)
    # Mandates 6-hour reporting for unauthorized access to IT systems / data leaks
    cert_in_deadline = (now + timedelta(hours=6)).strftime("%Y-%m-%d %H:%M UTC")
    frameworks.append({
        "name": "CERT-In Cyber Security Directions (Rule 20(5))",
        "jurisdiction": "India",
        "threshold": "Unauthorized access to IT systems / Data breaches",
        "mandated_window": "Within 6 hours of identification",
        "deadline": cert_in_deadline,
        "urgency": "IMMEDIATE (6 Hours)",
        "status": "ACTION REQUIRED"
    })

    # 2. DPDP Act 2023 (Digital Personal Data Protection Act - India)
    # Mandates notification to Data Protection Board of India and affected data principals
    dpdp_deadline = (now + timedelta(hours=72)).strftime("%Y-%m-%d %H:%M UTC")
    frameworks.append({
        "name": "DPDP Act 2023 (Section 8(6))",
        "jurisdiction": "India",
        "threshold": "Personal Data Breach impacting Data Principals",
        "mandated_window": "Intimation to Board & Data Principals",
        "deadline": dpdp_deadline,
        "max_penalty": "Up to INR 250 Crores (Section 33)",
        "status": "MANDATORY"
    })

    # 3. HIPAA Breach Notification Rule (for healthcare tenant data)
    if has_medical:
        hipaa_deadline = (now + timedelta(days=60)).strftime("%Y-%m-%d")
        frameworks.append({
            "name": "HIPAA Breach Notification Rule (45 CFR § 164.404)",
            "jurisdiction": "United States / Healthcare Inter-operability",
            "threshold": "Unauthorized exposure of Protected Health Information (PHI)",
            "mandated_window": "Without unreasonable delay, max 60 calendar days",
            "deadline": hipaa_deadline,
            "max_penalty": "Up to $1.9M / year (Tier 4 Willful Neglect)",
            "status": "MANDATORY - PHI COMPROMISED"
        })

    # 4. GDPR (Articles 33 & 34)
    if has_financial or has_pii:
        gdpr_deadline = (now + timedelta(hours=72)).strftime("%Y-%m-%d %H:%M UTC")
        frameworks.append({
            "name": "GDPR Articles 33/34",
            "jurisdiction": "European Union / Global extraterritorial",
            "threshold": "High risk to rights and freedoms of natural persons",
            "mandated_window": "Within 72 hours to Supervisory Authority",
            "deadline": gdpr_deadline,
            "max_penalty": "Up to €20M or 4% of worldwide annual turnover",
            "status": "ACTIVE JURISDICTION"
        })

    return {
        "applicable_frameworks": frameworks,
        "cert_in_mandatory": True,
        "dpdp_mandatory": True,
        "hipaa_mandatory": has_medical,
        "gdpr_mandatory": (has_financial or has_pii),
        "affected_data_subjects_count": len(victims),
        "sensitive_categories_exposed": list(all_fields),
        "highest_urgency": "CERT-In 6-Hour Window",
        "summary": (
            f"Breach involves {len(victims)} affected data principals across {len(tenants_involved)} organizational tenants. "
            f"Mandatory regulatory filings required under CERT-In (6 hrs), DPDP Act 2023 (72 hrs)"
            + (", and HIPAA Breach Notification Rule." if has_medical else ".")
        )
    }


def generate_regulatory_filing_notice(exposure_records: List[Dict[str, Any]]) -> str:
    """Draft an official Incident Notification Notice for Regulatory Authorities & Data Principals."""
    assessment = assess_regulatory_impact(exposure_records)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

    framework_rows = "\n".join([
        f"| **{fw['name']}** | {fw['jurisdiction']} | `{fw['mandated_window']}` | **{fw['deadline']}** | `{fw['status']}` |"
        for fw in assessment["applicable_frameworks"]
    ])

    sample_exposures = exposure_records[:4] if exposure_records else []
    sample_rows = "\n".join([
        f"| `{e['exposure_id']}` | User {e['victim_user_id']} ({e['victim_username']}) | {e['victim_tenant_name']} | {e['resource_type'].title()} #{e['resource_id']} | `{e['sensitivity_level']}` |"
        for e in sample_exposures
    ])

    filing_document = f"""# 🏛️ FORMAL DATA BREACH REGULATORY DISCLOSURE NOTICE
**Filing Reference:** `EXPOSURELENS-INC-{datetime.now().strftime('%Y%m%d')}-01`  
**Date of Incident Discovery:** `{now_str}`  
**Nature of Incident:** `Broken Object Level Authorization (BOLA / CWE-639) — Systemic API Perimeter Failure`

---

## 1. Incident Overview & Technical Classification
ExposureLens Telemetry confirmed that unauthorized API actors bypassed resource authorization logic on REST endpoints (`/api/orders/<id>`, `/api/documents/<id>`). The incident resulted in confirmed, unauthorized data extraction of **{assessment['affected_data_subjects_count']} Data Principals** across multiple organizational tenants.

* **Primary Root Cause:** Failure to validate `requester_id == resource.owner_id` prior to state retrieval (OWASP API1:2023).
* **Multi-Tenancy Impact:** Logical tenant separation was violated, allowing cross-tenant data exfiltration.

---

## 2. Applicable Statutory Frameworks & Deadlines
The following regulatory reporting obligations have been triggered:

| Statutory Authority / Act | Jurisdiction | Reporting Window | Absolute Filing Deadline | Compliance Status |
| :--- | :--- | :--- | :--- | :--- |
{framework_rows}

---

## 3. Categories of Exposed Personal Data
The data attributes exposed without authorization include:
`{', '.join(assessment['sensitive_categories_exposed'])}`

**Sample Affected Records:**
| Incident ID | Compromised Data Principal | Organizational Tenant | Target Resource | Sensitivity |
| :--- | :--- | :--- | :--- | :--- |
{sample_rows}

---

## 4. Immediate Mitigation & Remediation Actions Taken
1. **Automated Enforcement Rule Deployed:** Enforced strict object ownership assertions at the API gateway and controller tier.
2. **Session Revocation:** Quarantined active access credentials associated with the identifying attacker identities.
3. **Database Audit:** Verified that no database records were modified or deleted (unauthorized read-only exposure).
4. **Data Principal Notification:** Preparing secure email and postal communications to all affected users pursuant to Section 8(6) of the DPDP Act 2023.

---
*Signed on behalf of Corporate Information Security Office (CISO) & Legal Counsel.*  
*Generated by ExposureLens Compliance Module v2.0.*
"""
    return filing_document


if __name__ == "__main__":
    from detector.exposure_reconstructor import get_all_exposures
    exps = get_all_exposures()
    assessment = assess_regulatory_impact(exps)
    print("\n=== Regulatory Impact Assessment ===")
    print("Mandatory Frameworks:", [f["name"] for f in assessment["applicable_frameworks"]])
    print("Affected Subjects:", assessment["affected_data_subjects_count"])
    print("Highest Urgency:", assessment["highest_urgency"])
