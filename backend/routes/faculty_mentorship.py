from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timedelta
from typing import List, Optional
from backend.models.faculty_mentorship import (
    MentorProfile, MenteeProfile, MentorshipMatch, MentorshipSession,
    MentorshipProgress, MentorshipStatus, MentorshipGoal
)
from backend.utils.mongo import get_database
import math

router = APIRouter(prefix="/api/faculty", tags=["Faculty Mentorship"])
db = None

async def init_db():
    global db
    if db is None:
        db = await get_database()

def calculate_match_score(mentor: dict, mentee: dict) -> tuple:
    """Calculate mentorship match score"""
    score = 0
    factors = {}
    
    # Expertise match (40%)
    mentor_expertise = set(mentor.get("expertise_areas", []))
    mentee_expertise = set(mentee.get("preferred_mentor_expertise", []))
    expertise_overlap = len(mentor_expertise & mentee_expertise)
    expertise_match = (expertise_overlap / len(mentee_expertise) * 100) if mentee_expertise else 0
    score += expertise_match * 0.4
    factors["expertise_match"] = round(expertise_match, 2)
    
    # Availability match (20%)
    mentor_hours = mentor.get("availability_hours_per_month", 0)
    mentee_hours = mentee.get("commitment_hours_per_month", 0)
    availability_match = min(100, (mentor_hours / max(mentee_hours, 1)) * 100)
    score += availability_match * 0.2
    factors["availability_match"] = round(availability_match, 2)
    
    # Goals alignment (20%)
    mentee_goals = set(str(g) for g in mentee.get("mentorship_goals", []))
    mentor_expertise_goals = {"research", "teaching", "career_development"}
    goals_match = len(mentee_goals & mentor_expertise_goals) / len(mentee_goals) * 100 if mentee_goals else 0
    score += goals_match * 0.2
    factors["goals_alignment"] = round(goals_match, 2)
    
    # Experience consideration (10%)
    experience = min(100, mentor.get("mentoring_experience_years", 0) * 10)
    score += experience * 0.1
    factors["mentor_experience"] = round(experience, 2)
    
    return round(score, 2), factors

@router.post("/{faculty_id}/mentor-profile")
async def create_mentor_profile(faculty_id: str, profile_data: MentorProfile):
    """Register faculty as a mentor"""
    await init_db()
    
    try:
        mentor_doc = profile_data.dict()
        mentor_doc["_id"] = f"MENTOR-{faculty_id}"
        mentor_doc["faculty_id"] = faculty_id
        
        await db.mentor_profiles.update_one(
            {"faculty_id": faculty_id},
            {"$set": mentor_doc},
            upsert=True
        )
        
        return {"status": "mentor_profile_created", "faculty_id": faculty_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{faculty_id}/mentor-profile")
async def get_mentor_profile(faculty_id: str):
    """Get mentor profile"""
    await init_db()
    
    try:
        profile = await db.mentor_profiles.find_one({"faculty_id": faculty_id})
        if not profile:
            raise HTTPException(status_code=404, detail="Mentor profile not found")
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{faculty_id}/mentee-profile")
async def create_mentee_profile(faculty_id: str, profile_data: MenteeProfile):
    """Register faculty as a mentee"""
    await init_db()
    
    try:
        mentee_doc = profile_data.dict()
        mentee_doc["_id"] = f"MENTEE-{faculty_id}"
        mentee_doc["faculty_id"] = faculty_id
        
        await db.mentee_profiles.update_one(
            {"faculty_id": faculty_id},
            {"$set": mentee_doc},
            upsert=True
        )
        
        return {"status": "mentee_profile_created", "faculty_id": faculty_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/find-mentorship-matches/{mentee_id}")
async def find_mentorship_matches(mentee_id: str, department_id: Optional[str] = None):
    """Find best mentor matches for a mentee"""
    await init_db()
    
    try:
        # Get mentee profile
        mentee_profile = await db.mentee_profiles.find_one({"faculty_id": mentee_id})
        if not mentee_profile:
            raise HTTPException(status_code=404, detail="Mentee profile not found")
        
        # Get available mentors
        query = {"max_mentees": {"$gt": 0}}
        if department_id:
            query["department_id"] = {"$ne": department_id}  # Cross-department mentorship preferred
        
        mentors = await db.mentor_profiles.find(query).to_list(None)
        
        # Calculate match scores
        matches = []
        for mentor in mentors:
            score, factors = calculate_match_score(mentor, mentee_profile)
            
            if score >= 70:  # Minimum threshold
                match = {
                    "mentor_id": mentor["faculty_id"],
                    "match_score": score,
                    "compatibility_factors": factors,
                    "mentor_expertise": mentor.get("expertise_areas", []),
                    "mentor_availability": mentor.get("availability_hours_per_month", 0)
                }
                matches.append(match)
        
        # Sort by match score
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        
        return {"mentee_id": mentee_id, "potential_matches": matches[:5]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-mentorship-match")
async def create_mentorship_match(match_data: dict):
    """Create a mentorship match"""
    await init_db()
    
    try:
        mentor_id = match_data.get("mentor_id")
        mentee_id = match_data.get("mentee_id")
        
        mentor = await db.mentor_profiles.find_one({"faculty_id": mentor_id})
        mentee = await db.mentee_profiles.find_one({"faculty_id": mentee_id})
        
        if not mentor or not mentee:
            raise HTTPException(status_code=404, detail="Mentor or mentee not found")
        
        score, factors = calculate_match_score(mentor, mentee)
        
        match_doc = {
            "_id": f"MM-{datetime.utcnow().timestamp()}",
            "mentor_id": mentor_id,
            "mentee_id": mentee_id,
            "mentor_name": mentor.get("mentor_name", "Unknown"),
            "mentee_name": mentee.get("mentee_name", "Unknown"),
            "department_id": match_data.get("department_id"),
            "match_score": score,
            "compatibility_factors": factors,
            "mentorship_goals": mentee.get("mentorship_goals", []),
            "status": "proposed",
            "duration_months": match_data.get("duration_months", 6),
            "meeting_frequency": match_data.get("meeting_frequency", "bi-weekly"),
            "created_at": datetime.utcnow().isoformat(),
            "created_by": match_data.get("created_by")
        }
        
        await db.mentorship_matches.insert_one(match_doc)
        
        return {"match_id": match_doc["_id"], "match_score": score, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/mentorship-match/{match_id}/activate")
async def activate_mentorship_match(match_id: str):
    """Activate a mentorship match"""
    await init_db()
    
    try:
        start_date = datetime.utcnow()
        duration = (await db.mentorship_matches.find_one({"_id": match_id})).get("duration_months", 6)
        end_date = start_date + timedelta(days=duration * 30)
        
        await db.mentorship_matches.update_one(
            {"_id": match_id},
            {
                "$set": {
                    "status": "active",
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }
        )
        
        return {"status": "activated", "match_id": match_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mentorship-matches/{faculty_id}")
async def get_mentorship_matches(faculty_id: str, role: str = "mentee"):
    """Get mentorship matches for faculty"""
    await init_db()
    
    try:
        if role == "mentee":
            matches = await db.mentorship_matches.find({"mentee_id": faculty_id}).to_list(None)
        else:
            matches = await db.mentorship_matches.find({"mentor_id": faculty_id}).to_list(None)
        
        return matches
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mentorship-session")
async def create_mentorship_session(session_data: dict):
    """Log a mentorship session"""
    await init_db()
    
    try:
        session_doc = {
            "_id": f"MS-{datetime.utcnow().timestamp()}",
            **session_data,
            "session_status": "completed",
            "created_at": datetime.utcnow().isoformat()
        }
        
        await db.mentorship_sessions.insert_one(session_doc)
        
        return {"session_id": session_doc["_id"], "status": "recorded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mentorship-sessions/{match_id}")
async def get_mentorship_sessions(match_id: str):
    """Get all sessions for a mentorship match"""
    await init_db()
    
    try:
        sessions = await db.mentorship_sessions.find(
            {"match_id": match_id}
        ).sort("session_date", -1).to_list(None)
        
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mentorship-progress/{match_id}")
async def create_progress_report(match_id: str, progress_data: dict):
    """Create mentorship progress report"""
    await init_db()
    
    try:
        match = await db.mentorship_matches.find_one({"_id": match_id})
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        
        progress_doc = {
            "_id": f"MP-{datetime.utcnow().timestamp()}",
            "match_id": match_id,
            "mentor_id": match["mentor_id"],
            "mentee_id": match["mentee_id"],
            **progress_data,
            "created_at": datetime.utcnow().isoformat()
        }
        
        await db.mentorship_progress.insert_one(progress_doc)
        
        return {"progress_id": progress_doc["_id"], "status": "recorded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mentorship-progress/{match_id}")
async def get_progress_reports(match_id: str):
    """Get progress reports for a mentorship match"""
    await init_db()
    
    try:
        reports = await db.mentorship_progress.find(
            {"match_id": match_id}
        ).sort("created_at", -1).to_list(None)
        
        return reports
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
