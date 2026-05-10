from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Component Schemas
class ComponentBase(BaseModel):
    name: str
    description: Optional[str] = None
    project_id: int

class ComponentCreate(ComponentBase):
    pass

class Component(ComponentBase):
    id: int

    class Config:
        from_attributes = True

# Version Schemas
class VersionBase(BaseModel):
    name: str
    release_date: Optional[datetime] = None
    released: bool = False
    project_id: int

class VersionCreate(VersionBase):
    pass

class Version(VersionBase):
    id: int

    class Config:
        from_attributes = True

# Attachment Schemas
class AttachmentSchema(BaseModel):
    id: int
    filename: str
    file_path: str
    uploader_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Comment Schemas
class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class CommentSchema(CommentBase):
    id: int
    issue_id: int
    author_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Issue Schemas
class IssueBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "New"
    category: str = "ISSUE"
    project_id: int
    assignee_id: Optional[int] = None
    parent_id: Optional[int] = None
    component_id: Optional[int] = None
    version_id: Optional[int] = None
    tags: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None

class IssueCreate(IssueBase):
    send_email: Optional[bool] = False
    pass

class Issue(IssueBase):
    id: int
    reporter_id: int
    reporter_logged_hours: float
    assignee_logged_hours: float
    created_at: datetime
    updated_at: datetime
    attachments: List[AttachmentSchema] = []
    comments: List[CommentSchema] = []

    class Config:
        from_attributes = True

class ScheduleUpdate(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    send_email: Optional[bool] = False

# Board Schemas
class BoardBase(BaseModel):
    name: str
    type: str # 'scrum' or 'kanban'
    project_id: int

class BoardCreate(BoardBase):
    pass

class Board(BoardBase):
    id: int

    class Config:
        from_attributes = True

# Wiki Schemas
class WikiPageBase(BaseModel):
    title: str
    content: str
    project_id: int
    tags: Optional[str] = None

class WikiPageCreate(WikiPageBase):
    pass

class WikiPage(WikiPageBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
