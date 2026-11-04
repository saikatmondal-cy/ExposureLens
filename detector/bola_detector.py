"""
ExposureLens Deterministic BOLA Detection Engine.

Core Research Principle:
- Deterministic security analysis based on verifiable authorization facts.
- No probabilistic LLM hallucination in core security boundary decisions.
- Accurately segregates legitimate access, blocked attempts (403), not-found (404),
  intra-tenant BOLA, and cross-tenant boundary breaches.
"""

from collections import defaultdict
from typing import Any, Dict, List
from backend.database import SessionLocal
from backend.models import APIRequest, User


def detect_bola(db_session=None) -> List[Dict[str, Any]]:
    """
    Analyze logged API events and identify confirmed BOLA violations.

    Conditions for Confirmed BOLA:
    1. HTTP response status == 200 (access was granted and data delivered)
    2. requester_user_id != resource_owner_id (requester does not own the requested resource)
    3. resource_owner_id is not None (object exists and has a verified owner)
    """
    owns_session = False
    if db_session is None:
        db = SessionLocal()
        owns_session = True
    else:
        db = db_session

    try:
        requests = db.query(APIRequest).order_by(APIRequest.id.asc()).all()

        # Track requester activity for enumeration detection
        requester_object_history = defaultdict(list)
        for req in requests:
            if req.object_id is not None:
                requester_object_history[req.requester_user_id].append(req.object_id)

        findings = []

        for req in requests:
            # Check for BOLA condition
            is_successful = (req.response_status == 200)
            has_owner = (req.resource_owner_id is not None)
            is_mismatch = (req.requester_user_id != req.resource_owner_id)

            if is_successful and has_owner and is_mismatch:
                is_cross_tenant = (
                    req.requester_tenant_id is not None
                    and req.resource_tenant_id is not None
                    and req.requester_tenant_id != req.resource_tenant_id
                )

                # Check if part of enumeration pattern (>2 distinct objects targeted by requester)
                objects_targeted = set(requester_object_history[req.requester_user_id])
                is_enumeration = len(objects_targeted) >= 3

                sub_type = "BOLA_CROSS_TENANT" if is_cross_tenant else "BOLA_INTRA_TENANT"
                if is_enumeration:
                    sub_type += "_ENUMERATION"

                findings.append({
                    "request_id": req.id,
                    "request_uuid": req.request_id or f"REQ-{req.id:04d}",
                    "timestamp": req.timestamp,
                    "requester_user_id": req.requester_user_id,
                    "requester_tenant_id": req.requester_tenant_id,
                    "endpoint": req.endpoint,
                    "method": req.method,
                    "resource_type": req.resource_type or "order",
                    "object_id": req.object_id,
                    "resource_owner_id": req.resource_owner_id,
                    "resource_tenant_id": req.resource_tenant_id,
                    "response_status": req.response_status,
                    "is_cross_tenant": is_cross_tenant,
                    "is_enumeration": is_enumeration,
                    "vulnerability": "BOLA",
                    "violation_type": sub_type,
                    "response_payload_summary": req.response_body_sample
                })

        return findings

    finally:
        if owns_session:
            db.close()


if __name__ == "__main__":
    import sys
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    findings = detect_bola()

    print("\n=== ExposureLens Deterministic BOLA Detection ===")
    print(f"Total BOLA Violations Detected: {len(findings)}")

    for f in findings:
        print(f"\n[!] BOLA VIOLATION: {f['request_uuid']}")
        print(f"    Requester User: {f['requester_user_id']} (Tenant {f['requester_tenant_id']})")
        print(f"    Victim Owner:   {f['resource_owner_id']} (Tenant {f['resource_tenant_id']})")
        print(f"    Resource:       {f['resource_type'].upper()} #{f['object_id']}")
        print(f"    Endpoint:       {f['endpoint']}")
        print(f"    Cross-Tenant:   {f['is_cross_tenant']}")
        print(f"    Enumeration:    {f['is_enumeration']}")
        print(f"    Status:         {f['response_status']} OK")
