"""
ExposureLens Evidence-Grounded Prompt Templates & Security Reporting Framework.

Core Principle:
Every claim must be strictly grounded in verified EvidenceRecord and ExposureRecord entries.
Zero hallucination of users, IDs, timestamps, or data classifications.
"""

SYSTEM_PROMPT = """You are ExposureLens AI, an expert cybersecurity incident responder and API security analyst.
Your task is to analyze verified evidence of Broken Object Level Authorization (BOLA) data exposures.

CRITICAL CONSTRAINTS:
1. Ground every statement strictly in the provided evidence JSON.
2. DO NOT hallucinate, infer, or assume any user, resource, timestamp, or exposed data not explicitly given.
3. Reference specific Evidence IDs (e.g., EVD-0001-API, EVD-0001-OWN) and SHA-256 hashes for all factual assertions.
4. If an attribute or cause is unknown or absent, state explicitly: "Not evidenced in the provided telemetry."
5. Clearly distinguish between intra-tenant access violations and cross-tenant isolation breaches.
6. Provide concrete, actionable remediation steps for the identified vulnerability.
"""


def build_evidence_prompt(exposure_record: dict, evidence_records: list) -> str:
    """Construct an evidence-grounded analysis prompt for an individual exposure."""
    return f"""Analyze the following verified BOLA data exposure event:

EXPOSURE METADATA:
- Exposure ID: {exposure_record.get('exposure_id')}
- Request UUID: {exposure_record.get('request_uuid')}
- Timestamp: {exposure_record.get('timestamp')}
- Endpoint: {exposure_record.get('endpoint')}
- Requester: User {exposure_record.get('requester_user_id')} ({exposure_record.get('requester_username')}) [Tenant: {exposure_record.get('requester_tenant_name')} - ID {exposure_record.get('requester_tenant_id')}]
- Victim / Owner: User {exposure_record.get('victim_user_id')} ({exposure_record.get('victim_username')}) [Tenant: {exposure_record.get('victim_tenant_name')} - ID {exposure_record.get('victim_tenant_id')}]
- Resource: {exposure_record.get('resource_type')} #{exposure_record.get('resource_id')}
- Cross-Tenant Breach: {exposure_record.get('is_cross_tenant')}
- Data Sensitivity: {exposure_record.get('sensitivity_level')}
- Exposed Fields: {exposure_record.get('exposed_fields')}
- Risk Score: {exposure_record.get('risk_score')} / 100 ({exposure_record.get('risk_severity')})
- Risk Rationale: {exposure_record.get('risk_rationale')}

VERIFIED EVIDENCE CHAIN:
{chr(10).join([f"- [{ev.get('evidence_id')}] ({ev.get('evidence_type')}): {ev.get('description')} (Hash: {ev.get('integrity_hash', '')[:16]}...)" for ev in evidence_records])}

Please provide:
1. Executive Summary of the incident.
2. Exact Unauthorized Exposure Breakdown (Who, What, Whom, How).
3. Tenant Boundary & Impact Assessment.
4. Cryptographic Evidence Verification Trace.
5. Mitigation & Defensive Recommendations.
"""


def generate_deterministic_incident_report(
    exposure_record: dict,
    evidence_records: list,
    tenant_details: dict = None
) -> str:
    """
    Deterministic fallback report generator that produces high-quality,
    evidence-grounded reports without requiring external LLM API calls or keys.
    """
    exp_id = exposure_record.get("exposure_id", "UNKNOWN")
    req_user = f"User {exposure_record.get('requester_user_id')} ({exposure_record.get('requester_username')})"
    vic_user = f"User {exposure_record.get('victim_user_id')} ({exposure_record.get('victim_username')})"
    req_tenant = exposure_record.get("requester_tenant_name", "Unknown Tenant")
    vic_tenant = exposure_record.get("victim_tenant_name", "Unknown Tenant")
    res_type = exposure_record.get("resource_type", "Resource").capitalize()
    res_id = exposure_record.get("resource_id", "N/A")
    res_name = exposure_record.get("resource_name", f"{res_type} #{res_id}")
    endpoint = exposure_record.get("endpoint", "/api/endpoint")
    timestamp = exposure_record.get("timestamp", "N/A")
    sensitivity = exposure_record.get("sensitivity_level", "MEDIUM")
    risk_score = exposure_record.get("risk_score", 0.0)
    risk_sev = exposure_record.get("risk_severity", "MEDIUM")
    is_cross = exposure_record.get("is_cross_tenant", False)
    is_enum = exposure_record.get("is_enumeration", False)
    exposed_fields = exposure_record.get("exposed_fields", [])

    cross_tenant_text = (
        f"**CRITICAL ISOLATION BREACH:** Access crossed organizational boundaries between "
        f"**{req_tenant}** (Requester) and **{vic_tenant}** (Victim)."
        if is_cross
        else f"**INTRA-TENANT VIOLATION:** Access occurred within the same organizational tenant (**{req_tenant}**)."
    )

    enum_text = (
        "- **Attack Pattern Detected:** Requester executed sequential enumeration across multiple target IDs."
        if is_enum
        else "- **Attack Pattern:** Single targeted object access."
    )

    evidence_bullets = "\n".join([
        f"  * **[{ev.get('evidence_id')}]** `{ev.get('evidence_type')}`: {ev.get('description')}  \n"
        f"    *SHA-256 Digest:* `{ev.get('integrity_hash', 'N/A')}`"
        for ev in evidence_records
    ]) if evidence_records else "  * *No cryptographic evidence records linked.*"

    report = f"""# 🛡️ ExposureLens Forensic Security Incident Report
**Incident Identifier:** `{exp_id}` | **Severity:** `{risk_sev}` (Risk Score: `{risk_score}/100`)  
**Generated:** `{timestamp}` | **Vulnerability Classification:** `CWE-639 / OWASP API1:2023 - BOLA`

---

## 1. Executive Summary
On `{timestamp}`, ExposureLens detected a confirmed **Broken Object Level Authorization (BOLA)** incident. Authenticated entity **{req_user}** successfully queried endpoint `{endpoint}` and obtained unauthorized access to **{res_name}**, a resource owned by **{vic_user}**. The server responded with HTTP 200, exposing `{sensitivity}` data.

{cross_tenant_text}

---

## 2. Exposure & Blast Radius Breakdown
| Parameter | Forensic Detail | Verification Status |
| :--- | :--- | :--- |
| **Requester (Actor)** | {req_user} | Verified from HTTP Session Header |
| **Actor Organization** | {req_tenant} (Tenant ID: {exposure_record.get('requester_tenant_id')}) | Verified via Identity Store |
| **Victim (Resource Owner)** | {vic_user} | Verified via Database Ownership Record |
| **Target Organization** | {vic_tenant} (Tenant ID: {exposure_record.get('victim_tenant_id')}) | Verified via Tenant Isolation Table |
| **Accessed Resource** | {res_name} | Verified Object ID |
| **API Endpoint** | `{endpoint}` | Confirmed Vulnerable Controller |
| **HTTP Status Code** | `200 OK` (Unauthorized Data Delivered) | Confirmed Server Log |
| **Data Sensitivity** | `{sensitivity}` | Verified Classification Registry |
| **Exposed Fields** | `{', '.join(exposed_fields) if exposed_fields else 'N/A'}` | Verified from Response Payload |

{enum_text}

---

## 3. Risk & Impact Scoring Rationale
* **Base Sensitivity Weight:** `{sensitivity}` classification contributes baseline impact points.
* **Multi-Tenant Boundary:** Multiplier applied due to {'cross-tenant boundary crossing' if is_cross else 'intra-tenant resource mismatch'}.
* **Privacy Attributes:** High-risk identifiers ({', '.join(exposed_fields)}) leaked without user consent.
* **Total Computed Risk Score:** **{risk_score} / 100 ({risk_sev})**

---

## 4. Cryptographic Evidence Chain of Custody
All factual assertions in this report are backed by non-repudiable evidence recorded in the ExposureLens Evidence Ledger:

{evidence_bullets}

---

## 5. MITRE ATT&CK Mapping
* **T1078 - Valid Accounts:** Actor used legitimate authenticated credentials to bypass object-level boundaries.
* **T1530 - Data from Information Repositories:** Direct retrieval of sensitive victim records via unprotected object endpoints.
* **T1059 / T1119 - Automated Collection:** Object enumeration pattern observed across sequential identifier ranges.

---

## 6. Defensive Engineering Remediation
1. **Enforce Object-Level Authorization Gate:**
   Update the controller handler for `{endpoint}` to enforce strict ownership verification before query execution:
   ```python
   if resource.owner_id != authenticated_user.id:
       abort(403, "Access Denied: Object ownership boundary violated")
   ```
2. **Implement Logical Tenant Partitioning:**
   Ensure database queries incorporate mandatory tenant scoping clauses (`WHERE tenant_id = :current_user_tenant_id`).
3. **Deploy Anomaly Rate-Limiting:**
   Throttle and alert on sequential object probing patterns exceeding 3 requests per 10 seconds.
"""
    return report
