import sys
import os
from pathlib import Path

# Loyiha ildiz papkasini Python qidiruv yo'lagiga qo'shish
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, ensure_schema
from app import models
from app.routers import students, admin
from app.services.grant_sections import bootstrap_grant_sections_all_students

# Ma'lumotlar bazasini sozlash
models.Base.metadata.create_all(bind=engine)
ensure_schema()
bootstrap_grant_sections_all_students()

app = FastAPI(title="Student Backend")

# --- 1. CORS SOZLAMALARI ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. ROUTERLARNI RO'YXATDAN O'TKAZISH ---
app.include_router(students.router)
app.include_router(admin.router)

# --- 3. STATIK FAYLLAR (FRONTEND) UCHUN SOZLAMA ---
# 'static' papkasi yo'lini aniqlaymiz (main.py joylashgan papka ichidagi 'static')
_STATIC_DIR = Path(__file__).resolve().parent / "static"

if _STATIC_DIR.exists():
    # 'html=True' bo'lsa, '/' manzili avtomat index.html ni ochadi
    app.mount("/", StaticFiles(directory=str(_STATIC_DIR), html=True), name="static")
else:
    # Agar papka topilmasa, terminalda xato chiqadi
    print(f"DIQQAT: {_STATIC_DIR} papkasi topilmadi!")

# MUHIM: @app.get("/") funksiyasini olib tashladik! 
# Chunki u bo'lsa, statik index.html faylingiz ochilmay qoladi.

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)