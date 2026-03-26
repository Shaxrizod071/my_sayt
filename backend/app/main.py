from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.database import engine, ensure_schema
from app import models
from app.routers import students, admin
from app.services.grant_sections import bootstrap_grant_sections_all_students
models.Base.metadata.create_all(bind=engine)
ensure_schema()
bootstrap_grant_sections_all_students()

app = FastAPI(title="Student Backend")

# Serve simple frontend (HTML/JS) from /frontend
_STATIC_DIR = Path(__file__).resolve().parent / "static"
if _STATIC_DIR.exists():
    app.mount("/frontend", StaticFiles(directory=str(_STATIC_DIR), html=True), name="frontend")

app.include_router(students.router)
app.include_router(admin.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the student backend API"}
