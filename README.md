# Online Attendance Management System

A full-stack attendance platform for teachers, students, and administrators. The project includes secure authentication, class/session management, attendance marking, report generation, and Excel exports.

## Prerequisites

- Python 3.11+ recommended (3.12 is ideal)
- Node.js 18+ and npm 9+
- Git
- PowerShell 5.1+ / Windows Terminal

## Backend setup

From the project root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

If your machine does not expose `python` in PATH, use the project-local interpreter directly:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Environment configuration

The backend reads settings from the file `backend/.env`. A template is provided at `backend/.env.example`.

```powershell
Copy-Item .env.example .env
```

Example values:

```env
APP_ENV=development
APP_NAME="Online Attendance Management System"
SECRET_KEY=change-this-in-production-to-a-very-secure-random-secret-key
ALGORITHM=HS256
DATABASE_URL=sqlite:///./attendance.db
DEFAULT_ATTENDANCE_THRESHOLD=75.0
ALLOW_HALF_DAY=true
HALF_DAY_WEIGHT=0.5
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### Initialize the database

```powershell
cd backend
.\.venv\Scripts\python.exe -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### Run backend locally

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API docs are available at: http://localhost:8000/docs

## Frontend setup

From the project root:

```powershell
cd frontend
npm install
```

Create a local frontend environment file if needed:

```powershell
Copy-Item ..\.env.example .env
```

Example:

```env
VITE_API_URL=http://localhost:8000
```

### Run frontend locally

```powershell
cd frontend
npm run dev -- --host 0.0.0.0 --port 5173
```

Open: http://localhost:5173

### Build for production

```powershell
cd frontend
npm run build
```

## Test commands

Run focused checks first:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests/test_calculations.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_attendance.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_excel_export.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_auth.py -q
.\.venv\Scripts\python.exe -m pytest tests/test_permissions.py -q
```

Run the full backend suite:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q
```

## Demo / seed data

The backend includes a seeding utility for demonstration accounts and records. To initialize sample data:

```powershell
cd backend
.\.venv\Scripts\python.exe -c "from app.seed import seed_demo_data; seed_demo_data()"
```

If a seeder is not available in your branch, create the required teacher/student records through the application or the database shell before testing the teacher and student workflows.

## Deployment notes

- Use PostgreSQL for production by setting `DATABASE_URL` to a PostgreSQL connection string.
- Keep `SECRET_KEY` in a secure environment variable or secret manager.
- Restrict CORS origins to your production frontend origin.
- Run the backend behind a reverse proxy with HTTPS in production.

## Troubleshooting

### Python is not recognized

Use the project virtual environment directly:

```powershell
cd backend
.\.venv\Scripts\python.exe --version
```

### Frontend dependencies fail to install

Delete the lockfile and reinstall only if the package registry is healthy:

```powershell
cd frontend
Remove-Item -Recurse -Force node_modules, package-lock.json -ErrorAction SilentlyContinue
npm install
```

### Backend DB issues

Rebuild the SQLite database if needed:

```powershell
cd backend
Remove-Item attendance.db -ErrorAction SilentlyContinue
.\.venv\Scripts\python.exe -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### CORS problems

Ensure `CORS_ORIGINS` or `APP_ENV` values match the frontend URL and port.

---

This project preserves the teacher attendance workflow, student attendance privacy, and official attendance calculation logic while keeping personal tracker data separate from institutional records.
