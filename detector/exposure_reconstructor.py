"""
ExposureLens Structured Exposure Reconstruction Engine.

Connects:
Requester -> Accessed Resource -> Actual Owner/Victim -> Tenant Isolation ->
Endpoint -> Timestamp -> Exposed Attributes -> Sensitivity -> Cryptographic Evidence Trace

Produces structured ExposureRecord and EvidenceRecord entries in the database.
"""

import hashlib
import json
from datetime import datetime
from typing import Any, Dict, List

from backend.database import SessionLocal
from backend.models import APIRequest, Document, EvidenceRecord, ExposureRecord, Order, Tenant, User
from detector.bola_detector import detect_bola
from detector.impact_analyzer import calculate_exposure_risk


def sha256_hash(data: str) -> str:
    """Generate SHA-256 cryptographic digest of evidence data."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def reconstruct_exposures(clear_previous: bool = True) -> List[Dict[str, Any]]:
    """
    Reconstruct verified BOLA exposures from detected events and persist them.
    Returns fully populated exposure dictionaries ready for inventory, graph, and reporting.
    """
    db = SessionLocal()
    reconstructed_list = []

    try:
        if clear_previous:
            db.query(EvidenceRecord).delete()
            db.query(ExposureRecord).delete()
            db.commit()

        findings = detect_bola(db_session=db)

        # Pre-fetch lookup caches
        users = {u.id: u for u in db.query(User).all()}
        tenants = {t.id: t for t in db.query(Tenant).all()}
        orders = {o.id: o for o in db.query(Order).all()}
        documents = {d.id: d for d in db.query(Document).all()}

        for idx, finding in enumerate(findings, start=1):
            exp_id_str = f"EXP-{idx:04d}"
            req_id = finding["request_id"]
            res_type = finding["resource_type"]
            obj_id = finding["object_id"]
            req_user_id = finding["requester_user_id"]
            victim_user_id = finding["resource_owner_id"]

            # Resolve resource details & sensitivity
            exposed_fields_list = []
            sensitivity = "HIGH"
            data_classification = "GENERAL"
            resource_name = f"{res_type.title()} #{obj_id}"

            if res_type == "order" and obj_id in orders:
                ord_obj = orders[obj_id]
                exposed_fields_list = ["product", "amount", "shipping_address", "payment_last4", "status"]
                sensitivity = ord_obj.sensitivity
                data_classification = ord_obj.data_classification
                resource_name = f"Order #{obj_id} ({ord_obj.product})"
            elif res_type == "document" and obj_id in documents:
                doc_obj = documents[obj_id]
                exposed_fields_list = ["title", "category", "content_summary"]
                sensitivity = doc_obj.sensitivity
                data_classification = doc_obj.data_classification
                resource_name = f"Document #{obj_id} ({doc_obj.title})"
            else:
                exposed_fields_list = ["object_id", "owner_id"]

            # Calculate explainable risk score
            risk_calc = calculate_exposure_risk(
                sensitivity=sensitivity,
                is_cross_tenant=finding["is_cross_tenant"],
                exposed_fields=exposed_fields_list,
                is_enumeration=finding["is_enumeration"]
            )

            # Persist ExposureRecord
            now_iso = datetime.now().isoformat()
            exp_record = ExposureRecord(
                exposure_id=exp_id_str,
                request_id=req_id,
                requester_user_id=req_user_id,
                victim_user_id=victim_user_id,
                resource_type=res_type,
                resource_id=obj_id,
                endpoint=finding["endpoint"],
                timestamp=finding["timestamp"],
                requester_tenant_id=finding["requester_tenant_id"],
                resource_tenant_id=finding["resource_tenant_id"],
                is_cross_tenant=finding["is_cross_tenant"],
                exposed_fields=json.dumps(exposed_fields_list),
                sensitivity_level=sensitivity,
                risk_score=risk_calc["final_risk_score"],
                risk_severity=risk_calc["severity"],
                detection_rule="OWNERSHIP_MISMATCH_HTTP200",
                reconstruction_timestamp=now_iso
            )
            db.add(exp_record)

            # Generate Cryptographic Evidence Records
            # 1. API Access Evidence
            ev1_raw = json.dumps({
                "request_id": req_id,
                "request_uuid": finding["request_uuid"],
                "endpoint": finding["endpoint"],
                "method": finding["method"],
                "status_code": finding["response_status"],
                "timestamp": finding["timestamp"]
            }, sort_keys=True)
            ev1 = EvidenceRecord(
                evidence_id=f"EVD-{idx:04d}-API",
                exposure_id=exp_id_str,
                evidence_type="API_ACCESS_LOG",
                description=f"HTTP {finding['method']} {finding['endpoint']} returned HTTP 200 to unauthorized requester.",
                raw_data=ev1_raw,
                integrity_hash=sha256_hash(ev1_raw),
                recorded_at=now_iso
            )

            # 2. Ownership Boundary Evidence
            requester_name = users[req_user_id].username if req_user_id in users else str(req_user_id)
            victim_name = users[victim_user_id].username if victim_user_id in users else str(victim_user_id)
            req_tenant_name = tenants[finding['requester_tenant_id']].name if finding['requester_tenant_id'] in tenants else "Unknown"
            vic_tenant_name = tenants[finding['resource_tenant_id']].name if finding['resource_tenant_id'] in tenants else "Unknown"

            ev2_raw = json.dumps({
                "resource_type": res_type,
                "resource_id": obj_id,
                "verified_owner_id": victim_user_id,
                "verified_owner_name": victim_name,
                "owner_tenant_id": finding["resource_tenant_id"],
                "owner_tenant_name": vic_tenant_name,
                "requester_id": req_user_id,
                "requester_name": requester_name,
                "requester_tenant_id": finding["requester_tenant_id"],
                "requester_tenant_name": req_tenant_name,
                "boundary_violation": "CROSS_TENANT" if finding["is_cross_tenant"] else "INTRA_TENANT"
            }, sort_keys=True)
            ev2 = EvidenceRecord(
                evidence_id=f"EVD-{idx:04d}-OWN",
                exposure_id=exp_id_str,
                evidence_type="DATABASE_OWNERSHIP_PROOF",
                description=f"Resource {resource_name} is owned by User {victim_user_id} ({victim_name}), but accessed by User {req_user_id} ({requester_name}).",
                raw_data=ev2_raw,
                integrity_hash=sha256_hash(ev2_raw),
                recorded_at=now_iso
            )

            # 3. Payload Attributes Evidence
            ev3_raw = json.dumps({
                "exposed_fields": exposed_fields_list,
                "sensitivity": sensitivity,
                "classification": data_classification,
                "sample_payload": finding["response_payload_summary"]
            }, sort_keys=True)
            ev3 = EvidenceRecord(
                evidence_id=f"EVD-{idx:04d}-PAYLOAD",
                exposure_id=exp_id_str,
                evidence_type="EXPOSED_DATA_ATTRIBUTES",
                description=f"Exposed data classified as {sensitivity} ({data_classification}) containing fields: {', '.join(exposed_fields_list)}.",
                raw_data=ev3_raw,
                integrity_hash=sha256_hash(ev3_raw),
                recorded_at=now_iso
            )

            db.add_all([ev1, ev2, ev3])

            # Prepare structured dictionary
            reconstructed_list.append({
                "exposure_id": exp_id_str,
                "request_id": req_id,
                "request_uuid": finding["request_uuid"],
                "requester_user_id": req_user_id,
                "requester_username": requester_name,
                "requester_tenant_id": finding["requester_tenant_id"],
                "requester_tenant_name": req_tenant_name,
                "victim_user_id": victim_user_id,
                "victim_username": victim_name,
                "victim_tenant_id": finding["resource_tenant_id"],
                "victim_tenant_name": vic_tenant_name,
                "resource_type": res_type,
                "resource_id": obj_id,
                "resource_name": resource_name,
                "endpoint": finding["endpoint"],
                "timestamp": finding["timestamp"],
                "is_cross_tenant": finding["is_cross_tenant"],
                "is_enumeration": finding["is_enumeration"],
                "exposed_fields": exposed_fields_list,
                "sensitivity_level": sensitivity,
                "data_classification": data_classification,
                "risk_score": risk_calc["final_risk_score"],
                "risk_severity": risk_calc["severity"],
                "risk_rationale": risk_calc["rationale"],
                "evidence_ids": [ev1.evidence_id, ev2.evidence_id, ev3.evidence_id],
                "hashes": [ev1.integrity_hash[:12], ev2.integrity_hash[:12], ev3.integrity_hash[:12]]
            })

        db.commit()
        return reconstructed_list

    finally:
        db.close()


def get_all_exposures() -> List[Dict[str, Any]]:
    """Retrieve all current exposure records formatted for dashboard and reporting."""
    db = SessionLocal()
    try:
        records = db.query(ExposureRecord).order_by(ExposureRecord.id.asc()).all()
        users = {u.id: u for u in db.query(User).all()}
        tenants = {t.id: t for t in db.query(Tenant).all()}

        results = []
        for r in records:
            req_u = users.get(r.requester_user_id)
            vic_u = users.get(r.victim_user_id)
            req_t = tenants.get(r.requester_tenant_id)
            vic_t = tenants.get(r.resource_tenant_id)

            results.append({
                "exposure_id": r.exposure_id,
                "request_id": r.request_id,
                "requester_user_id": r.requester_user_id,
                "requester_username": req_u.username if req_u else str(r.requester_user_id),
                "requester_tenant_id": r.requester_tenant_id,
                "requester_tenant_name": req_t.name if req_t else "N/A",
                "victim_user_id": r.victim_user_id,
                "victim_username": vic_u.username if vic_u else str(r.victim_user_id),
                "victim_tenant_id": r.resource_tenant_id,
                "victim_tenant_name": vic_t.name if vic_t else "N/A",
                "resource_type": r.resource_type,
                "resource_id": r.resource_id,
                "endpoint": r.endpoint,
                "timestamp": r.timestamp,
                "is_cross_tenant": r.is_cross_tenant,
                "exposed_fields": json.loads(r.exposed_fields) if r.exposed_fields else [],
                "sensitivity_level": r.sensitivity_level,
                "risk_score": r.risk_score,
                "risk_severity": r.risk_severity,
                "detection_rule": r.detection_rule,
                "reconstruction_timestamp": r.reconstruction_timestamp
            })
        return results
    finally:
        db.close()


if __name__ == "__main__":
    reconstructed = reconstruct_exposures()
    print(f"\n=== Reconstructed {len(reconstructed)} Structured Exposure Records ===")
    for exp in reconstructed[:3]:
        print(f"\n[+] {exp['exposure_id']} (Risk: {exp['risk_score']} {exp['risk_severity']})")
        print(f"    Path: User {exp['requester_user_id']} ({exp['requester_username']}) -> "
              f"{exp['resource_name']} -> Owned by User {exp['victim_user_id']} ({exp['victim_username']})")
        print(f"    Cross-Tenant: {exp['is_cross_tenant']} | Sensitivity: {exp['sensitivity_level']}")
        print(f"    Exposed Fields: {exp['exposed_fields']}")
        print(f"    Evidence Chain: {', '.join(exp['evidence_ids'])}")
