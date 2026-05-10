from pydantic import BaseModel, EmailStr
from typing import Optional

class SetupRequest(BaseModel):
    db_type: str
    host: str
    port: int
    user: str
    password: str
    db_name: str
    
    # Admin details
    admin_username: str
    admin_email: EmailStr
    admin_password: str

    # SMTP configuration
    smtp_host: Optional[str] = ""
    smtp_port: Optional[int] = 587
    smtp_user: Optional[str] = ""
    smtp_password: Optional[str] = ""
    smtp_tls: bool = True
