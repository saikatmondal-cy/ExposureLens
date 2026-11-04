from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    domain: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    tier: Mapped[str] = mapped_column(String(50), default="Enterprise")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    address: Mapped[str] = mapped_column(String(250), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="customer")
    tenant_id: Mapped[int | None] = mapped_column(ForeignKey("tenants.id"), nullable=True)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    tenant_id: Mapped[int | None] = mapped_column(ForeignKey("tenants.id"), nullable=True)
    product: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    shipping_address: Mapped[str] = mapped_column(String(250), nullable=False)
    payment_last4: Mapped[str] = mapped_column(String(4), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    sensitivity: Mapped[str] = mapped_column(String(30), default="HIGH")
    data_classification: Mapped[str] = mapped_column(String(50), default="PII_FINANCIAL")


class Document(Base):
    """Secondary resource to demonstrate multi-resource BOLA scenarios."""
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    tenant_id: Mapped[int | None] = mapped_column(ForeignKey("tenants.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    content_summary: Mapped[str] = mapped_column(Text, nullable=False)
    sensitivity: Mapped[str] = mapped_column(String(30), default="CRITICAL")
    data_classification: Mapped[str] = mapped_column(String(50), default="PII_MEDICAL_CONFIDENTIAL")


class APIRequest(Base):
    __tablename__ = "api_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    request_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    timestamp: Mapped[str] = mapped_column(String(50), nullable=False)
    requester_user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    requester_tenant_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    endpoint: Mapped[str] = mapped_column(String(250), nullable=False)
    resource_type: Mapped[str | None] = mapped_column(String(50), default="order")
    object_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_status: Mapped[int] = mapped_column(Integer, nullable=False)
    resource_owner_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    resource_tenant_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_body_sample: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), default="127.0.0.1")


class ExposureRecord(Base):
    """Structured reconstruction of a confirmed BOLA data exposure event."""
    __tablename__ = "exposure_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exposure_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    request_id: Mapped[int] = mapped_column(ForeignKey("api_requests.id"), nullable=False)
    requester_user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    victim_user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_id: Mapped[int] = mapped_column(Integer, nullable=False)
    endpoint: Mapped[str] = mapped_column(String(250), nullable=False)
    timestamp: Mapped[str] = mapped_column(String(50), nullable=False)
    requester_tenant_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    resource_tenant_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_cross_tenant: Mapped[bool] = mapped_column(Boolean, default=False)
    exposed_fields: Mapped[str] = mapped_column(Text, nullable=False)
    sensitivity_level: Mapped[str] = mapped_column(String(30), nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    risk_severity: Mapped[str] = mapped_column(String(20), default="MEDIUM")
    detection_rule: Mapped[str] = mapped_column(String(100), default="OWNERSHIP_MISMATCH_HTTP200")
    reconstruction_timestamp: Mapped[str] = mapped_column(String(50), nullable=False)


class EvidenceRecord(Base):
    """Verifiable evidence unit linked to an exposure record."""
    __tablename__ = "evidence_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    evidence_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    exposure_id: Mapped[str] = mapped_column(String(50), nullable=False)
    evidence_type: Mapped[str] = mapped_column(String(60), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    raw_data: Mapped[str] = mapped_column(Text, nullable=False)
    integrity_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    recorded_at: Mapped[str] = mapped_column(String(50), nullable=False)
