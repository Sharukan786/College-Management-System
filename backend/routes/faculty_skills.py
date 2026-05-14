from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from typing import List, Optional
from backend.models.faculty_skills import (
    Skill, SkillMatrix, SkillGapAnalysis, DepartmentSkillMap,
    TrainingRecommendation, SkillCategory, SkillLevel, SkillGap
)
from backend.utils.mongo import get_database

router = APIRouter(prefix="/api/faculty", tags=["Faculty Skills"])
db = None

async def init_db():
    global db
    if db is None:
        db = await get_database()

# Initialize default skills (can be called during system setup)
DEFAULT_SKILLS = {
    "TEACH001": {"name": "Active Learning", "category": "pedagogical", "is_critical": True},
    "TECH001": {"name": "Python Programming", "category": "technical", "is_critical": True},
    "TECH002": {"name": "Data Analysis", "category": "technical", "is_critical": False},
    "RES001": {"name": "Research Methodology", "category": "research", "is_critical": True},
    "DIG001": {"name": "Learning Management Systems", "category": "digital", "is_critical": True},
    "SOFT001": {"name": "Communication", "category": "soft_skills", "is_critical": True},
    "SOFT002": {"name": "Leadership", "category": "soft_skills", "is_critical": False},
    "ADM001": {"name": "Academic Administration", "category": "administrative", "is_critical": False},
}

@router.post("/{faculty_id}/skills")
async def add_faculty_skill(faculty_id: str, skill_data: dict):
    """Add a skill to faculty's skill matrix"""
    await init_db()
    
    try:
        skill_matrix = await db.faculty_skill_matrix.find_one({"faculty_id": faculty_id})
        
        if not skill_matrix:
            skill_matrix = {
                "_id": f"SM-{faculty_id}",
                "faculty_id": faculty_id,
                "skills": [],
                "total_skills": 0,
                "last_updated": datetime.utcnow().isoformat()
            }
            await db.faculty_skill_matrix.insert_one(skill_matrix)
        
        new_skill = {
            **skill_data,
            "last_updated": datetime.utcnow().isoformat()
        }
        
        await db.faculty_skill_matrix.update_one(
            {"faculty_id": faculty_id},
            {
                "$push": {"skills": new_skill},
                "$inc": {"total_skills": 1},
                "$set": {"last_updated": datetime.utcnow().isoformat()}
            }
        )
        
        return {"status": "skill_added", "skill_name": skill_data.get("skill_name")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{faculty_id}/skill-matrix")
async def get_skill_matrix(faculty_id: str):
    """Get faculty's skill matrix"""
    await init_db()
    
    try:
        matrix = await db.faculty_skill_matrix.find_one({"faculty_id": faculty_id})
        if not matrix:
            raise HTTPException(status_code=404, detail="Skill matrix not found")
        return matrix
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{faculty_id}/skill-gap-analysis")
async def analyze_skill_gaps(faculty_id: str, department_id: str, role: str):
    """Generate skill gap analysis for faculty"""
    await init_db()
    
    try:
        # Get faculty's current skills
        skill_matrix = await db.faculty_skill_matrix.find_one({"faculty_id": faculty_id})
        if not skill_matrix:
            raise HTTPException(status_code=404, detail="Faculty not found")
        
        # Get department's required skills
        dept_map = await db.department_skill_map.find_one({"department_id": department_id})
        if not dept_map:
            # Create default skill map if none exists
            dept_map = {
                "department_id": department_id,
                "required_skills": list(DEFAULT_SKILLS.keys()),
                "skill_coverage": {}
            }
        
        # Calculate gaps
        skill_gaps = []
        required_skills = dept_map.get("required_skills", [])
        faculty_skills = {s.get("skill_id"): s for s in skill_matrix.get("skills", [])}
        
        for skill_id in required_skills:
            if skill_id not in faculty_skills:
                # Missing skill = gap
                gap = {
                    "skill_id": skill_id,
                    "skill_name": DEFAULT_SKILLS.get(skill_id, {}).get("name", "Unknown"),
                    "category": DEFAULT_SKILLS.get(skill_id, {}).get("category", "technical"),
                    "current_level": "beginner",
                    "required_level": "advanced",
                    "gap_severity": "high",
                    "priority": 4,
                    "recommended_training": ["Online Course", "Workshop"]
                }
                skill_gaps.append(gap)
            else:
                faculty_skill = faculty_skills[skill_id]
                current = faculty_skill.get("current_level")
                if current in ["beginner", "intermediate"]:
                    gap = {
                        "skill_id": skill_id,
                        "skill_name": faculty_skill.get("skill_name"),
                        "category": faculty_skill.get("category"),
                        "current_level": current,
                        "required_level": "advanced",
                        "gap_severity": "medium",
                        "priority": 3,
                        "recommended_training": ["Advanced Workshop"]
                    }
                    skill_gaps.append(gap)
        
        # Calculate gap coverage score (% of required skills with advanced level)
        covered_skills = len([s for s in faculty_skills.values() if s.get("current_level") in ["advanced", "expert"]])
        gap_coverage_score = (covered_skills / len(required_skills) * 100) if required_skills else 0
        
        analysis = {
            "_id": f"SGA-{faculty_id}-{datetime.utcnow().timestamp()}",
            "faculty_id": faculty_id,
            "department_id": department_id,
            "role": role,
            "academic_year": str(datetime.utcnow().year),
            "skill_gaps": skill_gaps,
            "critical_gaps": len([g for g in skill_gaps if g["gap_severity"] == "critical"]),
            "gap_coverage_score": round(gap_coverage_score, 2),
            "estimated_training_hours": len(skill_gaps) * 20,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        await db.faculty_skill_gap_analysis.insert_one(analysis)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{faculty_id}/skill-gap-analysis")
async def get_skill_gap_analysis(faculty_id: str):
    """Get latest skill gap analysis for faculty"""
    await init_db()
    
    try:
        analysis = await db.faculty_skill_gap_analysis.find_one(
            {"faculty_id": faculty_id},
            sort=[("generated_at", -1)]
        )
        if not analysis:
            raise HTTPException(status_code=404, detail="No analysis found")
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/department/{department_id}/skill-map")
async def get_department_skill_map(department_id: str):
    """Get department-wide skill coverage"""
    await init_db()
    
    try:
        map_doc = await db.department_skill_map.find_one({"department_id": department_id})
        if not map_doc:
            # Create default map
            map_doc = {
                "_id": f"DSM-{department_id}",
                "department_id": department_id,
                "required_skills": list(DEFAULT_SKILLS.keys()),
                "skill_coverage": {skill_id: 0 for skill_id in DEFAULT_SKILLS.keys()},
                "created_at": datetime.utcnow().isoformat()
            }
            await db.department_skill_map.insert_one(map_doc)
        
        # Calculate coverage percentages
        faculty_list = await db.faculty.find({"department_id": department_id}).to_list(None)
        
        coverage = {}
        for skill_id in map_doc.get("required_skills", []):
            faculty_with_skill = 0
            for faculty in faculty_list:
                matrix = await db.faculty_skill_matrix.find_one({"faculty_id": faculty.get("_id")})
                if matrix:
                    if any(s.get("skill_id") == skill_id and s.get("current_level") in ["advanced", "expert"] 
                           for s in matrix.get("skills", [])):
                        faculty_with_skill += 1
            
            coverage[skill_id] = {
                "skill_name": DEFAULT_SKILLS.get(skill_id, {}).get("name", "Unknown"),
                "coverage_percentage": round((faculty_with_skill / len(faculty_list) * 100) if faculty_list else 0, 2),
                "faculty_count": faculty_with_skill
            }
        
        return {
            "department_id": department_id,
            "total_faculty": len(faculty_list),
            "skill_coverage": coverage,
            "critical_shortages": [sid for sid, cov in coverage.items() if cov["coverage_percentage"] < 50]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{faculty_id}/training-recommendation")
async def create_training_recommendation(faculty_id: str, recommendation_data: dict):
    """Create training recommendation for skill gap"""
    await init_db()
    
    try:
        rec = {
            "_id": f"TR-{datetime.utcnow().timestamp()}",
            **recommendation_data,
            "faculty_id": faculty_id,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        
        await db.training_recommendations.insert_one(rec)
        return {"status": "recommendation_created", "recommendation_id": rec["_id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{faculty_id}/training-recommendations")
async def get_training_recommendations(faculty_id: str, status: Optional[str] = None):
    """Get training recommendations for faculty"""
    await init_db()
    
    try:
        query = {"faculty_id": faculty_id}
        if status:
            query["status"] = status
        
        recommendations = await db.training_recommendations.find(query).to_list(None)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
