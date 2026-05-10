from fastapi import APIRouter, HTTPException
import json
import os
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from ..schemas.setup import SetupRequest
from ..database import CONFIG_FILE, reinit_db, SessionLocal
from ..models import User, Base

router = APIRouter(prefix="/setup", tags=["Setup"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

@router.get("/status")
def check_setup_status():
    if os.path.exists(CONFIG_FILE):
        return {"setup_required": False}
    return {"setup_required": True}

@router.post("/")
def perform_setup(request: SetupRequest):
    if os.path.exists(CONFIG_FILE):
        raise HTTPException(status_code=400, detail="Setup already completed")

    # Save to config file
    config_data = {
        "db_type": request.db_type,
        "host": request.host,
        "port": request.port,
        "user": request.user,
        "password": request.password,
        "db_name": request.db_name,
        "smtp_host": request.smtp_host,
        "smtp_port": request.smtp_port,
        "smtp_user": request.smtp_user,
        "smtp_password": request.smtp_password,
        "smtp_tls": request.smtp_tls
    }
    
    # In a real scenario we'd test the connection before saving
    # Here we save, reinit DB, and if it fails, we remove the config
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f)
        
    try:
        reinit_db()
        from ..database import SessionLocal, engine
        if not engine:
            raise Exception("Failed to initialize engine")
            
        db: Session = SessionLocal()
        # Create admin user
        admin = User(
            username=request.admin_username,
            email=request.admin_email,
            hashed_password=get_password_hash(request.admin_password),
            is_admin=True
        )
        db.add(admin)
        db.commit()
        db.close()
        return {"message": "Setup completed successfully"}
    except Exception as e:
        # Revert on failure
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)
        raise HTTPException(status_code=500, detail=f"Database setup failed: {str(e)}")
