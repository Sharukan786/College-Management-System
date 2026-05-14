import uuid
from datetime import datetime

async def create_invoice_from_payroll(db, payroll_id: str, payroll: dict):
    # Check if invoice already exists
    existing = await db["invoices"].find_one({"payroll_id": payroll_id})
    if existing:
        return existing
        
    invoice_id = "INV-PAY-" + str(uuid.uuid4())[:8].upper()
    
    invoice = {
        "invoice_id": invoice_id,
        "payroll_id": payroll_id,
        "staff_name": payroll.get("staffName") or payroll.get("name"),
        "staff_id": payroll.get("staffId"),
        "pay_period": payroll.get("payPeriodDetailed") or payroll.get("payMonth") or "N/A",
        "total_amount": payroll.get("netPay") or 0,
        "payment_status": "Draft",
        "generated_date": datetime.now(),
        "items": [
            {"description": "Basic Salary", "amount": payroll.get("basicSalary", 0)},
            {"description": "HRA", "amount": payroll.get("hra", 0)},
            {"description": "Allowances", "amount": payroll.get("allowance", 0)},
            {"description": "Deductions (PF, Tax, etc.)", "amount": -(payroll.get("deductions", 0))}
        ]
    }
    
    result = await db["invoices"].insert_one(invoice)
    created = await db["invoices"].find_one({"_id": result.inserted_id})
    return created
