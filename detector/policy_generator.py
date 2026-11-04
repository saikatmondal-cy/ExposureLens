"""
ExposureLens Automated Defensive Policy & Virtual Patch Synthesizer.

Transforms reconstructed BOLA exposures into production-ready defensive guardrails:
1. Open Policy Agent (OPA) declarative Rego policy rules.
2. Framework-agnostic Python ownership & tenant boundary enforcement decorator.
3. SQL tenant-scoping query patch expressions.
"""

from typing import Any, Dict, List


def generate_opa_rego_policy(endpoints: List[str] = None) -> str:
    """Generate Open Policy Agent (OPA) Rego policy enforcing strict object ownership and tenant isolation."""
    rego_policy = """package exposurelens.authz

import future.keywords.in

# Default deny all access unless explicitly authorized
default allow = false

# Allow access if user is accessing their own resource within their verified tenant
allow {
    # 1. Requester must be authenticated
    input.requester.id != null
    input.requester.tenant_id != null

    # 2. Resource owner must match requester ID (Strict Object-Level Authorization)
    input.resource.owner_id == input.requester.id

    # 3. Tenant boundaries must match (Multi-Tenant Isolation)
    input.resource.tenant_id == input.requester.tenant_id

    # 4. HTTP Method check (Safe reads or approved mutations)
    input.http_method in ["GET", "POST", "PUT", "DELETE"]
}

# Reason string for audit logging when denied
deny_reason = "Object ownership boundary violated" {
    input.resource.owner_id != input.requester.id
}

deny_reason = "Cross-tenant isolation breach prevented" {
    input.resource.tenant_id != input.requester.tenant_id
}
"""
    return rego_policy


def generate_python_decorator_patch() -> str:
    """Synthesize production-grade Python authorization decorator for Flask/FastAPI."""
    decorator_code = """from functools import wraps
from flask import request, jsonify, abort
from backend.database import SessionLocal
from backend.models import User, Order, Document

def enforce_ownership_and_tenant(resource_model):
    \"\"\"
    ExposureLens Automated Virtual Patch Decorator.
    Enforces:
    1. Requester owns target resource (requester_id == resource.owner_id)
    2. Requester belongs to identical tenant (requester_tenant == resource.tenant)
    \"\"\"
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Extract object ID from URL kwargs
            object_id = kwargs.get("order_id") or kwargs.get("doc_id") or kwargs.get("id")
            if not object_id:
                return jsonify({"error": "Missing resource identifier"}), 400

            # Extract authenticated requester identity
            user_id_hdr = request.headers.get("X-User-ID")
            if not user_id_hdr:
                return jsonify({"error": "Unauthorized: Authentication required"}), 401

            try:
                requester_id = int(user_id_hdr)
            except ValueError:
                return jsonify({"error": "Invalid credential format"}), 400

            db = SessionLocal()
            try:
                requester = db.query(User).filter(User.id == requester_id).first()
                if not requester:
                    return jsonify({"error": "Requester identity unknown"}), 401

                # Query target resource
                resource = db.query(resource_model).filter(resource_model.id == object_id).first()
                if not resource:
                    return jsonify({"error": "Resource not found"}), 404

                # CRITICAL SECURITY ASSERTION 1: Object Ownership Check (BOLA Remediation)
                if resource.user_id != requester.id:
                    return jsonify({
                        "error": "Forbidden: Object ownership violation",
                        "code": "BOLA_PREVENTED",
                        "object_id": object_id
                    }), 403

                # CRITICAL SECURITY ASSERTION 2: Tenant Isolation Check
                if hasattr(resource, "tenant_id") and resource.tenant_id != requester.tenant_id:
                    return jsonify({
                        "error": "Forbidden: Cross-tenant access denied",
                        "code": "TENANT_ISOLATION_ENFORCED"
                    }), 403

                # Access granted
                return fn(*args, **kwargs)

            finally:
                db.close()

        return wrapper
    return decorator


# Usage Example:
# @app.route("/api/orders/<int:order_id>", methods=["GET"])
# @enforce_ownership_and_tenant(Order)
# def get_order(order_id):
#     ...
"""
    return decorator_code


def generate_sql_tenant_scoping_patch() -> str:
    """Demonstrate SQL query rewriting to achieve defense-in-depth tenant scoping."""
    sql_patch = """-- ==============================================================================
-- DEFENSE-IN-DEPTH: SQL TENANT & OWNERSHIP SCOPING
-- Instead of:
-- SELECT * FROM orders WHERE id = :target_id;
--
-- Apply Mandatory Parameterized Scoping:
-- ==============================================================================

SELECT 
    orders.id,
    orders.product,
    orders.amount,
    orders.shipping_address,
    orders.payment_last4,
    orders.status,
    orders.tenant_id,
    orders.user_id
FROM orders
INNER JOIN users ON users.id = orders.user_id
WHERE orders.id = :requested_order_id
  AND orders.user_id = :authenticated_user_id       -- BOLA Gate: Ownership Match
  AND orders.tenant_id = :authenticated_tenant_id;   -- Tenant Gate: Isolation Match
"""
    return sql_patch


if __name__ == "__main__":
    rego = generate_opa_rego_policy()
    py = generate_python_decorator_patch()
    print("\n=== Automated Defensive Policy Synthesizer ===")
    print("OPA Rego Policy lines:", len(rego.splitlines()))
    print("Python Decorator lines:", len(py.splitlines()))
