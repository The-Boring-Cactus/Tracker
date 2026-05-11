# Tracker Project

Tracker Project is a professional project management application featuring dynamic workspaces, integrated task tracking, interactive Gantt charts, issue tracking with categories and workflows, and integrated wikis with rich-text syntax highlighting. It allows teams to track and schedule work effectively while storing data persistently in a PostgreSQL backend.

## Project Structure
- **Frontend**: A Vue.js 3 application built with Vite, TailwindCSS, and Pinia.
- **Backend**: A robust FastAPI python backend that connects to a PostgreSQL (or MySQL) database via SQLAlchemy.

## Dev Environment Execution

To run the application locally for development:

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt

# Start the development server
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
*Note: Make sure you have a local PostgreSQL instance running or navigate to `http://127.0.0.1:8000/setup` to configure the application's config.json for the first time.*

### 2. Frontend Setup
```bash
cd frontend
npm install

# Start the Vite development server
npm run dev
```
The frontend will typically run at `http://localhost:5173`. 

---

## Prod Environment Execution (Docker)

The project includes Dockerfiles for containerized execution. Two Docker Compose setups are provided based on your PostgreSQL database preference.

### Option A: Complete Environment (Database Included)
Use this option to spin up a fully isolated environment including an embedded PostgreSQL database.

```bash
# Set your preferred environment variables before running, or configure them in a .env file.
export ADMIN_USERNAME="admin"
export ADMIN_PASSWORD="your_secure_password"
export ADMIN_EMAIL="admin@yourdomain.com"
export SMTP_HOST="smtp.example.com"
export SMTP_PORT="587"
export SMTP_USER="mailer"
export SMTP_PASSWORD="smtp_password"

# Launch the environment
docker-compose -f docker-compose-with-db.yml up -d
```

### Option B: Standalone Environment (Existing Database Server)
Use this option if you already have a dedicated database server and only wish to containerize the frontend and backend.

```bash
export DB_HOST="your.db.server.com"
export DB_PORT="5432"
export DB_USER="postgres_user"
export DB_PASSWORD="postgres_password"
export DB_NAME="tracker"

export ADMIN_USERNAME="admin"
export ADMIN_PASSWORD="your_secure_password"

# Launch the application
docker-compose -f docker-compose-standalone.yml up -d
```

### Note on Configuration and Persistence
- **Persistent DB Settings**: In both scenarios, the `backend/config.json` is persistently mapped to an internal Docker volume (`backend_config`). If `config.json` doesn't exist on the first run, the docker container uses your ENV variables to automatically initialize the PostgreSQL database connection and securely provision the initial `ADMIN` user.
- **Accessing the App**: After launching docker-compose, access the frontend at `http://localhost:8080`. The backend API will be available at `http://localhost:8000`.
