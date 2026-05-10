from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
import os
import shutil
import uuid
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import Project, Issue, Board, Component, Version, WikiPage, User, Attachment, Comment, TimeLog
from ..schemas.project_entities import (
    IssueCreate, Issue as IssueSchema,
    AttachmentSchema, CommentCreate, CommentSchema,
    BoardCreate, Board as BoardSchema,
    ComponentCreate, Component as ComponentSchema,
    VersionCreate, Version as VersionSchema,
    WikiPageCreate, WikiPage as WikiPageSchema
)
from .auth import get_current_user
from ..email_service import notify_issue_update

router = APIRouter(prefix="/projects", tags=["Project Entities"])

# --- Issues ---
@router.get("/{project_id}/issues", response_model=List[IssueSchema])
def get_issues(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Issue).filter(Issue.project_id == project_id).all()

@router.get("/{project_id}/issues/{issue_id}", response_model=IssueSchema)
def get_issue(project_id: int, issue_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    issue = db.query(Issue).filter(Issue.id == issue_id, Issue.project_id == project_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue

@router.post("/{project_id}/issues", response_model=IssueSchema)
def create_issue(project_id: int, issue: IssueCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if issue.project_id != project_id:
        raise HTTPException(status_code=400, detail="Project ID mismatch")
    
    issue_data = issue.model_dump(exclude={'send_email'})
    db_issue = Issue(**issue_data, reporter_id=current_user.id)
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    
    if getattr(issue, 'send_email', False):
        recipients = [current_user.email]
        if issue.assignee_id:
            assignee = db.query(User).filter(User.id == issue.assignee_id).first()
            if assignee and assignee.email:
                recipients.append(assignee.email)
        notify_issue_update(
            issue_title=db_issue.title,
            action="Created",
            details=f"A new issue was created by {current_user.username}.",
            recipient_emails=recipients
        )
        
    return db_issue

from pydantic import BaseModel
class StatusUpdate(BaseModel):
    status: str
    send_email: Optional[bool] = False

@router.patch("/{project_id}/issues/{issue_id}/status", response_model=IssueSchema)
def update_issue_status(project_id: int, issue_id: int, status_update: StatusUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    issue = db.query(Issue).filter(Issue.id == issue_id, Issue.project_id == project_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    old_status = issue.status
    issue.status = status_update.status
    db.commit()
    db.refresh(issue)
    
    if status_update.send_email:
        recipients = []
        reporter = db.query(User).filter(User.id == issue.reporter_id).first()
        if reporter and reporter.email: recipients.append(reporter.email)
        if issue.assignee_id:
            assignee = db.query(User).filter(User.id == issue.assignee_id).first()
            if assignee and assignee.email: recipients.append(assignee.email)
            
        notify_issue_update(
            issue_title=issue.title,
            action="Status Updated",
            details=f"Status changed from {old_status} to {issue.status} by {current_user.username}.",
            recipient_emails=recipients
        )
        
    return issue

class AssigneeUpdate(BaseModel):
    assignee_id: Optional[int] = None
    send_email: Optional[bool] = False

@router.patch("/{project_id}/issues/{issue_id}/assignee", response_model=IssueSchema)
def update_issue_assignee(project_id: int, issue_id: int, assignee_update: AssigneeUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    issue = db.query(Issue).filter(Issue.id == issue_id, Issue.project_id == project_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    issue.assignee_id = assignee_update.assignee_id
    db.commit()
    db.refresh(issue)
    
    if assignee_update.send_email:
        recipients = []
        reporter = db.query(User).filter(User.id == issue.reporter_id).first()
        if reporter and reporter.email: recipients.append(reporter.email)
        if issue.assignee_id:
            assignee = db.query(User).filter(User.id == issue.assignee_id).first()
            if assignee and assignee.email: recipients.append(assignee.email)
            
        notify_issue_update(
            issue_title=issue.title,
            action="Assignee Updated",
            details=f"Assignee was updated by {current_user.username}.",
            recipient_emails=recipients
        )
        
    return issue

from ..schemas.project_entities import ScheduleUpdate

@router.patch("/{project_id}/issues/{issue_id}/schedule", response_model=IssueSchema)
def update_issue_schedule(project_id: int, issue_id: int, schedule_update: ScheduleUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    issue = db.query(Issue).filter(Issue.id == issue_id, Issue.project_id == project_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    issue.start_date = schedule_update.start_date
    issue.end_date = schedule_update.end_date
    db.commit()
    db.refresh(issue)
    
    if schedule_update.send_email:
        recipients = []
        reporter = db.query(User).filter(User.id == issue.reporter_id).first()
        if reporter and reporter.email: recipients.append(reporter.email)
        if issue.assignee_id:
            assignee = db.query(User).filter(User.id == issue.assignee_id).first()
            if assignee and assignee.email: recipients.append(assignee.email)
            
        notify_issue_update(
            issue_title=issue.title,
            action="Schedule Updated",
            details=f"Schedule was updated by {current_user.username}.",
            recipient_emails=recipients
        )
        
    return issue

class TimeLogUpdate(BaseModel):
    role: str # "reporter" or "assignee"
    hours: float

@router.patch("/{project_id}/issues/{issue_id}/log_time", response_model=IssueSchema)
def log_issue_time(project_id: int, issue_id: int, time_update: TimeLogUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    issue = db.query(Issue).filter(Issue.id == issue_id, Issue.project_id == project_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    if time_update.role == "reporter":
        issue.reporter_logged_hours += time_update.hours
    elif time_update.role == "assignee":
        issue.assignee_logged_hours += time_update.hours
    else:
        raise HTTPException(status_code=400, detail="Role must be reporter or assignee")
        
    db_timelog = TimeLog(
        issue_id=issue_id,
        user_id=current_user.id,
        hours=time_update.hours
    )
    db.add(db_timelog)
    
    db.commit()
    db.refresh(issue)
    return issue

@router.post("/{project_id}/issues/{issue_id}/comments", response_model=CommentSchema)
def create_comment(project_id: int, issue_id: int, comment: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    issue = db.query(Issue).filter(Issue.id == issue_id, Issue.project_id == project_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
        
    db_comment = Comment(
        issue_id=issue_id,
        author_id=current_user.id,
        content=comment.content
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.post("/{project_id}/issues/{issue_id}/attachments", response_model=AttachmentSchema)
def upload_issue_attachment(project_id: int, issue_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Verify issue belongs to project
    issue = db.query(Issue).filter(Issue.id == issue_id, Issue.project_id == project_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    upload_dir = "uploads/attachments"
    os.makedirs(upload_dir, exist_ok=True)
    
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    db_attachment = Attachment(
        issue_id=issue_id,
        filename=file.filename,
        file_path=f"/static/attachments/{unique_filename}",
        uploader_id=current_user.id
    )
    db.add(db_attachment)
    db.commit()
    db.refresh(db_attachment)
    return db_attachment

# --- Boards ---
@router.get("/{project_id}/boards", response_model=List[BoardSchema])
def get_boards(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Board).filter(Board.project_id == project_id).all()

@router.post("/{project_id}/boards", response_model=BoardSchema)
def create_board(project_id: int, board: BoardCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if board.project_id != project_id:
        raise HTTPException(status_code=400, detail="Project ID mismatch")
    db_board = Board(**board.model_dump())
    db.add(db_board)
    db.commit()
    db.refresh(db_board)
    return db_board

# --- Components ---
@router.get("/{project_id}/components", response_model=List[ComponentSchema])
def get_components(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Component).filter(Component.project_id == project_id).all()

@router.post("/{project_id}/components", response_model=ComponentSchema)
def create_component(project_id: int, component: ComponentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if component.project_id != project_id:
        raise HTTPException(status_code=400, detail="Project ID mismatch")
    db_component = Component(**component.model_dump())
    db.add(db_component)
    db.commit()
    db.refresh(db_component)
    return db_component

# --- Versions ---
@router.get("/{project_id}/versions", response_model=List[VersionSchema])
def get_versions(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Version).filter(Version.project_id == project_id).all()

@router.post("/{project_id}/versions", response_model=VersionSchema)
def create_version(project_id: int, version: VersionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if version.project_id != project_id:
        raise HTTPException(status_code=400, detail="Project ID mismatch")
    db_version = Version(**version.model_dump())
    db.add(db_version)
    db.commit()
    db.refresh(db_version)
    return db_version

# --- Wiki Pages ---
@router.get("/{project_id}/wikis", response_model=List[WikiPageSchema])
def get_wikis(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(WikiPage).filter(WikiPage.project_id == project_id).all()

@router.get("/{project_id}/wikis/{wiki_id}", response_model=WikiPageSchema)
def get_wiki(project_id: int, wiki_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    wiki = db.query(WikiPage).filter(WikiPage.id == wiki_id, WikiPage.project_id == project_id).first()
    if not wiki:
        raise HTTPException(status_code=404, detail="Wiki not found")
    return wiki

@router.post("/{project_id}/wikis", response_model=WikiPageSchema)
def create_wiki(project_id: int, wiki: WikiPageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if wiki.project_id != project_id:
        raise HTTPException(status_code=400, detail="Project ID mismatch")
    db_wiki = WikiPage(**wiki.model_dump(), author_id=current_user.id)
    db.add(db_wiki)
    db.commit()
    db.refresh(db_wiki)
    return db_wiki
