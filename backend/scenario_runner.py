"""
Scenario Runner for ExposureLens.
Simulates a diverse suite of legitimate, intra-tenant, cross-tenant, failed,
and enumeration API requests to evaluate BOLA detection and exposure reconstruction.
"""

from backend.app import app
from backend.database import SessionLocal
from backend.models import APIRequest


def run_scenarios(clear_existing_logs: bool = False):
    """
    Simulate realistic synthetic API traffic through the Flask test client.
    Captures requests directly into the ExposureLens database.
    """
    if clear_existing_logs:
        db = SessionLocal()
        try:
            db.query(APIRequest).delete()
            db.commit()
            print("[INFO] Cleared previous APIRequest logs.")
        finally:
            db.close()

    client = app.test_client()

    scenarios = [
        # --- SCENARIO GROUP 1: Legitimate Same-User Access (Ownership Respected) ---
        {
            "name": "Legitimate - Alice accesses own Order 1001",
            "endpoint": "/api/orders/1001",
            "headers": {"X-User-ID": "101"},
            "expected_status": 200,
            "category": "LEGITIMATE"
        },
        {
            "name": "Legitimate - Charlie accesses own Document 2003",
            "endpoint": "/api/documents/2003",
            "headers": {"X-User-ID": "103"},
            "expected_status": 200,
            "category": "LEGITIMATE"
        },
        {
            "name": "Legitimate - Bob accesses own Order 1005",
            "endpoint": "/api/orders/1005",
            "headers": {"X-User-ID": "102"},
            "expected_status": 200,
            "category": "LEGITIMATE"
        },

        # --- SCENARIO GROUP 2: Cross-User Intra-Tenant BOLA (Same Tenant, Wrong Owner) ---
        {
            "name": "BOLA Intra-Tenant - Alice (101) accesses Bob's Order 1002 (Tenant 1)",
            "endpoint": "/api/orders/1002",
            "headers": {"X-User-ID": "101"},
            "expected_status": 200,
            "category": "BOLA_INTRA_TENANT"
        },
        {
            "name": "BOLA Intra-Tenant - Bob (102) accesses Alice's Tax Document 2001 (Tenant 1)",
            "endpoint": "/api/documents/2001",
            "headers": {"X-User-ID": "102"},
            "expected_status": 200,
            "category": "BOLA_INTRA_TENANT"
        },

        # --- SCENARIO GROUP 3: Cross-Tenant Critical BOLA (Tenant Boundary Breach) ---
        {
            "name": "BOLA Cross-Tenant - Alice (Tenant 1) accesses Charlie's Biopsy Report 2003 (Tenant 2)",
            "endpoint": "/api/documents/2003",
            "headers": {"X-User-ID": "101"},
            "expected_status": 200,
            "category": "BOLA_CROSS_TENANT"
        },
        {
            "name": "BOLA Cross-Tenant - Eve (Tenant 3) accesses Diana's Cardiac Device Order 1006 (Tenant 2)",
            "endpoint": "/api/orders/1006",
            "headers": {"X-User-ID": "105"},
            "expected_status": 200,
            "category": "BOLA_CROSS_TENANT"
        },
        {
            "name": "BOLA Cross-Tenant - Charlie (Tenant 2) accesses Bob's Compensation Agreement 2002 (Tenant 1)",
            "endpoint": "/api/documents/2002",
            "headers": {"X-User-ID": "103"},
            "expected_status": 200,
            "category": "BOLA_CROSS_TENANT"
        },

        # --- SCENARIO GROUP 4: Authorization Enforced & Error Handling ---
        {
            "name": "Protected Endpoint - Alice (101) denied access to Bob's Order 1002",
            "endpoint": "/api/secure/orders/1002",
            "headers": {"X-User-ID": "101"},
            "expected_status": 403,
            "category": "FAILED_UNAUTHORIZED"
        },
        {
            "name": "Object Probing - Alice requests non-existent Order 9999",
            "endpoint": "/api/orders/9999",
            "headers": {"X-User-ID": "101"},
            "expected_status": 404,
            "category": "OBJECT_NOT_FOUND"
        },

        # --- SCENARIO GROUP 5: Systematic Object Enumeration / Scraping ---
        {
            "name": "Enumeration #1 - Eve scrapes Order 1001",
            "endpoint": "/api/orders/1001",
            "headers": {"X-User-ID": "105"},
            "expected_status": 200,
            "category": "ENUMERATION_ATTACK"
        },
        {
            "name": "Enumeration #2 - Eve scrapes Order 1002",
            "endpoint": "/api/orders/1002",
            "headers": {"X-User-ID": "105"},
            "expected_status": 200,
            "category": "ENUMERATION_ATTACK"
        },
        {
            "name": "Enumeration #3 - Eve scrapes Order 1003",
            "endpoint": "/api/orders/1003",
            "headers": {"X-User-ID": "105"},
            "expected_status": 200,
            "category": "ENUMERATION_ATTACK"
        },
        {
            "name": "Enumeration #4 - Eve scrapes Order 1004",
            "endpoint": "/api/orders/1004",
            "headers": {"X-User-ID": "105"},
            "expected_status": 200,
            "category": "ENUMERATION_ATTACK"
        },
        {
            "name": "Enumeration #5 - Eve scrapes Order 1005",
            "endpoint": "/api/orders/1005",
            "headers": {"X-User-ID": "105"},
            "expected_status": 200,
            "category": "ENUMERATION_ATTACK"
        }
    ]

    print(f"\n[RUNNING] Executing {len(scenarios)} synthetic access scenarios...")
    executed = []
    for sc in scenarios:
        res = client.get(sc["endpoint"], headers=sc["headers"])
        assert res.status_code == sc["expected_status"], (
            f"Scenario '{sc['name']}' returned {res.status_code}, expected {sc['expected_status']}"
        )
        executed.append({
            "name": sc["name"],
            "status": res.status_code,
            "category": sc["category"]
        })

    print(f"[SUCCESS] All {len(executed)} test scenarios simulated and logged in database.")
    return executed


if __name__ == "__main__":
    run_scenarios(clear_existing_logs=True)
