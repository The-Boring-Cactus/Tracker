from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(255))
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    time_logs = relationship("TimeLog", back_populates="user")

class Workspace(Base):
    __tablename__ = "workspaces"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    projects = relationship("Project", back_populates="workspace", cascade="all, delete-orphan")

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"))
    name = Column(String(100), index=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    workspace = relationship("Workspace", back_populates="projects")
    issues = relationship("Issue", back_populates="project", cascade="all, delete-orphan")
    boards = relationship("Board", back_populates="project", cascade="all, delete-orphan")
    components = relationship("Component", back_populates="project", cascade="all, delete-orphan")
    versions = relationship("Version", back_populates="project", cascade="all, delete-orphan")
    wikis = relationship("WikiPage", back_populates="project", cascade="all, delete-orphan")

class Component(Base):
    __tablename__ = "components"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String(100))
    description = Column(Text, nullable=True)

    project = relationship("Project", back_populates="components")
    issues = relationship("Issue", back_populates="component")

class Version(Base):
    __tablename__ = "versions"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String(100))
    release_date = Column(DateTime, nullable=True)
    released = Column(Boolean, default=False)

    project = relationship("Project", back_populates="versions")
    issues = relationship("Issue", back_populates="version")

class Board(Base):
    __tablename__ = "boards"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String(100))
    type = Column(String(50)) # scrum, kanban

    project = relationship("Project", back_populates="boards")

class Issue(Base):
    __tablename__ = "issues"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    title = Column(String(200), index=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="New") # New, On Process, Close, Rejected
    category = Column(String(50), default="ISSUE") # TODO, WORK, ISSUE, TASK
    reporter_id = Column(Integer, ForeignKey("users.id"))
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    parent_id = Column(Integer, ForeignKey("issues.id"), nullable=True)
    component_id = Column(Integer, ForeignKey("components.id"), nullable=True)
    version_id = Column(Integer, ForeignKey("versions.id"), nullable=True)
    tags = Column(String(500), nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    estimated_hours = Column(Float, nullable=True)
    reporter_logged_hours = Column(Float, default=0.0)
    assignee_logged_hours = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="issues")
    reporter = relationship("User", foreign_keys=[reporter_id])
    assignee = relationship("User", foreign_keys=[assignee_id])
    parent = relationship("Issue", remote_side=[id], backref="children")
    component = relationship("Component", back_populates="issues")
    version = relationship("Version", back_populates="issues")
    attachments = relationship("Attachment", back_populates="issue", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="issue", cascade="all, delete-orphan")
    time_logs = relationship("TimeLog", back_populates="issue", cascade="all, delete-orphan")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id"))
    author_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    issue = relationship("Issue", back_populates="comments")
    author = relationship("User")

class Attachment(Base):
    __tablename__ = "attachments"
    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id"))
    filename = Column(String(255))
    file_path = Column(String(500))
    uploader_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    issue = relationship("Issue", back_populates="attachments")
    uploader = relationship("User")

class WikiPage(Base):
    __tablename__ = "wiki_pages"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    title = Column(String(200))
    content = Column(Text)
    tags = Column(String(500), nullable=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="wikis")
    author = relationship("User", foreign_keys=[author_id])

class TimeLog(Base):
    __tablename__ = "time_logs"
    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    hours = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    issue = relationship("Issue", back_populates="time_logs")
    user = relationship("User", back_populates="time_logs")
