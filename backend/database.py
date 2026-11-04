from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base, Tenant, User, Order, Document, APIRequest, ExposureRecord, EvidenceRecord


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "data" / "exposurelens.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


def init_db(force_recreate: bool = False):
    """Create database tables and seed baseline multi-tenant test data."""

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    if force_recreate:
        Base.metadata.drop_all(engine)

    Base.metadata.create_all(engine)

    db = SessionLocal()

    try:
        # Check if tenants exist; if not, populate demo data
        if db.query(Tenant).count() == 0:
            tenants = [
                Tenant(id=1, name="FinServe Global", domain="finserve.local", tier="Financial-Enterprise"),
                Tenant(id=2, name="HealthFirst Diagnostics", domain="healthfirst.local", tier="Healthcare-HIPAA"),
                Tenant(id=3, name="OmniRetail Commerce", domain="omniretail.local", tier="Retail-Standard")
            ]
            db.add_all(tenants)
            db.commit()

        if db.query(User).count() == 0:
            users = [
                User(id=101, username="alice", email="alice@finserve.local", phone="+1-555-0101", address="12 Park Street, Kolkata", role="analyst", tenant_id=1),
                User(id=102, username="bob", email="bob@finserve.local", phone="+1-555-0102", address="45 Marine Drive, Mumbai", role="manager", tenant_id=1),
                User(id=103, username="charlie", email="charlie@healthfirst.local", phone="+1-555-0103", address="78 MG Road, Bengaluru", role="doctor", tenant_id=2),
                User(id=104, username="diana", email="diana@healthfirst.local", phone="+1-555-0104", address="22 Residency Rd, Chennai", role="patient", tenant_id=2),
                User(id=105, username="eve", email="eve@omniretail.local", phone="+1-555-0105", address="99 Connaught Place, Delhi", role="auditor", tenant_id=3)
            ]
            db.add_all(users)
            db.commit()

        if db.query(Order).count() == 0:
            orders = [
                Order(id=1001, user_id=101, tenant_id=1, product="MacBook Pro M3", amount=149999.00, shipping_address="12 Park Street, Kolkata", payment_last4="4821", status="Delivered", sensitivity="HIGH", data_classification="PII_FINANCIAL"),
                Order(id=1002, user_id=102, tenant_id=1, product="iPhone 16 Pro Max", amount=119999.00, shipping_address="45 Marine Drive, Mumbai", payment_last4="7319", status="Processing", sensitivity="HIGH", data_classification="PII_FINANCIAL"),
                Order(id=1003, user_id=103, tenant_id=2, product="Clinical Ultrasound Unit", amount=350000.00, shipping_address="78 MG Road, Bengaluru", payment_last4="1654", status="Shipped", sensitivity="CRITICAL", data_classification="COMMERCIAL_MEDICAL"),
                Order(id=1004, user_id=101, tenant_id=1, product="Apple Watch Ultra", amount=89999.00, shipping_address="12 Park Street, Kolkata", payment_last4="9204", status="Delivered", sensitivity="MEDIUM", data_classification="COMMERCE"),
                Order(id=1005, user_id=102, tenant_id=1, product="iPad Pro 13-inch", amount=99999.00, shipping_address="45 Marine Drive, Mumbai", payment_last4="3387", status="Delivered", sensitivity="HIGH", data_classification="PII_FINANCIAL"),
                Order(id=1006, user_id=104, tenant_id=2, product="Cardiac Holter Monitor", amount=45000.00, shipping_address="22 Residency Rd, Chennai", payment_last4="5512", status="Processing", sensitivity="CRITICAL", data_classification="MEDICAL_DEVICE"),
                Order(id=1007, user_id=105, tenant_id=3, product="OmniPOS Smart Terminal", amount=28500.00, shipping_address="99 Connaught Place, Delhi", payment_last4="8820", status="Delivered", sensitivity="MEDIUM", data_classification="COMMERCE")
            ]
            db.add_all(orders)
            db.commit()

        if db.query(Document).count() == 0:
            documents = [
                Document(id=2001, user_id=101, tenant_id=1, title="Q3 Tax Audit and Asset Declaration", category="Taxation", content_summary="Personal tax filings, PAN metadata, bank interest disclosures, declared liquid assets of INR 4.2M.", sensitivity="CRITICAL", data_classification="PII_FINANCIAL_CONFIDENTIAL"),
                Document(id=2002, user_id=102, tenant_id=1, title="Executive Compensation & Stock Option Vesting", category="Human Resources", content_summary="Base salary INR 6.5M/yr, equity grant vesting schedule, executive bonus formula.", sensitivity="CRITICAL", data_classification="INTERNAL_CONFIDENTIAL"),
                Document(id=2003, user_id=103, tenant_id=2, title="Histopathology Diagnostic Laboratory Report", category="Medical Records", content_summary="Patient biopsy results, cell cytology, physician notes, prescribed oncology regimen.", sensitivity="CRITICAL", data_classification="PHI_HIPAA_PROTECTED"),
                Document(id=2004, user_id=104, tenant_id=2, title="Cardiology ECHO Ultrasound Summary", category="Medical Records", content_summary="Ejection fraction 58%, mitral valve examination findings, outpatient medication protocol.", sensitivity="CRITICAL", data_classification="PHI_HIPAA_PROTECTED"),
                Document(id=2005, user_id=105, tenant_id=3, title="Q4 Supplier SLA Master Agreement", category="Contracts", content_summary="Wholesale tier pricing discounts, logistics penalties, distributor banking coordinates.", sensitivity="HIGH", data_classification="COMMERCIAL_CONFIDENTIAL")
            ]
            db.add_all(documents)
            db.commit()

        print("[OK] ExposureLens multi-tenant database initialized.")

    finally:
        db.close()


if __name__ == "__main__":
    init_db(force_recreate=True)
