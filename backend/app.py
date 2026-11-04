import json
import uuid
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

from .database import init_db, SessionLocal
from .models import User, Order, Document, APIRequest


app = Flask(__name__)
CORS(app)


def log_api_request(
    requester_user_id: int,
    method: str,
    endpoint: str,
    resource_type: str,
    object_id: int | None,
    response_status: int,
    resource_owner_id: int | None,
    response_body_sample: dict | None = None
):
    """Store an enriched API request in the ExposureLens database."""

    db = SessionLocal()

    try:
        # Determine requester tenant
        requester = db.query(User).filter(User.id == requester_user_id).first()
        requester_tenant_id = requester.tenant_id if requester else None

        # Determine resource tenant
        resource_tenant_id = None
        if resource_owner_id:
            owner = db.query(User).filter(User.id == resource_owner_id).first()
            resource_tenant_id = owner.tenant_id if owner else None

        request_id_str = f"REQ-{uuid.uuid4().hex[:8].upper()}"
        body_sample_str = json.dumps(response_body_sample) if response_body_sample else None

        api_request = APIRequest(
            request_id=request_id_str,
            timestamp=datetime.now().isoformat(),
            requester_user_id=requester_user_id,
            requester_tenant_id=requester_tenant_id,
            method=method,
            endpoint=endpoint,
            resource_type=resource_type,
            object_id=object_id,
            response_status=response_status,
            resource_owner_id=resource_owner_id,
            resource_tenant_id=resource_tenant_id,
            response_body_sample=body_sample_str,
            ip_address=request.remote_addr or "127.0.0.1"
        )

        db.add(api_request)
        db.commit()
        return api_request.id

    finally:
        db.close()


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "application": "ExposureLens Lab API",
        "version": "2.0.0",
        "description": "Controlled environment for BOLA detection & exposure reconstruction research"
    })


@app.route("/api/my-orders", methods=["GET"])
def my_orders():
    """Legitimate endpoint: returns only orders belonging to requesting user."""
    user_id_header = request.headers.get("X-User-ID")
    if not user_id_header:
        return jsonify({"error": "X-User-ID header is required"}), 400

    try:
        user_id = int(user_id_header)
    except ValueError:
        return jsonify({"error": "X-User-ID must be an integer"}), 400

    db = SessionLocal()
    try:
        orders = db.query(Order).filter(Order.user_id == user_id).all()
        res_data = [
            {
                "order_id": o.id,
                "product": o.product,
                "amount": o.amount,
                "status": o.status,
                "sensitivity": o.sensitivity
            }
            for o in orders
        ]

        log_api_request(
            requester_user_id=user_id,
            method="GET",
            endpoint="/api/my-orders",
            resource_type="order",
            object_id=None,
            response_status=200,
            resource_owner_id=user_id,
            response_body_sample={"count": len(res_data), "owner": user_id}
        )

        return jsonify({"requester_user_id": user_id, "orders": res_data})
    finally:
        db.close()


@app.route("/api/orders/<int:order_id>", methods=["GET"])
def get_order_vulnerable(order_id):
    """
    INTENTIONALLY VULNERABLE ENDPOINT (BOLA).
    Returns order without verifying requester ownership.
    """
    user_id_header = request.headers.get("X-User-ID")
    if not user_id_header:
        return jsonify({"error": "X-User-ID header is required"}), 400

    try:
        requester_id = int(user_id_header)
    except ValueError:
        return jsonify({"error": "X-User-ID must be an integer"}), 400

    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            log_api_request(
                requester_user_id=requester_id,
                method="GET",
                endpoint=request.path,
                resource_type="order",
                object_id=order_id,
                response_status=404,
                resource_owner_id=None,
                response_body_sample={"error": "Order not found"}
            )
            return jsonify({"error": "Order not found"}), 404

        exposed_payload = {
            "order_id": order.id,
            "product": order.product,
            "amount": order.amount,
            "shipping_address": order.shipping_address,
            "payment_last4": order.payment_last4,
            "status": order.status,
            "owner_user_id": order.user_id,
            "tenant_id": order.tenant_id,
            "sensitivity": order.sensitivity,
            "classification": order.data_classification
        }

        # Log request with ownership and payload metadata
        log_api_request(
            requester_user_id=requester_id,
            method="GET",
            endpoint=request.path,
            resource_type="order",
            object_id=order.id,
            response_status=200,
            resource_owner_id=order.user_id,
            response_body_sample=exposed_payload
        )

        return jsonify(exposed_payload), 200
    finally:
        db.close()


@app.route("/api/documents/<int:doc_id>", methods=["GET"])
def get_document_vulnerable(doc_id):
    """
    INTENTIONALLY VULNERABLE ENDPOINT (BOLA).
    Returns confidential/medical documents without authorization checks.
    """
    user_id_header = request.headers.get("X-User-ID")
    if not user_id_header:
        return jsonify({"error": "X-User-ID header is required"}), 400

    try:
        requester_id = int(user_id_header)
    except ValueError:
        return jsonify({"error": "X-User-ID must be an integer"}), 400

    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            log_api_request(
                requester_user_id=requester_id,
                method="GET",
                endpoint=request.path,
                resource_type="document",
                object_id=doc_id,
                response_status=404,
                resource_owner_id=None,
                response_body_sample={"error": "Document not found"}
            )
            return jsonify({"error": "Document not found"}), 404

        exposed_payload = {
            "document_id": doc.id,
            "title": doc.title,
            "category": doc.category,
            "content_summary": doc.content_summary,
            "owner_user_id": doc.user_id,
            "tenant_id": doc.tenant_id,
            "sensitivity": doc.sensitivity,
            "classification": doc.data_classification
        }

        log_api_request(
            requester_user_id=requester_id,
            method="GET",
            endpoint=request.path,
            resource_type="document",
            object_id=doc.id,
            response_status=200,
            resource_owner_id=doc.user_id,
            response_body_sample=exposed_payload
        )

        return jsonify(exposed_payload), 200
    finally:
        db.close()


@app.route("/api/secure/orders/<int:order_id>", methods=["GET"])
def get_order_secure(order_id):
    """
    SECURE ENDPOINT (BOLA Remediated).
    Validates that the requester is the legitimate owner.
    """
    user_id_header = request.headers.get("X-User-ID")
    if not user_id_header:
        return jsonify({"error": "X-User-ID header is required"}), 400

    try:
        requester_id = int(user_id_header)
    except ValueError:
        return jsonify({"error": "X-User-ID must be an integer"}), 400

    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return jsonify({"error": "Order not found"}), 404

        # Ownership authorization check
        if order.user_id != requester_id:
            log_api_request(
                requester_user_id=requester_id,
                method="GET",
                endpoint=request.path,
                resource_type="order",
                object_id=order_id,
                response_status=403,
                resource_owner_id=order.user_id,
                response_body_sample={"error": "Forbidden: ownership boundary enforced"}
            )
            return jsonify({
                "error": "Forbidden: you do not have permission to access this resource",
                "object_id": order_id
            }), 403

        # Legitimate access
        payload = {
            "order_id": order.id,
            "product": order.product,
            "amount": order.amount,
            "status": order.status,
            "owner_user_id": order.user_id
        }
        log_api_request(
            requester_user_id=requester_id,
            method="GET",
            endpoint=request.path,
            resource_type="order",
            object_id=order.id,
            response_status=200,
            resource_owner_id=order.user_id,
            response_body_sample=payload
        )
        return jsonify(payload), 200
    finally:
        db.close()


@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """Return public information about a user."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "address": user.address,
            "tenant_id": user.tenant_id,
            "role": user.role
        })
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    print("Starting ExposureLens vulnerable API...")
    print("API: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
