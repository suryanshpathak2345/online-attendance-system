from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import engine, Base
import app.models  # ensure all models are registered

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Production-grade Online Attendance Management System API with Teacher, Student, and Personal Tracker modules."
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
from app.routers import auth, classes, subjects, students, sessions, attendance, reports, holidays, personal

app.include_router(auth.router)
app.include_router(classes.router)
app.include_router(subjects.router)
app.include_router(students.router)
app.include_router(sessions.router)
app.include_router(attendance.router)
app.include_router(reports.router)
app.include_router(holidays.router)
app.include_router(personal.router)


@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "environment": settings.app_env,
        "database": "connected"
    }


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to Online Attendance Management System API",
        "docs_url": "/docs",
        "health_url": "/api/health"
    }
