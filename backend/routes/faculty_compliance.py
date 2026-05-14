from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timedelta
from typing import List, Optional
from backend.models.faculty_compliance import (
    ComplianceRequirement, ContractInfo, ComplianceRecord, ComplianceAlert,
    Certification, DocumentExpiry, ComplianceDashboard, AlertType, AlertPriority
)
from backend.utils.mongo import get_database

router = APIRouter(prefix="/api/faculty", tags=["Compliance & Alerts"])
db = None

async def init_db():
    global db
    if db is None:
        db = await get_database()

# Default compliance requirements
DEFAULT_REQUIREMENTS = {
    "ANNUAL_REVIEW": {
        "name": "Annual Performance Review",
        "category": "contractual",
        "frequency": "annually",
        "deadline_months_before": 2,
        "is_mandatory": True
    },
    "CONTRACT_RENEWAL": {
        "name": "Contract Renewal",
        "category": "contractual",
        "frequency": "custom",
        "deadline_months_before": 3,
        "is_mandatory": True
    },
    "COMPLIANCE_TRAINING": {
        "name": "Mandatory Compliance Training",
        "category": "institutional",
        "frequency": "annually",
        "deadline_months_before": 1,
        "is_mandatory": True
    },
    "BACKGROUND_CHECK": {
        "name": "Background Check Renewal",
        "category": "regulatory",
        "frequency": "every 3 years",
        "deadline_months_before": 6,
        "is_mandatory": True
    }
}

@router.post("/{faculty_id}/contract")
async def add_faculty_contract(faculty_id: str, contract_data: ContractInfo):
    """Add or update faculty contract information"""
    await init_db()
    
    try:
        contract_doc = contract_data.dict()
        contract_doc["_id"] = contract_data.contract_id
        
        await db.faculty_contracts.update_one(
            {"faculty_id": faculty_id},
            {"$set": contract_doc},
            upsert=True
        )
        
        # Create contract expiry alert
        days_until_expiry = (contract_data.end_date - datetime.utcnow()).days
        
        if days_until_expiry <= 180:  # Alert if expiring within 6 months
            priority = AlertPriority.CRITICAL if days_until_expiry <= 30 else AlertPriority.HIGH
            
            alert = {
                "_id": f"ALERT-{datetime.utcnow().timestamp()}",
                "faculty_id": faculty_id,
                "alert_type": "contract_renewal",
                "priority": priority,
                "title": "Contract Renewal Required",
                "description": f"Faculty contract expires on {contract_data.end_date}",
                "related_record_id": contract_data.contract_id,
                "due_date": contract_data.end_date.isoformat(),
                "days_remaining": days_until_expiry,
                "action_required": "Review and renew contract",
                "created_at": datetime.utcnow().isoformat()
            }
            await db.compliance_alerts.insert_one(alert)
        
        return {"contract_id": contract_data.contract_id, "status": "saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{faculty_id}/contract")
async def get_faculty_contract(faculty_id: str):
    """Get faculty contract information"""
    await init_db()
    
    try:
        contract = await db.faculty_contracts.find_one({"faculty_id": faculty_id})
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        return contract
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{faculty_id}/compliance-requirement")
async def add_compliance_requirement(faculty_id: str, requirement_data: ComplianceRequirement):
    """Add compliance requirement for faculty"""
    await init_db()
    
    try:
        req_doc = requirement_data.dict()
        req_doc["_id"] = requirement_data.requirement_id
        
        await db.compliance_requirements.insert_one(req_doc)
        
        # Create compliance record
        due_date = datetime.utcnow() + timedelta(days=30)
        
        record = {
            "_id": f"COMP-{datetime.utcnow().timestamp()}",
            "faculty_id": faculty_id,
            "requirement_id": requirement_data.requirement_id,
            "requirement_name": requirement_data.name,
            "requirement_category": requirement_data.category,
            "due_date": due_date.isoformat(),
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        
        await db.compliance_records.insert_one(record)
        
        return {"requirement_id": requirement_data.requirement_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{faculty_id}/compliance-records")
async def get_compliance_records(faculty_id: str, status: Optional[str] = None):
    """Get compliance records for faculty"""
    await init_db()
    
    try:
        query = {"faculty_id": faculty_id}
        if status:
            query["status"] = status
        
        records = await db.compliance_records.find(query).sort("due_date", 1).to_list(None)
        
        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{faculty_id}/compliance-records/{record_id}/complete")
async def mark_compliance_complete(faculty_id: str, record_id: str, completion_data: dict):
    """Mark compliance requirement as completed"""
    await init_db()
    
    try:
        now = datetime.utcnow()
        
        update_data = {
            "status": "completed",
            "completion_date": now.isoformat(),
            "evidence_document": completion_data.get("evidence_document"),
            "notes": completion_data.get("notes")
        }
        
        await db.compliance_records.update_one(
            {"_id": record_id, "faculty_id": faculty_id},
            {"$set": update_data}
        )
        
        return {"record_id": record_id, "status": "marked_complete"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{faculty_id}/certification")
async def add_faculty_certification(faculty_id: str, certification_data: Certification):
    """Add certification for faculty"""
    await init_db()
    
    try:
        cert_doc = certification_data.dict()
        cert_doc["_id"] = certification_data.certification_id
        
        await db.faculty_certifications.insert_one(cert_doc)
        
        # Create alert if expiring within 3 months
        days_until_expiry = (certification_data.expiry_date - datetime.utcnow()).days
        
        if days_until_expiry <= 90:
            alert = {
                "_id": f"ALERT-{datetime.utcnow().timestamp()}",
                "faculty_id": faculty_id,
                "alert_type": "certification_expiry",
                "priority": AlertPriority.HIGH,
                "title": f"{certification_data.certification_name} Expiring",
                "description": f"Certification expires on {certification_data.expiry_date}",
                "related_record_id": certification_data.certification_id,
                "due_date": certification_data.expiry_date.isoformat(),
                "days_remaining": days_until_expiry,
                "action_required": "Renew certification",
                "created_at": datetime.utcnow().isoformat()
            }
            await db.compliance_alerts.insert_one(alert)
        
        return {"certification_id": certification_data.certification_id, "status": "added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{faculty_id}/certifications")
async def get_faculty_certifications(faculty_id: str):
    """Get all certifications for faculty"""
    await init_db()
    
    try:
        certifications = await db.faculty_certifications.find(
            {"faculty_id": faculty_id}
        ).to_list(None)
        
        return certifications
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{faculty_id}/alerts")
async def get_faculty_alerts(faculty_id: str, priority: Optional[str] = None):
    """Get compliance alerts for faculty"""
    await init_db()
    
    try:
        query = {"faculty_id": faculty_id, "is_resolved": False}
        if priority:
            query["priority"] = priority
        
        alerts = await db.compliance_alerts.find(query).sort("due_date", 1).to_list(None)
        
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{faculty_id}/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(faculty_id: str, alert_id: str, acknowledged_by: str):
    """Acknowledge compliance alert"""
    await init_db()
    
    try:
        await db.compliance_alerts.update_one(
            {"_id": alert_id, "faculty_id": faculty_id},
            {
                "$set": {
                    "is_acknowledged": True,
                    "acknowledged_by": acknowledged_by,
                    "acknowledged_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        return {"alert_id": alert_id, "status": "acknowledged"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{faculty_id}/compliance-dashboard")
async def get_compliance_dashboard(faculty_id: str):
    """Get compliance dashboard for faculty"""
    await init_db()
    
    try:
        # Get all compliance records
        records = await db.compliance_records.find(
            {"faculty_id": faculty_id}
        ).to_list(None)
        
        # Get contract info
        contract = await db.faculty_contracts.find_one({"faculty_id": faculty_id})
        
        # Get alerts
        alerts = await db.compliance_alerts.find(
            {"faculty_id": faculty_id, "is_resolved": False}
        ).to_list(None)
        
        # Get expiring documents
        certs = await db.faculty_certifications.find(
            {"faculty_id": faculty_id, "is_active": True}
        ).to_list(None)
        
        expiring_docs = [c["certification_name"] for c in certs 
                        if (c.get("expiry_date") - datetime.utcnow()).days <= 90]
        
        # Calculate statistics
        total_requirements = len(records)
        completed = len([r for r in records if r.get("status") == "completed"])
        pending = len([r for r in records if r.get("status") == "pending"])
        overdue = len([r for r in records if r.get("status") == "overdue"])
        
        compliance_percentage = (completed / total_requirements * 100) if total_requirements > 0 else 0
        
        dashboard = {
            "faculty_id": faculty_id,
            "total_requirements": total_requirements,
            "completed_requirements": completed,
            "pending_requirements": pending,
            "overdue_requirements": overdue,
            "compliance_percentage": round(compliance_percentage, 2),
            "critical_alerts": len([a for a in alerts if a.get("priority") == "critical"]),
            "high_alerts": len([a for a in alerts if a.get("priority") == "high"]),
            "expiring_documents": expiring_docs,
            "contract_expiry_date": contract.get("end_date") if contract else None,
            "total_alerts": len(alerts),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        return dashboard
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/department/{department_id}/compliance-report")
async def get_department_compliance_report(department_id: str):
    """Get compliance report for entire department"""
    await init_db()
    
    try:
        # Get all faculty in department
        faculty_list = await db.faculty.find({"department_id": department_id}).to_list(None)
        
        # Calculate compliance stats
        total_faculty = len(faculty_list)
        fully_compliant = 0
        critical_issues = 0
        
        for faculty in faculty_list:
            dashboard = await get_compliance_dashboard(faculty["_id"])
            if dashboard["compliance_percentage"] == 100:
                fully_compliant += 1
            if dashboard["critical_alerts"] > 0:
                critical_issues += 1
        
        report = {
            "department_id": department_id,
            "total_faculty": total_faculty,
            "fully_compliant_faculty": fully_compliant,
            "compliance_rate": round((fully_compliant / total_faculty * 100) if total_faculty > 0 else 0, 2),
            "faculty_with_critical_issues": critical_issues,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
