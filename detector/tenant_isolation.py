"""
ExposureLens Multi-Tenant Isolation Failure & Blast-Radius Engine.

Formulation:
Quantifies organizational perimeter breakdown in multi-tenant SaaS architectures:
1. Tenant Isolation Failure Index (TIFI):
       TIFI = (Sum of cross-tenant exposure events) / (Total exposure events)
   - Range: [0.0, 1.0]
   - 0.0: Strict tenant perimeter maintained (pure intra-tenant permission failures)
   - 1.0: Complete tenant boundary collapse (all exposures cross tenant borders)

2. Inter-Tenant Spillover Adjacency Matrix:
       M_spill[T_requester, T_victim] = Count of unauthorized cross-tenant queries
"""

from typing import Any, Dict, List
import pandas as pd
from backend.database import SessionLocal
from backend.models import ExposureRecord, Tenant, User


def compute_tenant_isolation_metrics() -> Dict[str, Any]:
    """Compute mathematical multi-tenancy isolation metrics and inter-tenant spillover matrix."""
    from detector.exposure_reconstructor import get_all_exposures
    exposures = get_all_exposures()

    db = SessionLocal()
    try:
        tenants = {t.id: t.name for t in db.query(Tenant).all()}
        tenant_names = sorted(list(tenants.values()))

        if not exposures:
            return {
                "tifi_score": 0.0,
                "total_exposures": 0,
                "cross_tenant_count": 0,
                "intra_tenant_count": 0,
                "tenant_names": tenant_names,
                "spillover_matrix": {},
                "spillover_df": pd.DataFrame(),
                "most_impacted_tenant": "None",
                "most_infiltrating_tenant": "None"
            }

        total_count = len(exposures)
        cross_count = sum(1 for e in exposures if e.get("is_cross_tenant"))
        intra_count = total_count - cross_count

        # Formal TIFI Metric
        tifi = round(cross_count / total_count, 4) if total_count > 0 else 0.0

        # Construct Spillover Adjacency Matrix (Requester Tenant -> Victim Tenant)
        spillover_counts: Dict[str, Dict[str, int]] = {
            t_req: {t_vic: 0 for t_vic in tenant_names}
            for t_req in tenant_names
        }

        infiltrating_tally: Dict[str, int] = {t: 0 for t in tenant_names}
        impacted_tally: Dict[str, int] = {t: 0 for t in tenant_names}

        for exp in exposures:
            req_t = exp.get("requester_tenant_name", "Unknown")
            vic_t = exp.get("victim_tenant_name", "Unknown")

            if req_t in spillover_counts and vic_t in spillover_counts[req_t]:
                spillover_counts[req_t][vic_t] += 1
                if req_t != vic_t:
                    infiltrating_tally[req_t] = infiltrating_tally.get(req_t, 0) + 1
                    impacted_tally[vic_t] = impacted_tally.get(vic_t, 0) + 1

        most_infiltrating = max(infiltrating_tally.items(), key=lambda x: x[1])[0] if infiltrating_tally else "N/A"
        most_impacted = max(impacted_tally.items(), key=lambda x: x[1])[0] if impacted_tally else "N/A"

        spillover_df = pd.DataFrame.from_dict(spillover_counts, orient="index")

        return {
            "tifi_score": tifi,
            "tifi_percentage": round(tifi * 100, 1),
            "total_exposures": total_count,
            "cross_tenant_count": cross_count,
            "intra_tenant_count": intra_count,
            "tenant_names": tenant_names,
            "spillover_matrix": spillover_counts,
            "spillover_df": spillover_df,
            "most_impacted_tenant": most_impacted,
            "most_infiltrating_tenant": most_infiltrating,
            "isolation_status": "PERIMETER_BREACH" if tifi > 0.0 else "CONTAINED_INTRA_TENANT"
        }
    finally:
        db.close()


if __name__ == "__main__":
    m = compute_tenant_isolation_metrics()
    print("\n=== Multi-Tenant Isolation Analysis ===")
    print(f"Tenant Isolation Failure Index (TIFI): {m['tifi_score']} ({m['tifi_percentage']}%)")
    print(f"Cross-Tenant Breaches: {m['cross_tenant_count']} / {m['total_exposures']}")
    print(f"Most Infiltrating Tenant: {m['most_infiltrating_tenant']}")
    print(f"Most Impacted Victim Tenant: {m['most_impacted_tenant']}")
    print("\nInter-Tenant Spillover Matrix:\n", m["spillover_df"])
