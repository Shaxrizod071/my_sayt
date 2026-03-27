import sys
import os
from pathlib import Path

# Loyiha ildiz papkasini Python qidiruv yo'lagiga qo'shish
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware  # <-- 1. CORS import qilindi

from app.database import engine, ensure_schema
from app import models
from app.routers import students, admin
from app.services.grant_sections import bootstrap_grant_sections_all_students

models.Base.metadata.create_all(bind=engine)
ensure_schema()
bootstrap_grant_sections_all_students()

app = FastAPI(title="Student Backend")

# --- 2. CORS SOZLAMALARI SHU YERDA (Frontend ishlashi uchun shart!) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Hamma joydan so'rov qabul qilish
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE hammasiga ruxsat
    allow_headers=["*"],
)
# -----------------------------------------------------------------------

# Serve simple frontend (HTML/JS) from /frontend
_STATIC_DIR = Path(__file__).resolve().parent / "static"
if _STATIC_DIR.exists():
    app.mount("/frontend", StaticFiles(directory=str(_STATIC_DIR), html=True), name="frontend")

app.include_router(students.router)
app.include_router(admin.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the student backend API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)