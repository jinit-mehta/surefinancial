from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import tempfile
import os
from pathlib import Path

from utils.database import get_db
from utils.pdf_utils import extract_text_hybrid, detect_bank
from parsers import get_parser
from models import Statement

router = APIRouter()

@router.post("/upload")
async def upload_statement(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and parse a credit card statement PDF"""
    
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Save uploaded file temporarily
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Extract text from PDF
        text = extract_text_hybrid(tmp_path)
        
        if not text or len(text) < 100:
            os.unlink(tmp_path)
            raise HTTPException(status_code=400, detail="Could not extract text from PDF. File may be corrupted or image-based.")
        
        # Detect bank
        bank = detect_bank(text)
        if not bank:
            os.unlink(tmp_path)
            raise HTTPException(status_code=400, detail="Could not detect bank. Supported banks: HDFC, ICICI, SBI, Axis, AMEX")
        
        # Get appropriate parser
        parser = get_parser(bank, text)
        if not parser:
            os.unlink(tmp_path)
            raise HTTPException(status_code=400, detail=f"Parser not available for {bank}")
        
        # Parse statement
        parsed_data = parser.parse()
        
        # Save to database
        statement = Statement(
            bank_name=parsed_data.get("bank_name"),
            card_variant=parsed_data.get("card_variant"),
            last_4_digits=parsed_data.get("last_4_digits"),
            billing_cycle_start=parsed_data.get("billing_cycle_start"),
            billing_cycle_end=parsed_data.get("billing_cycle_end"),
            due_date=parsed_data.get("due_date"),
            total_amount_due=parsed_data.get("total_amount_due"),
            currency=parsed_data.get("currency", "INR"),
            raw_text=text[:5000],  # Store first 5000 chars
            filename=file.filename
        )
        
        db.add(statement)
        db.commit()
        db.refresh(statement)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        return {
            "success": True,
            "message": "Statement parsed successfully",
            "data": statement.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        if 'tmp_path' in locals():
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.get("/history")
async def get_history(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get upload history"""
    statements = db.query(Statement).order_by(Statement.upload_timestamp.desc()).limit(limit).all()
    return {
        "success": True,
        "count": len(statements),
        "data": [stmt.to_dict() for stmt in statements]
    }

@router.get("/statement/{statement_id}")
async def get_statement(
    statement_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific statement by ID"""
    statement = db.query(Statement).filter(Statement.id == statement_id).first()
    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")
    return {
        "success": True,
        "data": statement.to_dict()
    }

@router.delete("/statement/{statement_id}")
async def delete_statement(
    statement_id: int,
    db: Session = Depends(get_db)
):
    """Delete a statement"""
    statement = db.query(Statement).filter(Statement.id == statement_id).first()
    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")
    
    db.delete(statement)
    db.commit()
    
    return {
        "success": True,
        "message": "Statement deleted successfully"
    }