from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from typing import List, Optional
from backend.models.faculty_research import (
    ResearchProject, FundingGrant, ResearchCollaborator, ResearchMilestone,
    ResearchPublication, ResearchCollaborationNetwork, ResearchStatus, FundingStatus
)
from backend.utils.mongo import get_database

router = APIRouter(prefix="/api/faculty", tags=["Research Collaboration"])
db = None

async def init_db():
    global db
    if db is None:
        db = await get_database()

@router.post("/{faculty_id}/research-projects")
async def create_research_project(faculty_id: str, project_data: ResearchProject):
    """Create a new research project"""
    await init_db()
    
    try:
        project_doc = project_data.dict()
        project_doc["_id"] = project_data.project_id
        
        if not project_doc.get("principal_investigator_id"):
            project_doc["principal_investigator_id"] = faculty_id
        
        await db.research_projects.insert_one(project_doc)
        
        return {"project_id": project_data.project_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{faculty_id}/research-projects")
async def get_faculty_research_projects(faculty_id: str, status: Optional[str] = None):
    """Get research projects for faculty (as PI or collaborator)"""
    await init_db()
    
    try:
        query = {
            "$or": [
                {"principal_investigator_id": faculty_id},
                {"co_investigators": faculty_id}
            ]
        }
        
        if status:
            query["status"] = status
        
        projects = await db.research_projects.find(query).sort("created_at", -1).to_list(None)
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{faculty_id}/research-projects/{project_id}/collaborators")
async def add_project_collaborator(faculty_id: str, project_id: str, collaborator_data: ResearchCollaborator):
    """Add collaborator to research project"""
    await init_db()
    
    try:
        # Verify project exists
        project = await db.research_projects.find_one({"_id": project_id})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        collaborator_doc = collaborator_data.dict()
        collaborator_doc["_id"] = collaborator_data.collaborator_id
        collaborator_doc["project_id"] = project_id
        
        await db.research_collaborators.insert_one(collaborator_doc)
        
        # Update project's co_investigators list if applicable
        if collaborator_data.role == "co-investigator":
            await db.research_projects.update_one(
                {"_id": project_id},
                {"$addToSet": {"co_investigators": collaborator_data.faculty_id}}
            )
        
        return {"collaborator_id": collaborator_data.collaborator_id, "status": "added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/research-projects/{project_id}/collaborators")
async def get_project_collaborators(project_id: str):
    """Get all collaborators for a research project"""
    await init_db()
    
    try:
        collaborators = await db.research_collaborators.find(
            {"project_id": project_id}
        ).to_list(None)
        return collaborators
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{faculty_id}/funding-grants")
async def create_funding_grant(faculty_id: str, grant_data: FundingGrant):
    """Submit funding grant for research project"""
    await init_db()
    
    try:
        grant_doc = grant_data.dict()
        grant_doc["_id"] = grant_data.grant_id
        grant_doc["faculty_id"] = faculty_id
        
        await db.funding_grants.insert_one(grant_doc)
        
        return {"grant_id": grant_data.grant_id, "status": "submitted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{faculty_id}/funding-grants")
async def get_faculty_funding_grants(faculty_id: str, status: Optional[str] = None):
    """Get funding grants for faculty"""
    await init_db()
    
    try:
        query = {
            "$or": [
                {"faculty_id": faculty_id},
                {"co_investigators": faculty_id}
            ]
        }
        
        if status:
            query["status"] = status
        
        grants = await db.funding_grants.find(query).sort("submission_date", -1).to_list(None)
        
        # Calculate total funded amount
        total_funded = sum([g["grant_amount"] for g in grants if g.get("status") == "funded"])
        
        return {
            "grants": grants,
            "total_funded": total_funded,
            "count": len(grants)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/funding-grants/{grant_id}/status")
async def update_grant_status(grant_id: str, new_status: str):
    """Update funding grant status"""
    await init_db()
    
    try:
        if new_status not in ["submitted", "approved", "rejected", "funded", "completed"]:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        update_data = {"status": new_status}
        if new_status == "approved":
            update_data["approval_date"] = datetime.utcnow().isoformat()
        
        await db.funding_grants.update_one(
            {"_id": grant_id},
            {"$set": update_data}
        )
        
        return {"grant_id": grant_id, "status": new_status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/research-projects/{project_id}/milestones")
async def create_project_milestone(project_id: str, milestone_data: ResearchMilestone):
    """Create milestone for research project"""
    await init_db()
    
    try:
        milestone_doc = milestone_data.dict()
        milestone_doc["_id"] = milestone_data.milestone_id
        milestone_doc["project_id"] = project_id
        
        await db.research_milestones.insert_one(milestone_doc)
        
        return {"milestone_id": milestone_data.milestone_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/research-projects/{project_id}/milestones")
async def get_project_milestones(project_id: str):
    """Get milestones for research project"""
    await init_db()
    
    try:
        milestones = await db.research_milestones.find(
            {"project_id": project_id}
        ).sort("scheduled_date", 1).to_list(None)
        
        return milestones
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/research-projects/{project_id}/publications")
async def add_project_publication(project_id: str, publication_data: ResearchPublication):
    """Add publication to research project"""
    await init_db()
    
    try:
        pub_doc = publication_data.dict()
        pub_doc["_id"] = publication_data.publication_id
        pub_doc["project_id"] = project_id
        
        await db.research_publications.insert_one(pub_doc)
        
        # Update project publication count
        await db.research_projects.update_one(
            {"_id": project_id},
            {"$inc": {"publications_achieved": 1}}
        )
        
        return {"publication_id": publication_data.publication_id, "status": "added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/research-projects/{project_id}/publications")
async def get_project_publications(project_id: str):
    """Get publications for research project"""
    await init_db()
    
    try:
        publications = await db.research_publications.find(
            {"project_id": project_id}
        ).sort("publication_date", -1).to_list(None)
        
        return publications
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{faculty_id}/research-collaboration-network")
async def get_research_collaboration_network(faculty_id: str):
    """Get faculty's research collaboration network"""
    await init_db()
    
    try:
        # Get all projects where faculty is PI or collaborator
        projects = await db.research_projects.find({
            "$or": [
                {"principal_investigator_id": faculty_id},
                {"co_investigators": faculty_id}
            ]
        }).to_list(None)
        
        # Count collaborators
        collaborators_set = set()
        active_projects = 0
        for project in projects:
            active_projects += 1 if project.get("status") == "active" else 0
            collaborators_set.update(project.get("co_investigators", []))
        
        # Get publications
        publications = await db.research_publications.find(
            {"project_id": {"$in": [p["_id"] for p in projects]}}
        ).to_list(None)
        
        # Get grants
        grants = await db.funding_grants.find({
            "$or": [
                {"faculty_id": faculty_id},
                {"co_investigators": faculty_id}
            ]
        }).to_list(None)
        
        total_grant_amount = sum([g["grant_amount"] for g in grants if g.get("status") == "funded"])
        
        # Count collaborations
        all_collaborators = await db.research_collaborators.find(
            {"project_id": {"$in": [p["_id"] for p in projects]}}
        ).to_list(None)
        
        internal_collab = len([c for c in all_collaborators if not c.get("is_external")])
        external_collab = len([c for c in all_collaborators if c.get("is_external")])
        
        network = {
            "faculty_id": faculty_id,
            "collaborator_count": len(collaborators_set),
            "active_projects": active_projects,
            "total_projects": len(projects),
            "total_publications": len(publications),
            "total_grant_amount": total_grant_amount,
            "internal_collaborations": internal_collab,
            "external_collaborations": external_collab,
            "recent_publications": publications[-5:] if publications else []
        }
        
        return network
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/research-projects/{project_id}/analytics")
async def get_project_analytics(project_id: str):
    """Get analytics for research project"""
    await init_db()
    
    try:
        project = await db.research_projects.find_one({"_id": project_id})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        collaborators = await db.research_collaborators.find(
            {"project_id": project_id}
        ).to_list(None)
        
        publications = await db.research_publications.find(
            {"project_id": project_id}
        ).to_list(None)
        
        grants = await db.funding_grants.find(
            {"project_id": project_id}
        ).to_list(None)
        
        milestones = await db.research_milestones.find(
            {"project_id": project_id}
        ).to_list(None)
        
        analytics = {
            "project_id": project_id,
            "project_title": project.get("title"),
            "status": project.get("status"),
            "collaborator_count": len(collaborators),
            "publication_count": len(publications),
            "publication_target": project.get("publications_target"),
            "total_funding": sum([g["grant_amount"] for g in grants]),
            "funded_grants": len([g for g in grants if g.get("status") == "funded"]),
            "total_citations": sum([p.get("citations_count", 0) for p in publications]),
            "milestones_completed": len([m for m in milestones if m.get("status") == "completed"]),
            "milestones_total": len(milestones),
            "project_start": project.get("start_date"),
            "project_end": project.get("end_date")
        }
        
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
