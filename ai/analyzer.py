"""
ExposureLens AI Incident Analyzer & Reporting Engine.

Provides evidence-grounded incident analysis:
1. Deterministic forensic report generation (works 100% offline with zero dependencies).
2. Optional LLM-assisted analysis if an API key is configured.
3. Macro-level CISO / Executive Incident Briefing across all exposures.
"""

import json
import os
import sys
from typing import Any, Dict, List, Optional

from backend.database import SessionLocal
from backend.models import EvidenceRecord, ExposureRecord, Tenant, User
from ai.prompts import (
    SYSTEM_PROMPT,
    build_evidence_prompt,
    generate_deterministic_incident_report
)


def get_exposure_with_evidence(exposure_id: str) -> Optional[Dict[str, Any]]:
    """Fetch complete exposure record and its linked cryptographic evidence chain."""
    db = SessionLocal()
    try:
        exp = db.query(ExposureRecord).filter(ExposureRecord.exposure_id == exposure_id).first()
        if not exp:
            return None

        users = {u.id: u for u in db.query(User).all()}
        tenants = {t.id: t for t in db.query(Tenant).all()}
        evidence_rows = db.query(EvidenceRecord).filter(EvidenceRecord.exposure_id == exposure_id).all()

        req_u = users.get(exp.requester_user_id)
        vic_u = users.get(exp.victim_user_id)
        req_t = tenants.get(exp.requester_tenant_id)
        vic_t = tenants.get(exp.resource_tenant_id)

        evidence_list = [
            {
                "evidence_id": ev.evidence_id,
                "evidence_type": ev.evidence_type,
                "description": ev.description,
                "raw_data": json.loads(ev.raw_data) if ev.raw_data.startswith("{") else ev.raw_data,
                "integrity_hash": ev.integrity_hash,
                "recorded_at": ev.recorded_at
            }
            for ev in evidence_rows
        ]

        exp_dict = {
            "exposure_id": exp.exposure_id,
            "request_id": exp.request_id,
            "requester_user_id": exp.requester_user_id,
            "requester_username": req_u.username if req_u else str(exp.requester_user_id),
            "requester_tenant_id": exp.requester_tenant_id,
            "requester_tenant_name": req_t.name if req_t else "Unknown Tenant",
            "victim_user_id": exp.victim_user_id,
            "victim_username": vic_u.username if vic_u else str(exp.victim_user_id),
            "victim_tenant_id": exp.resource_tenant_id,
            "victim_tenant_name": vic_t.name if vic_t else "Unknown Tenant",
            "resource_type": exp.resource_type,
            "resource_id": exp.resource_id,
            "resource_name": f"{exp.resource_type.title()} #{exp.resource_id}",
            "endpoint": exp.endpoint,
            "timestamp": exp.timestamp,
            "is_cross_tenant": exp.is_cross_tenant,
            "is_enumeration": "ENUMERATION" in exp.detection_rule or (exp.risk_score >= 70.0 and exp.is_cross_tenant),
            "exposed_fields": json.loads(exp.exposed_fields) if exp.exposed_fields else [],
            "sensitivity_level": exp.sensitivity_level,
            "risk_score": exp.risk_score,
            "risk_severity": exp.risk_severity,
            "detection_rule": exp.detection_rule
        }

        return {
            "exposure": exp_dict,
            "evidence": evidence_list
        }
    finally:
        db.close()


def generate_incident_report(
    exposure_id: str,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate an evidence-grounded incident report.
    Defaults to deterministic template; integrates LLM if API key provided.
    """
    data = get_exposure_with_evidence(exposure_id)
    if not data:
        return {
            "error": f"Exposure ID '{exposure_id}' not found.",
            "report_markdown": f"Error: No data found for exposure ID {exposure_id}."
        }

    exposure = data["exposure"]
    evidence = data["evidence"]

    effective_key = api_key or os.environ.get("GEMINI_API_KEY")

    # If LLM key is provided and valid, try querying LLM
    if effective_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=effective_key)
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=SYSTEM_PROMPT
            )
            prompt = build_evidence_prompt(exposure, evidence)
            response = model.generate_content(prompt)
            return {
                "exposure_id": exposure_id,
                "engine": "Gemini 1.5 Flash (LLM Assisted)",
                "report_markdown": response.text,
                "exposure": exposure,
                "evidence": evidence
            }
        except Exception:
            # Graceful fallback to deterministic engine on any API error
            pass

    # Deterministic evidence-grounded generator
    report_md = generate_deterministic_incident_report(exposure, evidence)
    return {
        "exposure_id": exposure_id,
        "engine": "ExposureLens Deterministic Grounder (Offline Safe)",
        "report_markdown": report_md,
        "exposure": exposure,
        "evidence": evidence
    }


def generate_comprehensive_investigation_brief() -> str:
    """Generate high-level organizational briefing across all active exposures."""
    db = SessionLocal()
    try:
        exposures = db.query(ExposureRecord).all()
        if not exposures:
            return "No exposures recorded. System is secure."

        users = {u.id: u for u in db.query(User).all()}
        tenants = {t.id: t for t in db.query(Tenant).all()}

        total = len(exposures)
        cross_tenant = sum(1 for e in exposures if e.is_cross_tenant)
        critical_count = sum(1 for e in exposures if e.risk_severity == "CRITICAL")
        high_count = sum(1 for e in exposures if e.risk_severity == "HIGH")
        avg_score = round(sum(e.risk_score for e in exposures) / total, 1)

        victims = {e.victim_user_id for e in exposures}
        attackers = {e.requester_user_id for e in exposures}

        brief = f"""# ExposureLens Executive Threat Briefing
**Threat Status:** {'CRITICAL ACTIVE BREACH' if critical_count > 0 or cross_tenant > 0 else 'ELEVATED RISK'}
**Total Confirmed Exposures:** `{total}` | **Cross-Tenant Breaches:** `{cross_tenant}`  
**Average Risk Score:** `{avg_score} / 100` | **Affected Victims:** `{len(victims)}` | **Identified Attackers:** `{len(attackers)}`

---

### Key Findings
1. **Multi-Tenancy Breakdown:** `{cross_tenant}` out of `{total}` exposures breached inter-tenant data walls, allowing organizations to access other tenants' proprietary records.
2. **High-Impact Victims:**
"""
        for vic_id in victims:
            v_user = users.get(vic_id)
            v_name = v_user.username if v_user else f"User {vic_id}"
            v_tenant = tenants.get(v_user.tenant_id).name if v_user and v_user.tenant_id in tenants else "Unknown"
            count = sum(1 for e in exposures if e.victim_user_id == vic_id)
            brief += f"   - **{v_name}** ({v_tenant}): `{count}` unauthorized accesses recorded against their resources.\n"

        brief += """
3. **Most Aggressive Requester Identities:**
"""
        for req_id in attackers:
            r_user = users.get(req_id)
            r_name = r_user.username if r_user else f"User {req_id}"
            r_tenant = tenants.get(r_user.tenant_id).name if r_user and r_user.tenant_id in tenants else "Unknown"
            count = sum(1 for e in exposures if e.requester_user_id == req_id)
            brief += f"   - **{r_name}** ({r_tenant}): Initiated `{count}` unauthorized requests.\n"

        brief += f"""
---

### Recommended Remediation Priority
* **P0 - Urgent:** Deploy centralized ownership authorization middleware on `/api/orders/<id>` and `/api/documents/<id>`.
* **P0 - Urgent:** Enforce SQL tenant scoping clauses to prevent multi-tenant cross-talk.
* **P1 - High:** Implement rate-limiting thresholds to halt automated object ID enumeration.
* **P2 - Medium:** Notify affected users ({len(victims)}) in compliance with mandatory breach disclosure regulations.
"""
        return brief
    finally:
        db.close()


if __name__ == "__main__":
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    report = generate_incident_report("EXP-0001")
    print(f"\n=== Generated Report for EXP-0001 (Engine: {report['engine']}) ===")
    print(report["report_markdown"][:600] + "\n...\n[Truncated for console]")
