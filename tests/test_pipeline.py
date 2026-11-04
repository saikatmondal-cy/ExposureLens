"""
ExposureLens Complete End-to-End Pipeline & Research Verification Test Suite.

Executes and verifies:
1. Database initialization & seed integrity.
2. Synthetic scenario execution & request logging.
3. Deterministic BOLA detection engine.
4. Structured exposure reconstruction & cryptographic evidence creation.
5. Risk & impact scoring calculation.
6. NetworkX exposure graph construction.
7. Evidence-grounded forensic report generation.
8. Quantitative research benchmark evaluation.
9. Semantic Property-Level Exposure Delta (OWASP API1 + API3).
10. Tenant Isolation Failure Index (TIFI) & Spillover Matrix.
11. Cryptographic Proof-of-Exposure (PoE) Blockchain Hash-Chain.
12. AI Faithfulness & Zero-Hallucination Verification Score.
13. Camera-Ready IEEE LaTeX Paper Compiler.
"""

import unittest
from backend.database import init_db, SessionLocal
from backend.models import Tenant, User, Order, Document, APIRequest, ExposureRecord, EvidenceRecord
from backend.scenario_runner import run_scenarios
from detector.bola_detector import detect_bola
from detector.exposure_reconstructor import reconstruct_exposures, get_all_exposures, sha256_hash
from detector.impact_analyzer import calculate_exposure_risk, summarize_overall_threat
from detector.exposure_graph import build_exposure_graph, compute_graph_metrics
from detector.semantic_exposure import analyze_semantic_property_exposure, compute_macro_semantic_exposure_matrix
from detector.tenant_isolation import compute_tenant_isolation_metrics
from detector.forensic_chain import build_forensic_hash_chain, verify_chain_integrity, generate_forensic_certificate
from ai.analyzer import generate_incident_report, generate_comprehensive_investigation_brief
from ai.faithfulness_verifier import verify_report_faithfulness, benchmark_all_incident_reports
from results.evaluation import run_benchmark_evaluation
from results.paper_compiler import generate_ieee_latex_paper


class TestExposureLensPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Seed database and run scenarios once for all tests."""
        init_db(force_recreate=True)
        run_scenarios(clear_existing_logs=True)
        reconstruct_exposures(clear_previous=True)

    def test_01_database_seed_integrity(self):
        db = SessionLocal()
        try:
            self.assertEqual(db.query(Tenant).count(), 3, "Expected 3 tenants")
            self.assertEqual(db.query(User).count(), 5, "Expected 5 users")
            self.assertEqual(db.query(Order).count(), 7, "Expected 7 orders")
            self.assertEqual(db.query(Document).count(), 5, "Expected 5 documents")
        finally:
            db.close()

    def test_02_request_logging_and_scenarios(self):
        db = SessionLocal()
        try:
            reqs = db.query(APIRequest).all()
            self.assertEqual(len(reqs), 15, "Expected 15 simulated requests")
            statuses = set(r.response_status for r in reqs)
            self.assertIn(200, statuses)
            self.assertIn(403, statuses)
            self.assertIn(404, statuses)
        finally:
            db.close()

    def test_03_deterministic_bola_detection(self):
        findings = detect_bola()
        self.assertEqual(len(findings), 10, "Expected exactly 10 confirmed BOLA events")

        for f in findings:
            self.assertEqual(f["response_status"], 200)
            self.assertNotEqual(f["requester_user_id"], f["resource_owner_id"])

        cross_tenant = [f for f in findings if f["is_cross_tenant"]]
        self.assertGreater(len(cross_tenant), 0, "Expected cross-tenant findings")

    def test_04_exposure_reconstruction(self):
        exposures = get_all_exposures()
        self.assertEqual(len(exposures), 10, "Expected 10 reconstructed exposure records")

        exp1 = exposures[0]
        self.assertTrue(exp1["exposure_id"].startswith("EXP-"))
        self.assertIn("exposed_fields", exp1)
        self.assertIn(exp1["sensitivity_level"], ["CRITICAL", "HIGH", "MEDIUM", "LOW"])
        self.assertGreaterEqual(exp1["risk_score"], 0.0)

    def test_05_cryptographic_evidence_chain(self):
        db = SessionLocal()
        try:
            evidence = db.query(EvidenceRecord).all()
            self.assertEqual(len(evidence), 30, "Expected 30 evidence records (3 per exposure)")

            for ev in evidence:
                recomputed = sha256_hash(ev.raw_data)
                self.assertEqual(ev.integrity_hash, recomputed, f"Tamper detected in {ev.evidence_id}")
        finally:
            db.close()

    def test_06_risk_and_impact_assessment(self):
        calc_crit = calculate_exposure_risk(
            sensitivity="CRITICAL",
            is_cross_tenant=True,
            exposed_fields=["content_summary"],
            is_enumeration=True
        )
        self.assertGreaterEqual(calc_crit["final_risk_score"], 80.0)
        self.assertEqual(calc_crit["severity"], "CRITICAL")

    def test_07_exposure_graph(self):
        G = build_exposure_graph()
        self.assertGreater(len(G.nodes), 20)
        self.assertGreater(len(G.edges), 25)

        metrics = compute_graph_metrics(G)
        self.assertGreater(metrics["cross_tenant_paths_count"], 0)

    def test_08_evidence_grounded_reporting(self):
        report_data = generate_incident_report("EXP-0001")
        self.assertIn("report_markdown", report_data)
        md = report_data["report_markdown"]
        self.assertIn("EXP-0001", md)

    def test_09_research_benchmark_evaluation(self):
        bench = run_benchmark_evaluation()
        d = bench["detection"]
        self.assertEqual(d["precision"], 1.0)
        self.assertEqual(d["recall"], 1.0)
        self.assertEqual(d["f1_score"], 1.0)

    def test_10_semantic_property_exposure_delta(self):
        sem_macro = compute_macro_semantic_exposure_matrix()
        self.assertEqual(sem_macro["total_incidents"], 10)
        self.assertGreater(sem_macro["total_leaked_properties_count"], 20)
        self.assertGreater(sem_macro["average_sev"], 50.0)
        self.assertIn("PII_DIRECT", sem_macro["category_distribution"])
        self.assertIn("FINANCIAL_METADATA", sem_macro["category_distribution"])

    def test_11_tenant_isolation_failure_index(self):
        tifi_res = compute_tenant_isolation_metrics()
        self.assertGreater(tifi_res["tifi_score"], 0.5)
        self.assertEqual(tifi_res["isolation_status"], "PERIMETER_BREACH")
        self.assertEqual(len(tifi_res["tenant_names"]), 3)

    def test_12_proof_of_exposure_hash_chain(self):
        chain = build_forensic_hash_chain()
        self.assertEqual(chain["chain_length"], 10)
        valid, errs = verify_chain_integrity(chain)
        self.assertTrue(valid, f"Proof of exposure chain invalid: {errs}")

        cert = generate_forensic_certificate("EXP-0001")
        self.assertIn("CERT-EXPOSURELENS-EXP-0001", cert)

    def test_13_ai_faithfulness_zero_hallucination(self):
        faith_bench = benchmark_all_incident_reports()
        self.assertEqual(faith_bench["total_evaluated_incidents"], 10)
        self.assertEqual(faith_bench["average_faithfulness_score"], 1.0)
        self.assertEqual(faith_bench["average_hallucination_rate"], 0.0)

    def test_14_latex_paper_generation(self):
        tex = generate_ieee_latex_paper()
        self.assertIn("ExposureLens: Evidence-Based Data Exposure Reconstruction", tex)
        self.assertIn(r"\begin{abstract}", tex)
        self.assertIn(r"\end{document}", tex)


if __name__ == "__main__":
    unittest.main()
