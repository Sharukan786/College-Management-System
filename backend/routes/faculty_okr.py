from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from typing import List, Optional
from backend.models.faculty_okr import (
    Objective, KeyResult, OKRCycle, KPITemplate, KPIReview,
    DepartmentKPIMetrics, PerformanceRating, ObjectiveStatus, KPICategory
)
from backend.utils.mongo import get_database

router = APIRouter(prefix="/api/faculty", tags=["OKR/KPI Tracking"])
db = None

async def init_db():
    global db
    if db is None:
        db = await get_database()

@router.post("/okr-cycle")
async def create_okr_cycle(cycle_data: OKRCycle):
    """Create a new OKR cycle"""
    await init_db()
    
    try:
        cycle_doc = cycle_data.dict()
        cycle_doc["_id"] = cycle_data.cycle_id
        
        await db.okr_cycles.insert_one(cycle_doc)
        
        return {"cycle_id": cycle_data.cycle_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/okr-cycles")
async def get_okr_cycles(department_id: Optional[str] = None):
    """Get all OKR cycles"""
    await init_db()
    
    try:
        query = {}
        if department_id:
            query["department_id"] = department_id
        
        cycles = await db.okr_cycles.find(query).sort("start_date", -1).to_list(None)
        return cycles
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{faculty_id}/objectives/{cycle_id}")
async def create_objective(faculty_id: str, cycle_id: str, objective_data: Objective):
    """Create objectives for faculty in a specific OKR cycle"""
    await init_db()
    
    try:
        # Verify cycle exists
        cycle = await db.okr_cycles.find_one({"_id": cycle_id})
        if not cycle:
            raise HTTPException(status_code=404, detail="OKR cycle not found")
        
        objective_doc = objective_data.dict()
        objective_doc["_id"] = objective_data.objective_id
        objective_doc["faculty_id"] = faculty_id
        objective_doc["cycle_id"] = cycle_id
        objective_doc["owner_id"] = faculty_id
        
        await db.faculty_objectives.insert_one(objective_doc)
        
        return {"objective_id": objective_data.objective_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{faculty_id}/objectives/{cycle_id}")
async def get_faculty_objectives(faculty_id: str, cycle_id: str):
    """Get objectives for faculty in a cycle"""
    await init_db()
    
    try:
        objectives = await db.faculty_objectives.find({
            "faculty_id": faculty_id,
            "cycle_id": cycle_id
        }).to_list(None)
        
        return objectives
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{faculty_id}/objectives/{objective_id}/update-progress")
async def update_objective_progress(faculty_id: str, objective_id: str, progress_data: dict):
    """Update progress on an objective"""
    await init_db()
    
    try:
        objective = await db.faculty_objectives.find_one({"_id": objective_id, "faculty_id": faculty_id})
        if not objective:
            raise HTTPException(status_code=404, detail="Objective not found")
        
        # Update key results
        updated_key_results = []
        total_weighted_score = 0
        total_weight = 0
        
        for kr in objective.get("key_results", []):
            kr_id = kr.get("kr_id")
            if kr_id in progress_data.get("key_results_progress", {}):
                kr["current_value"] = progress_data["key_results_progress"][kr_id]
                
                # Calculate progress percentage
                target = kr.get("target_value", 1)
                current = kr.get("current_value", 0)
                kr["progress_percentage"] = min(100, (current / target * 100)) if target > 0 else 0
                
                # Update status
                if kr["progress_percentage"] >= 100:
                    kr["status"] = ObjectiveStatus.COMPLETED
                elif kr["progress_percentage"] >= 50:
                    kr["status"] = ObjectiveStatus.ON_TRACK
                else:
                    kr["status"] = ObjectiveStatus.IN_PROGRESS
                
                # Calculate weighted score
                weight = kr.get("weighting", 1)
                kr_score = (kr["progress_percentage"] / 100) * 5  # 0-5 scale
                total_weighted_score += kr_score * weight
                total_weight += weight
            
            updated_key_results.append(kr)
        
        # Calculate overall objective score
        overall_score = total_weighted_score / total_weight if total_weight > 0 else 0
        
        # Determine status
        if overall_score >= 4.5:
            status = ObjectiveStatus.COMPLETED
        elif overall_score >= 3:
            status = ObjectiveStatus.ON_TRACK
        else:
            status = ObjectiveStatus.IN_PROGRESS
        
        await db.faculty_objectives.update_one(
            {"_id": objective_id},
            {
                "$set": {
                    "key_results": updated_key_results,
                    "overall_score": round(overall_score, 2),
                    "status": status,
                    "updated_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        return {"objective_id": objective_id, "overall_score": round(overall_score, 2), "status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{faculty_id}/kpi-review/{objective_id}")
async def create_kpi_review(faculty_id: str, objective_id: str, review_data: dict):
    """Create KPI review for faculty"""
    await init_db()
    
    try:
        objective = await db.faculty_objectives.find_one({"_id": objective_id})
        if not objective:
            raise HTTPException(status_code=404, detail="Objective not found")
        
        review_doc = {
            "_id": f"KPIR-{datetime.utcnow().timestamp()}",
            "objective_id": objective_id,
            "faculty_id": faculty_id,
            **review_data,
            "review_date": datetime.utcnow().isoformat(),
            "approval_status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        
        await db.kpi_reviews.insert_one(review_doc)
        
        return {"review_id": review_doc["_id"], "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{faculty_id}/kpi-reviews/{cycle_id}")
async def get_kpi_reviews(faculty_id: str, cycle_id: str):
    """Get KPI reviews for faculty"""
    await init_db()
    
    try:
        # Get objectives in cycle
        objectives = await db.faculty_objectives.find({
            "faculty_id": faculty_id,
            "cycle_id": cycle_id
        }).to_list(None)
        
        objective_ids = [obj.get("_id") for obj in objectives]
        
        reviews = await db.kpi_reviews.find({
            "objective_id": {"$in": objective_ids}
        }).sort("review_date", -1).to_list(None)
        
        return reviews
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/kpi-template")
async def create_kpi_template(template_data: KPITemplate):
    """Create KPI template"""
    await init_db()
    
    try:
        template_doc = template_data.dict()
        template_doc["_id"] = template_data.template_id
        
        await db.kpi_templates.insert_one(template_doc)
        
        return {"template_id": template_data.template_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/kpi-templates")
async def get_kpi_templates(category: Optional[str] = None, department_id: Optional[str] = None):
    """Get KPI templates"""
    await init_db()
    
    try:
        query = {}
        if category:
            query["category"] = category
        if department_id:
            query["$or"] = [{"department_id": department_id}, {"department_id": None}]
        
        templates = await db.kpi_templates.find(query).to_list(None)
        return templates
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/performance-rating/{faculty_id}/{cycle_id}")
async def create_performance_rating(faculty_id: str, cycle_id: str, rating_data: dict):
    """Create performance rating for faculty"""
    await init_db()
    
    try:
        # Calculate rating based on OKR score
        objectives = await db.faculty_objectives.find({
            "faculty_id": faculty_id,
            "cycle_id": cycle_id
        }).to_list(None)
        
        if objectives:
            okr_scores = [obj.get("overall_score", 0) for obj in objectives]
            avg_okr_score = sum(okr_scores) / len(okr_scores) if okr_scores else 0
        else:
            avg_okr_score = 0
        
        rating_doc = {
            "_id": f"PR-{datetime.utcnow().timestamp()}",
            "faculty_id": faculty_id,
            "cycle_id": cycle_id,
            "okr_score": round(avg_okr_score, 2),
            **rating_data,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Determine rating level
        overall = rating_doc.get("overall_rating", 0)
        if overall >= 4.5:
            rating_doc["rating_level"] = "exceptional"
            rating_doc["promotion_eligible"] = True
        elif overall >= 4:
            rating_doc["rating_level"] = "exceeds"
            rating_doc["promotion_eligible"] = True
        elif overall >= 3:
            rating_doc["rating_level"] = "meets"
        elif overall >= 2:
            rating_doc["rating_level"] = "developing"
        else:
            rating_doc["rating_level"] = "needs_improvement"
        
        await db.performance_ratings.insert_one(rating_doc)
        
        return {"rating_id": rating_doc["_id"], "rating_level": rating_doc["rating_level"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance-ratings/{faculty_id}")
async def get_performance_ratings(faculty_id: str):
    """Get performance ratings for faculty"""
    await init_db()
    
    try:
        ratings = await db.performance_ratings.find(
            {"faculty_id": faculty_id}
        ).sort("created_at", -1).to_list(None)
        
        return ratings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/department/{department_id}/kpi-metrics/{cycle_id}")
async def get_department_kpi_metrics(department_id: str, cycle_id: str):
    """Get department-wide KPI metrics"""
    await init_db()
    
    try:
        # Get all faculty in department
        faculty_list = await db.faculty.find({"department_id": department_id}).to_list(None)
        
        total_objectives = 0
        completed_objectives = 0
        on_track_objectives = 0
        at_risk_objectives = 0
        category_performance = {}
        
        for faculty in faculty_list:
            objectives = await db.faculty_objectives.find({
                "faculty_id": faculty["_id"],
                "cycle_id": cycle_id
            }).to_list(None)
            
            for obj in objectives:
                total_objectives += 1
                status = obj.get("status")
                if status == ObjectiveStatus.COMPLETED:
                    completed_objectives += 1
                elif status == ObjectiveStatus.ON_TRACK:
                    on_track_objectives += 1
                elif status == ObjectiveStatus.AT_RISK:
                    at_risk_objectives += 1
                
                category = obj.get("category")
                if category not in category_performance:
                    category_performance[category] = {"total": 0, "score": 0}
                category_performance[category]["total"] += 1
                category_performance[category]["score"] += obj.get("overall_score", 0)
        
        # Calculate averages
        category_avgs = {}
        for category, data in category_performance.items():
            if data["total"] > 0:
                category_avgs[category] = round(data["score"] / data["total"], 2)
        
        dept_avg_score = sum(category_avgs.values()) / len(category_avgs) if category_avgs else 0
        
        metrics = {
            "department_id": department_id,
            "cycle_id": cycle_id,
            "total_objectives": total_objectives,
            "completed_objectives": completed_objectives,
            "on_track_objectives": on_track_objectives,
            "at_risk_objectives": at_risk_objectives,
            "department_avg_score": round(dept_avg_score, 2),
            "category_performance": category_avgs,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
