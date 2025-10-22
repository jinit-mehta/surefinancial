from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import json

DB_URL = "sqlite:///parser_results.db"
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class ParseResult(Base):
    __tablename__ = "parse_results"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    issuer = Column(String)
    card_variant = Column(String)
    last4 = Column(String)
    billing_start = Column(String)
    billing_end = Column(String)
    due_date = Column(String)
    amount_due = Column(String)
    raw_text = Column(Text)
    metadata = Column(Text)  # JSON dump of full parse result
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def save_result(filename: str, result: dict):
    session = SessionLocal()
    pr = ParseResult(
        filename=filename,
        issuer=result.get("issuer"),
        card_variant=result.get("card_variant"),
        last4=result.get("last4"),
        billing_start=result.get("billing_start"),
        billing_end=result.get("billing_end"),
        due_date=result.get("due_date"),
        amount_due=result.get("amount_due"),
        raw_text=result.get("raw_text_snippet") or result.get("raw_text") or "",
        metadata=json.dumps(result)
    )
    session.add(pr)
    session.commit()
    session.refresh(pr)
    session.close()
    return pr.id
