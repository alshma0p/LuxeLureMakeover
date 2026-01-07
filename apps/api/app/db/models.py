from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    referral_code = Column(String, unique=True, index=True)
    invited_by = Column(String, ForeignKey("users.id"), nullable=True)
    wallet_balance = Column(Integer, default=0)
    referral_completed = Column(Integer, default=0)

    scans = relationship("Scan", back_populates="user")


class Scan(Base):
    __tablename__ = "scans"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    predicted_label = Column(String)
    confidence = Column(Float)
    attributes = Column(String)
    unlocked = Column(Boolean, default=False)
    unlocked_via = Column(String, default="none")
    model_name = Column(String)
    model_version_hash = Column(String)

    user = relationship("User", back_populates="scans")


class WalletLedger(Base):
    __tablename__ = "wallet_ledger"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    amount = Column(Integer)
    type = Column(String)
    description = Column(String)


class MinimalLog(Base):
    __tablename__ = "minimal_logs"

    id = Column(String, primary_key=True, index=True)
    request_id = Column(String)
    route = Column(String)
    method = Column(String)
    status_code = Column(Integer)
    latency_ms = Column(Integer)
    user_id = Column(String, nullable=True)
    error_code = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
