from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from typing import List, Optional, Dict
from collections import Counter
from backend.models.faculty_publications import (
    Publication, PublicationMetrics, CitationMetric, ResearchProductivity,
    CollaborationNetwork, PublicationDashboard, ImpactReport, PublicationType
)
from backend.utils.mongo import get_database
import statistics

router = APIRouter(prefix="/api/faculty", tags=["Publication Analytics"])
db = None

async def init_db():
    global db
    if db is None:
        db = await get_database()

def calculate_h_index(citations_list: List[int]) -> float:
    """Calculate H-index from citations list"""
    if not citations_list:
        return 0
    sorted_citations = sorted(citations_list, reverse=True)
    h_index = 0
    for i, citations in enumerate(sorted_citations):
        if citations >= i + 1:
            h_index = i + 1
    return h_index

def calculate_g_index(citations_list: List[int]) -> float:
    """Calculate G-index from citations list"""
    if not citations_list:
        return 0
    sorted_citations = sorted(citations_list, reverse=True)
    g_index = 0
    cumulative_citations = 0
    for i, citations in enumerate(sorted_citations):
        cumulative_citations += citations
        if cumulative_citations >= (i + 1) ** 2:
            g_index = i + 1
    return g_index

@router.post("/{faculty_id}/publications")
async def add_publication(faculty_id: str, pub_data: Publication):
    """Add publication for faculty"""
    await init_db()
    
    try:
        pub_doc = pub_data.dict()
        pub_doc["_id"] = pub_data.pub_id
        pub_doc["faculty_id"] = faculty_id
        
        await db.faculty_publications.insert_one(pub_doc)
        
        return {"publication_id": pub_data.pub_id, "status": "added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{faculty_id}/publications")
async def get_faculty_publications(faculty_id: str, publication_type: Optional[str] = None, 
                                   start_year: Optional[int] = None, end_year: Optional[int] = None):
    """Get publications for faculty"""
    await init_db()
    
    try:
        query = {"faculty_id": faculty_id}
        
        if publication_type:
            query["publication_type"] = publication_type
        
        if start_year or end_year:
            year_query = {}
            if start_year:
                year_query["$gte"] = start_year
            if end_year:
                year_query["$lte"] = end_year
            query["publication_year"] = year_query
        
        publications = await db.faculty_publications.find(query).sort("publication_year", -1).to_list(None)
        
        return publications
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{faculty_id}/publications/{pub_id}/citations")
async def record_citation(faculty_id: str, pub_id: str, citation_data: CitationMetric):
    """Record a citation for a publication"""
    await init_db()
    
    try:
        # Verify publication exists
        pub = await db.faculty_publications.find_one({"_id": pub_id, "faculty_id": faculty_id})
        if not pub:
            raise HTTPException(status_code=404, detail="Publication not found")
        
        citation_doc = citation_data.dict()
        citation_doc["_id"] = citation_data.citation_id
        citation_doc["pub_id"] = pub_id
        
        await db.citations.insert_one(citation_doc)
        
        # Update publication citation count
        new_count = pub.get("citations_count", 0) + 1
        await db.faculty_publications.update_one(
            {"_id": pub_id},
            {"$set": {"citations_count": new_count}}
        )
        
        return {"citation_id": citation_data.citation_id, "status": "recorded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{faculty_id}/publication-metrics")
async def get_publication_metrics(faculty_id: str):
    """Get publication metrics for faculty"""
    await init_db()
    
    try:
        publications = await db.faculty_publications.find(
            {"faculty_id": faculty_id}
        ).to_list(None)
        
        if not publications:
            raise HTTPException(status_code=404, detail="No publications found")
        
        # Calculate metrics
        total_pubs = len(publications)
        by_type = {}
        citations_list = []
        open_access_count = 0
        first_author_count = 0
        corresponding_author_count = 0
        total_citations = 0
        impact_factors = []
        yearly_trend = {}
        
        for pub in publications:
            # By type
            pub_type = pub.get("publication_type", "unknown")
            by_type[pub_type] = by_type.get(pub_type, 0) + 1
            
            # Citations
            citations = pub.get("citations_count", 0)
            citations_list.append(citations)
            total_citations += citations
            
            # Open access
            if pub.get("is_open_access"):
                open_access_count += 1
            
            # Author position
            if pub.get("author_position") == 1:
                first_author_count += 1
            if pub.get("corresponding_author"):
                corresponding_author_count += 1
            
            # Impact factor
            if pub.get("impact_factor"):
                impact_factors.append(pub.get("impact_factor"))
            
            # Yearly trend
            year = pub.get("publication_year")
            yearly_trend[year] = yearly_trend.get(year, 0) + 1
        
        # Calculate indices
        h_index = calculate_h_index(citations_list)
        g_index = calculate_g_index(citations_list)
        
        # Get unique co-authors
        all_authors = []
        for pub in publications:
            all_authors.extend(pub.get("authors", []))
        unique_co_authors = len(set(all_authors))
        
        metrics = {
            "faculty_id": faculty_id,
            "total_publications": total_pubs,
            "by_type": by_type,
            "journal_publications": by_type.get("journal", 0),
            "conference_publications": by_type.get("conference", 0),
            "first_author_publications": first_author_count,
            "corresponding_author_publications": corresponding_author_count,
            "total_citations": total_citations,
            "average_citations_per_publication": round(total_citations / total_pubs, 2) if total_pubs > 0 else 0,
            "h_index": round(h_index, 2),
            "g_index": round(g_index, 2),
            "open_access_publications": open_access_count,
            "open_access_percentage": round((open_access_count / total_pubs * 100) if total_pubs > 0 else 0, 2),
            "average_impact_factor": round(statistics.mean(impact_factors), 2) if impact_factors else None,
            "yearly_publication_trend": yearly_trend,
            "unique_co_authors": unique_co_authors,
            "calculated_at": datetime.utcnow().isoformat()
        }
        
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{faculty_id}/publication-dashboard")
async def get_publication_dashboard(faculty_id: str):
    """Get comprehensive publication dashboard"""
    await init_db()
    
    try:
        publications = await db.faculty_publications.find(
            {"faculty_id": faculty_id}
        ).sort("publication_year", -1).to_list(None)
        
        if not publications:
            raise HTTPException(status_code=404, detail="No publications found")
        
        # Get metrics
        metrics = await get_publication_metrics(faculty_id)
        
        # Top 5 cited
        top_cited = sorted(publications, key=lambda x: x.get("citations_count", 0), reverse=True)[:5]
        top_cited_formatted = [
            {
                "title": p.get("title"),
                "citations": p.get("citations_count", 0),
                "pub_type": p.get("publication_type"),
                "year": p.get("publication_year")
            }
            for p in top_cited
        ]
        
        # Research areas
        research_areas = {}
        for pub in publications:
            area = pub.get("research_area", "General")
            research_areas[area] = research_areas.get(area, 0) + 1
        
        # Collaboration metrics
        all_authors = []
        for pub in publications:
            all_authors.extend(pub.get("authors", []))
        author_counts = Counter(all_authors)
        top_collaborators = [author for author, count in author_counts.most_common(5)]
        
        # Publication trend for chart
        yearly_data = {}
        for pub in publications:
            year = pub.get("publication_year")
            yearly_data[year] = yearly_data.get(year, 0) + 1
        
        trend_chart_data = [
            {"year": year, "publications": count}
            for year, count in sorted(yearly_data.items())
        ]
        
        dashboard = {
            "faculty_id": faculty_id,
            "total_publications": metrics["total_publications"],
            "publication_by_type": metrics["by_type"],
            "total_citations": metrics["total_citations"],
            "h_index": metrics["h_index"],
            "g_index": metrics["g_index"],
            "average_citations": metrics["average_citations_per_publication"],
            "publication_trend_chart_data": trend_chart_data,
            "top_5_cited_publications": top_cited_formatted,
            "research_areas_distribution": research_areas,
            "top_collaborators": top_collaborators,
            "open_access_percentage": metrics["open_access_percentage"],
            "first_author_percentage": round((metrics["first_author_publications"] / metrics["total_publications"] * 100) if metrics["total_publications"] > 0 else 0, 2),
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return dashboard
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{faculty_id}/research-productivity")
async def calculate_research_productivity(faculty_id: str, period: str, start_year: int, end_year: int):
    """Calculate research productivity metrics"""
    await init_db()
    
    try:
        publications = await db.faculty_publications.find({
            "faculty_id": faculty_id,
            "publication_year": {"$gte": start_year, "$lte": end_year}
        }).to_list(None)
        
        if not publications:
            raise HTTPException(status_code=404, detail="No publications in period")
        
        # Calculate metrics
        citations_list = [p.get("citations_count", 0) for p in publications]
        total_pubs = len(publications)
        total_citations = sum(citations_list)
        years_span = end_year - start_year + 1
        
        yearly_data = {}
        for pub in publications:
            year = pub.get("publication_year")
            yearly_data[year] = yearly_data.get(year, 0) + 1
        
        # Trend analysis
        years_list = sorted(yearly_data.keys())
        if len(years_list) > 1:
            first_period_avg = statistics.mean([yearly_data[y] for y in years_list[:len(years_list)//2]])
            last_period_avg = statistics.mean([yearly_data[y] for y in years_list[len(years_list)//2:]])
            if last_period_avg > first_period_avg * 1.1:
                trend = "increasing"
            elif last_period_avg < first_period_avg * 0.9:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        productivity = {
            "faculty_id": faculty_id,
            "period": period,
            "start_year": start_year,
            "end_year": end_year,
            "publications_count": total_pubs,
            "average_publications_per_year": round(total_pubs / years_span, 2),
            "citation_count": total_citations,
            "average_citations_per_publication": round(total_citations / total_pubs, 2) if total_pubs > 0 else 0,
            "h_index": calculate_h_index(citations_list),
            "publications_per_year_data": yearly_data,
            "productivity_score": min(100, round((total_pubs * 10 + total_citations * 2) / years_span, 2)),
            "trend": trend,
            "calculated_at": datetime.utcnow().isoformat()
        }
        
        return productivity
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/department/{department_id}/publication-analytics")
async def get_department_publication_analytics(department_id: str):
    """Get publication analytics for entire department"""
    await init_db()
    
    try:
        # Get all faculty in department
        faculty_list = await db.faculty.find({"department_id": department_id}).to_list(None)
        
        dept_total_pubs = 0
        dept_total_citations = 0
        dept_h_indices = []
        dept_by_type = {}
        top_researchers = []
        
        for faculty in faculty_list:
            try:
                metrics = await get_publication_metrics(faculty["_id"])
                dept_total_pubs += metrics.get("total_publications", 0)
                dept_total_citations += metrics.get("total_citations", 0)
                dept_h_indices.append(metrics.get("h_index", 0))
                
                # Aggregate by type
                for pub_type, count in metrics.get("by_type", {}).items():
                    dept_by_type[pub_type] = dept_by_type.get(pub_type, 0) + count
                
                # Track top researchers
                top_researchers.append({
                    "faculty_id": faculty["_id"],
                    "faculty_name": faculty.get("name"),
                    "publications": metrics.get("total_publications", 0),
                    "h_index": metrics.get("h_index", 0),
                    "citations": metrics.get("total_citations", 0)
                })
            except:
                continue
        
        # Sort top researchers
        top_researchers.sort(key=lambda x: x["h_index"], reverse=True)
        
        analytics = {
            "department_id": department_id,
            "total_faculty": len(faculty_list),
            "total_publications": dept_total_pubs,
            "total_citations": dept_total_citations,
            "average_publications_per_faculty": round(dept_total_pubs / len(faculty_list), 2) if faculty_list else 0,
            "average_h_index": round(statistics.mean(dept_h_indices), 2) if dept_h_indices else 0,
            "publication_by_type": dept_by_type,
            "top_10_researchers": top_researchers[:10],
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
