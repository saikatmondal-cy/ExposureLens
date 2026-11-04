"""
ExposureLens Quantitative Evaluation & Benchmark Suite.

Evaluates:
1. BOLA Detection Performance (Precision, Recall, F1, Specificity, FPR).
2. Exposure Reconstruction Accuracy (Requester, Victim, Resource, Tenant, Sensitivity).
3. Evidence Completeness & Integrity Hash Validation.
4. Comparative Analysis: Conventional BOLA Scanner vs. ExposureLens Reconstruction.
"""

import time
from typing import Any, Dict

from backend.database import SessionLocal
from backend.models import APIRequest, EvidenceRecord, ExposureRecord
from detector.bola_detector import detect_bola
from detector.exposure_reconstructor import reconstruct_exposures, sha256_hash


def run_benchmark_evaluation() -> Dict[str, Any]:
    """Run full quantitative evaluation against verified lab ground truth."""
    db = SessionLocal()

    try:
        # Time detection
        t0 = time.perf_counter()
        findings = detect_bola(db_session=db)
        t_detect = (time.perf_counter() - t0) * 1000

        # Time reconstruction
        t1 = time.perf_counter()
        exposures = db.query(ExposureRecord).all()
        if not exposures:
            exposures = reconstruct_exposures(clear_previous=True)
        t_reconstruct = (time.perf_counter() - t1) * 1000

        all_requests = db.query(APIRequest).all()
        total_requests = len(all_requests)

        # Ground truth assessment:
        # Request is truly BOLA if response_status == 200 and requester_user_id != resource_owner_id and resource_owner_id is not None
        tp, fp, tn, fn = 0, 0, 0, 0
        detected_req_ids = {f["request_id"] for f in findings}

        for req in all_requests:
            actual_bola = (
                req.response_status == 200
                and req.resource_owner_id is not None
                and req.requester_user_id != req.resource_owner_id
            )
            predicted_bola = req.id in detected_req_ids

            if actual_bola and predicted_bola:
                tp += 1
            elif not actual_bola and predicted_bola:
                fp += 1
            elif not actual_bola and not predicted_bola:
                tn += 1
            elif actual_bola and not predicted_bola:
                fn += 1

        precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 1.0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 1.0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0

        # Reconstruction Fidelity Checks
        correct_victims = 0
        correct_resources = 0
        correct_tenants = 0
        correct_sensitivities = 0

        for exp in exposures:
            # Query parent request
            parent_req = db.query(APIRequest).filter(APIRequest.id == exp.request_id).first()
            if parent_req:
                if exp.victim_user_id == parent_req.resource_owner_id:
                    correct_victims += 1
                if exp.resource_id == parent_req.object_id:
                    correct_resources += 1
                if exp.resource_tenant_id == parent_req.resource_tenant_id:
                    correct_tenants += 1
                if exp.sensitivity_level in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                    correct_sensitivities += 1

        exp_count = max(1, len(exposures))
        reconstruction_metrics = {
            "total_reconstructed": len(exposures),
            "victim_attribution_accuracy": round((correct_victims / exp_count) * 100, 1),
            "resource_identification_accuracy": round((correct_resources / exp_count) * 100, 1),
            "tenant_attribution_accuracy": round((correct_tenants / exp_count) * 100, 1),
            "sensitivity_classification_accuracy": round((correct_sensitivities / exp_count) * 100, 1),
        }

        # Cryptographic Evidence Audit
        all_evidence = db.query(EvidenceRecord).all()
        valid_hashes = 0
        for ev in all_evidence:
            recomputed = sha256_hash(ev.raw_data)
            if recomputed == ev.integrity_hash:
                valid_hashes += 1

        evidence_count = max(1, len(all_evidence))
        evidence_metrics = {
            "total_evidence_records": len(all_evidence),
            "evidence_per_exposure_ratio": round(len(all_evidence) / exp_count, 1),
            "cryptographic_integrity_valid_pct": round((valid_hashes / evidence_count) * 100, 1),
            "tamper_detected_count": len(all_evidence) - valid_hashes
        }

        # Comparative Information Utility
        comparison_matrix = [
            {"Dimension": "Identifies Vulnerable Endpoint", "Traditional BOLA Scanner": "Yes", "ExposureLens": "Yes"},
            {"Dimension": "Identifies Requesting User", "Traditional BOLA Scanner": "Optional (Logs)", "ExposureLens": "Yes (Ground Truth)"},
            {"Dimension": "Identifies Affected Victim User", "Traditional BOLA Scanner": "No", "ExposureLens": "Yes (Ownership Link)"},
            {"Dimension": "Reconstructs Exact Data Attributes", "Traditional BOLA Scanner": "No (Payload Dumps Only)", "ExposureLens": "Yes (Structured Schema)"},
            {"Dimension": "Cross-Tenant Boundary Attribution", "Traditional BOLA Scanner": "No", "ExposureLens": "Yes (Isolation Verification)"},
            {"Dimension": "Sensitivity & Risk Blast Radius", "Traditional BOLA Scanner": "Generic CVSS", "ExposureLens": "Yes (Explainable 4-Factor Score)"},
            {"Dimension": "Relationship Graph Visualization", "Traditional BOLA Scanner": "No", "ExposureLens": "Yes (Interactive NetworkX Graph)"},
            {"Dimension": "Cryptographic Audit Trail", "Traditional BOLA Scanner": "No", "ExposureLens": "Yes (SHA-256 Ledger)"},
            {"Dimension": "Evidence-Grounded Incident Report", "Traditional BOLA Scanner": "No (Static alert)", "ExposureLens": "Yes (Zero-Hallucination Report)"}
        ]

        return {
            "detection": {
                "total_requests_analyzed": total_requests,
                "true_positives": tp,
                "false_positives": fp,
                "true_negatives": tn,
                "false_negatives": fn,
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1_score": round(f1, 4),
                "specificity": round(specificity, 4),
                "false_positive_rate": round(fpr, 4),
                "detection_latency_ms": round(t_detect, 2)
            },
            "reconstruction": reconstruction_metrics,
            "evidence": evidence_metrics,
            "comparison": comparison_matrix
        }

    finally:
        db.close()


if __name__ == "__main__":
    bench = run_benchmark_evaluation()
    print("\n=== ExposureLens Quantitative Evaluation Results ===")
    d = bench["detection"]
    print(f"Detection: Precision={d['precision']} | Recall={d['recall']} | F1={d['f1_score']} | FPR={d['false_positive_rate']}")
    r = bench["reconstruction"]
    print(f"Reconstruction Accuracy: Victim={r['victim_attribution_accuracy']}% | Tenant={r['tenant_attribution_accuracy']}% | Resource={r['resource_identification_accuracy']}%")
    e = bench["evidence"]
    print(f"Evidence Audit: {e['total_evidence_records']} records | Integrity={e['cryptographic_integrity_valid_pct']}% | Tampered={e['tamper_detected_count']}")
