from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Workspace, User, WorkspaceMember
from ..schemas.workspaces import WorkspaceCreate, Workspace as WorkspaceSchema
from ..schemas.project_entities import WorkspaceMemberCreate, WorkspaceMember as WorkspaceMemberSchema
from .auth import get_current_user

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])

@router.get("/", response_model=List[WorkspaceSchema])
def get_workspaces(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Filter workspaces to ones where user is a member, or user is admin
    if current_user.is_admin:
        return db.query(Workspace).all()
        
    member_workspaces = db.query(WorkspaceMember.workspace_id).filter(WorkspaceMember.user_id == current_user.id).all()
    workspace_ids = [w[0] for w in member_workspaces]
    
    # Temporarily also return all if no members exist to avoid locking everyone out during migration
    total_members = db.query(WorkspaceMember).count()
    if total_members == 0:
        return db.query(Workspace).all()
        
    return db.query(Workspace).filter(Workspace.id.in_(workspace_ids)).all()

@router.post("/", response_model=WorkspaceSchema)
def create_workspace(workspace: WorkspaceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_workspace = Workspace(**workspace.model_dump())
    db.add(db_workspace)
    db.commit()
    db.refresh(db_workspace)
    
    # Automatically make creator an admin member
    db_member = WorkspaceMember(workspace_id=db_workspace.id, user_id=current_user.id, role="admin")
    db.add(db_member)
    db.commit()
    
    return db_workspace

@router.get("/{workspace_id}", response_model=WorkspaceSchema)
def get_workspace(workspace_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace

@router.delete("/{workspace_id}")
def delete_workspace(workspace_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    db.delete(workspace)
    db.commit()
    return {"message": "Workspace deleted successfully"}

@router.get("/{workspace_id}/members", response_model=List[WorkspaceMemberSchema])
def get_workspace_members(workspace_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    members = db.query(WorkspaceMember).filter(WorkspaceMember.workspace_id == workspace_id).all()
    return members

@router.post("/{workspace_id}/members", response_model=WorkspaceMemberSchema)
def add_workspace_member(workspace_id: int, member: WorkspaceMemberCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if member.workspace_id != workspace_id:
        raise HTTPException(status_code=400, detail="Workspace ID mismatch")
    
    existing = db.query(WorkspaceMember).filter(WorkspaceMember.workspace_id == workspace_id, WorkspaceMember.user_id == member.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="User is already a member")
        
    db_member = WorkspaceMember(**member.model_dump())
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member
