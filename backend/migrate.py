from database import engine
from sqlalchemy import text

def run_migration():
    # Try to add parent_id
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE issues ADD COLUMN parent_id INTEGER NULL;"))
            conn.execute(text("ALTER TABLE issues ADD CONSTRAINT fk_issue_parent FOREIGN KEY (parent_id) REFERENCES issues(id);"))
        print("Added parent_id column.")
    except Exception as e:
        print(f"parent_id probably exists: {e}")
        
    # Try to add tags
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE issues ADD COLUMN tags VARCHAR(500) NULL;"))
        print("Added tags column.")
    except Exception as e:
        print(f"tags probably exists: {e}")

    # Try to add full_name
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN full_name VARCHAR(100) NULL;"))
        print("Added full_name column to users.")
    except Exception as e:
        print(f"full_name probably exists: {e}")

    print("Migration completed.")

if __name__ == "__main__":
    run_migration()
