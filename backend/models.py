from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Statement(Base):
    __tablename__ = "statements"
    
    id = Column(Integer, primary_key=True, index=True)
    bank_name = Column(String(100), nullable=False)
    card_variant = Column(String(200))
    last_4_digits = Column(String(4))
    billing_cycle_start = Column(String(50))
    billing_cycle_end = Column(String(50))
    due_date = Column(String(50))
    total_amount_due = Column(Float)
    currency = Column(String(10), default="INR")
    raw_text = Column(Text)
    filename = Column(String(255))
    upload_timestamp = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "bank_name": self.bank_name,
            "card_variant": self.card_variant,
            "last_4_digits": self.last_4_digits,
            "billing_cycle": f"{self.billing_cycle_start} to {self.billing_cycle_end}",
            "due_date": self.due_date,
            "total_amount_due": self.total_amount_due,
            "currency": self.currency,
            "filename": self.filename,
            "upload_timestamp": self.upload_timestamp.isoformat() if self.upload_timestamp else None
        }