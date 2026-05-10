import os
import json

CONFIG_FILE = "config.json"

def init_from_env():
    if os.path.exists(CONFIG_FILE):
        return

    db_type = os.getenv("DB_TYPE")
    if not db_type:
        return  # Do not auto-init if DB_TYPE is not provided

    config_data = {
        "db_type": db_type,
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", 5432)),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", ""),
        "db_name": os.getenv("DB_NAME", "tracker"),
        "smtp_host": os.getenv("SMTP_HOST", ""),
        "smtp_port": int(os.getenv("SMTP_PORT", 587)),
        "smtp_user": os.getenv("SMTP_USER", ""),
        "smtp_password": os.getenv("SMTP_PASSWORD", ""),
        "smtp_tls": os.getenv("SMTP_TLS", "true").lower() == "true"
    }

    # Write config file
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f)
    print("Created config.json from environment variables.")

    try:
        from database import reinit_db, SessionLocal, engine
        reinit_db()
        if not engine:
            print("Failed to initialize engine")
            return
            
        # Create admin user if details are provided
        admin_user = os.getenv("ADMIN_USERNAME")
        if admin_user:
            from models import User
            from routers.setup import get_password_hash
            db = SessionLocal()
            existing_admin = db.query(User).filter(User.username == admin_user).first()
            if not existing_admin:
                admin = User(
                    username=admin_user,
                    email=os.getenv("ADMIN_EMAIL", ""),
                    hashed_password=get_password_hash(os.getenv("ADMIN_PASSWORD", "admin")),
                    is_admin=True
                )
                db.add(admin)
                db.commit()
                print(f"Created admin user: {admin_user}")
            db.close()
    except Exception as e:
        print(f"Error during environment initialization: {e}")
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)

if __name__ == "__main__":
    init_from_env()
