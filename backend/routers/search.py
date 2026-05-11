from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from sqlalchemy import or_
from ..database import get_db
from ..models import Issue, Project, WikiPage, User
from .auth import get_current_user

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("/")
def global_search(q: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not q or len(q) < 2:
        return {"issues": [], "projects": [], "wikis": []}
    
    term = f"%{q}%"
    
    issues = db.query(Issue).filter(or_(Issue.title.ilike(term), Issue.description.ilike(term))).limit(10).all()
    projects = db.query(Project).filter(or_(Project.name.ilike(term), Project.description.ilike(term))).limit(5).all()
    wikis = db.query(WikiPage).filter(or_(WikiPage.title.ilike(term), WikiPage.content.ilike(term))).limit(5).all()
    
    return {
        "issues": [{"id": i.id, "title": i.title, "project_id": i.project_id} for i in issues],
        "projects": [{"id": p.id, "name": p.name} for p in projects],
        "wikis": [{"id": w.id, "title": w.title, "project_id": w.project_id} for w in wikis]
    }
