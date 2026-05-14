from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import uuid
from typing import List, Optional
from bson import ObjectId

from backend.db import get_db
from backend.utils.mongo import parse_object_id, serialize_doc
from backend.schemas.invoice import InvoiceUpdate, InvoiceResponse, InvoiceCreate
from backend.utils.invoice_utils import create_invoice_from_payroll

router = APIRouter(prefix="/api/invoices", tags=["Invoices"])

@router.get("", response_model=List[dict])
async def get_invoices():
    db = get_db()
    invoices = []
    async for inv in db["invoices"].find().sort("generated_date", -1):
        invoices.append(serialize_doc(inv))
    return invoices

@router.post("/generate-from-payroll/{payroll_id}")
async def generate_invoice_from_payroll(payroll_id: str):
    db = get_db()
    
    # Check if payroll record exists
    oid = parse_object_id(payroll_id)
    payroll = await db["payroll"].find_one({"_id": oid})
    if not payroll:
        raise HTTPException(status_code=404, detail="Payroll record not found")
    
    invoice = await create_invoice_from_payroll(db, payroll_id, payroll)
    return serialize_doc(invoice)

@router.patch("/{invoice_id}/status")
async def update_invoice_status(invoice_id: str, update: InvoiceUpdate):
    db = get_db()
    oid = parse_object_id(invoice_id)
    
    # Find active invoice
    invoice = await db["invoices"].find_one({"_id": oid})
    if not invoice:
        # Try finding by invoice_id string if _id fails
        invoice = await db["invoices"].find_one({"invoice_id": invoice_id})
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        oid = invoice["_id"]

    update_data = update.model_dump(exclude_unset=True)
    
    # Status transition logic (optional validation could go here)
    # Draft -> Processing -> Paid
    
    result = await db["invoices"].find_one_and_update(
        {"_id": oid},
        {"$set": update_data},
        return_document=True
    )
    
    # Update synchronized payroll status if linked
    if invoice.get("payroll_id"):
        payroll_id = invoice["payroll_id"]
        try:
            p_oid = parse_object_id(payroll_id)
            sync_res = await db["payroll"].update_one(
                {"_id": p_oid},
                {"$set": {"status": update.payment_status}}
            )
            if sync_res.matched_count > 0:
                print(f"Synchronized Payroll {payroll_id} status to {update.payment_status} (Modified: {sync_res.modified_count})")
            else:
                print(f"WARNING: Linked Payroll {payroll_id} not found during sync.")
        except Exception as e:
            print(f"ERROR: Failed to sync payroll status: {e}")

    return serialize_doc(result)

@router.delete("/{invoice_id}")
async def delete_invoice(invoice_id: str):
    db = get_db()
    try:
        oid = parse_object_id(invoice_id)
        result = await db["invoices"].delete_one({"_id": oid})
    except:
        result = await db["invoices"].delete_one({"invoice_id": invoice_id})
        
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    return {"message": "Invoice deleted"}