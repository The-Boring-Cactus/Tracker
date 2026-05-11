import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy_utils import database_exists, create_database

CONFIG_FILE = "config.json"
Base = declarative_base()

def get_db_url():
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
        db_type = config.get("db_type")
        user = config.get("user")
        password = config.get("password")
        host = config.get("host")
        port = config.get("port")
        db_name = config.get("db_name")

        # Basic DB URL mappings
        if db_type == "postgresql":
            return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}"
        elif db_type == "mysql":
            return f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"
        elif db_type == "mssql":
            # Using pyodbc and the standard SQL Server driver for Linux/Windows
            return f"mssql+pyodbc://{user}:{password}@{host}:{port}/{db_name}?driver=ODBC+Driver+17+for+SQL+Server"
        return f"sqlite:///./sql_app.db" # Default fallback for local testing

def init_engine():
    db_url = get_db_url()
    if not db_url:
        return None, None
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal

engine, SessionLocal = init_engine()

def get_db():
    if not SessionLocal:
        raise Exception("Database not configured. Please run setup.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def reinit_db():
    global engine, SessionLocal
    engine, SessionLocal = init_engine()
    if engine:
        # Create the database if it doesn't exist (MySQL, Postgres, MS-SQL)
        if not database_exists(engine.url):
            create_database(engine.url)
        # Create all tables
        Base.metadata.create_all(bind=engine)
