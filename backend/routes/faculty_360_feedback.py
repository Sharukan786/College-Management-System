from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from typing import List, Optional
from backend.models.faculty_feedback import (
    FeedbackRound, Faculty360Feedback, FeedbackSummary, 
    FeedbackSourceType, FeedbackCategory
)
from backend.utils.mongo import get_database

router = APIRouter(prefix="/api/faculty", tags=["Faculty 360 Feedback"])
db = None

async def init_db():
    global db
    if db is None:
        db = await get_database()

@router.post("/{faculty_id}/feedback-rounds")
async def create_feedback_round(faculty_id: str, round_data: FeedbackRound):
    """Create a new 360-degree feedback round"""
    await init_db()
    
    try:
        round_doc = round_data.dict()
        round_doc["_id"] = f"FBROUND-{datetime.utcnow().timestamp()}"
        
        result = await db.faculty_feedback_rounds.insert_one(round_doc)
        return {"round_id": round_doc["_id"], "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{faculty_id}/feedback-rounds")
async def get_feedback_rounds(faculty_id: str, academic_year: Optional[str] = None):
    """Get all 360-feedback rounds for a faculty"""
    await init_db()
    
    try:
        query = {"faculty_id": faculty_id}
        if academic_year:
            query["academic_year"] = academic_year
        
        rounds = await db.faculty_feedback_rounds.find(query).to_list(None)
        return rounds
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{faculty_id}/feedback/{round_id}/submit")
async def submit_feedback(faculty_id: str, round_id: str, feedback: Faculty360Feedback):
    """Submit feedback for a faculty member"""
    await init_db()
    
    try:
        # Verify feedback round exists
        round_doc = await db.faculty_feedback_rounds.find_one({"_id": round_id})
        if not round_doc:
            raise HTTPException(status_code=404, detail="Feedback round not found")
        
        # Check if feedback is still open
        if not round_doc.get("is_active"):
            raise HTTPException(status_code=400, detail="Feedback round is closed")
        
        # Calculate overall rating
        ratings = [item.rating for item in feedback.feedback_items]
        overall_rating = sum(ratings) / len(ratings) if ratings else 0
        
        feedback_doc = feedback.dict()
        feedback_doc["_id"] = feedback.feedback_id
        feedback_doc["overall_rating"] = overall_rating
        feedback_doc["is_submitted"] = True
        feedback_doc["submitted_at"] = datetime.utcnow().isoformat()
        
        await db.faculty_360_feedback.insert_one(feedback_doc)
        
        return {"feedback_id": feedback.feedback_id, "status": "submitted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{faculty_id}/feedback-summary/{round_id}")
async def get_feedback_summary(faculty_id: str, round_id: str):
    """Get 360-feedback summary for a faculty member"""
    await init_db()
    
    try:
        # Get all feedback for this round
        feedbacks = await db.faculty_360_feedback.find({
            "faculty_id": faculty_id,
            "feedback_round_id": round_id,
            "is_submitted": True
        }).to_list(None)
        
        if not feedbacks:
            raise HTTPException(status_code=404, detail="No feedback found")
        
        # Calculate averages by source type
        peer_ratings = [f for f in feedbacks if f["source_type"] == "peer"]
        student_ratings = [f for f in feedbacks if f["source_type"] == "student"]
        supervisor_ratings = [f for f in feedbacks if f["source_type"] == "supervisor"]
        
        peer_avg = sum([f["overall_rating"] for f in peer_ratings]) / len(peer_ratings) if peer_ratings else None
        student_avg = sum([f["overall_rating"] for f in student_ratings]) / len(student_ratings) if student_ratings else None
        supervisor_avg = sum([f["overall_rating"] for f in supervisor_ratings]) / len(supervisor_ratings) if supervisor_ratings else None
        
        all_ratings = [f["overall_rating"] for f in feedbacks]
        overall_360_rating = sum(all_ratings) / len(all_ratings) if all_ratings else None
        
        # Category analysis
        category_ratings = {}
        for feedback in feedbacks:
            for item in feedback.get("feedback_items", []):
                cat = item["category"]
                if cat not in category_ratings:
                    category_ratings[cat] = []
                category_ratings[cat].append(item["rating"])
        
        category_avgs = {cat: sum(ratings)/len(ratings) for cat, ratings in category_ratings.items()}
        
        summary = {
            "faculty_id": faculty_id,
            "feedback_round_id": round_id,
            "peer_average": round(peer_avg, 2) if peer_avg else None,
            "student_average": round(student_avg, 2) if student_avg else None,
            "supervisor_average": round(supervisor_avg, 2) if supervisor_avg else None,
            "overall_360_rating": round(overall_360_rating, 2) if overall_360_rating else None,
            "category_ratings": {k: round(v, 2) for k, v in category_avgs.items()},
            "total_responses": len(feedbacks),
            "peer_responses": len(peer_ratings),
            "student_responses": len(student_ratings),
            "supervisor_responses": len(supervisor_ratings),
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{faculty_id}/feedback-history")
async def get_feedback_history(faculty_id: str):
    """Get historical 360-feedback data"""
    await init_db()
    
    try:
        history = await db.faculty_feedback_rounds.find(
            {"faculty_id": faculty_id}
        ).sort("start_date", -1).to_list(None)
        
        results = []
        for round_doc in history:
            summary = await get_feedback_summary(faculty_id, round_doc.get("_id"))
            results.append({
                "round": round_doc,
                "summary": summary
            })
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
