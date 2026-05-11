from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class WorkspaceBase(BaseModel):
    name: str
    description: Optional[str] = None

class WorkspaceCreate(WorkspaceBase):
    pass

class Workspace(WorkspaceBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
