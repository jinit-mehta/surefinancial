from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io
import csv

from utils.database import get_db
from models import Statement

router = APIRouter()

@router.get("/export/{statement_id}")
async def export_statement_csv(
    statement_id: int,
    db: Session = Depends(get_db)
):
    """Export a statement as CSV"""
    statement = db.query(Statement).filter(Statement.id == statement_id).first()
    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow([
        "Bank Name", "Card Variant", "Last 4 Digits", 
        "Billing Cycle Start", "Billing Cycle End", 
        "Due Date", "Total Amount Due", "Currency"
    ])
    
    # Write data
    writer.writerow([
        statement.bank_name,
        statement.card_variant,
        statement.last_4_digits,
        statement.billing_cycle_start,
        statement.billing_cycle_end,
        statement.due_date,
        statement.total_amount_due,
        statement.currency
    ])
    
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=statement_{statement_id}.csv"}
    )

@router.get("/export/all")
async def export_all_statements_csv(
    db: Session = Depends(get_db)
):
    """Export all statements as CSV"""
    statements = db.query(Statement).order_by(Statement.upload_timestamp.desc()).all()
    
    if not statements:
        raise HTTPException(status_code=404, detail="No statements found")
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow([
        "ID", "Bank Name", "Card Variant", "Last 4 Digits", 
        "Billing Cycle Start", "Billing Cycle End", 
        "Due Date", "Total Amount Due", "Currency", "Upload Date"
    ])
    
    # Write data
    for stmt in statements:
        writer.writerow([
            stmt.id,
            stmt.bank_name,
            stmt.card_variant,
            stmt.last_4_digits,
            stmt.billing_cycle_start,
            stmt.billing_cycle_end,
            stmt.due_date,
            stmt.total_amount_due,
            stmt.currency,
            stmt.upload_timestamp.strftime("%Y-%m-%d %H:%M:%S") if stmt.upload_timestamp else ""
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=all_statements.csv"}
    )

@router.get("/stats")
async def get_statistics(db: Session = Depends(get_db)):
    """Get statistics about parsed statements"""
    from sqlalchemy import func
    
    total_statements = db.query(func.count(Statement.id)).scalar()
    total_due = db.query(func.sum(Statement.total_amount_due)).scalar() or 0
    
    bank_breakdown = db.query(
        Statement.bank_name,
        func.count(Statement.id).label('count'),
        func.sum(Statement.total_amount_due).label('total_due')
    ).group_by(Statement.bank_name).all()
    
    return {
        "success": True,
        "data": {
            "total_statements": total_statements,
            "total_amount_due": round(total_due, 2),
            "bank_breakdown": [
                {
                    "bank": bank,
                    "count": count,
                    "total_due": round(total or 0, 2)
                }
                for bank, count, total in bank_breakdown
            ]
        }
    }