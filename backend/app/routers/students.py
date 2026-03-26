from pathlib import Path
import hashlib
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import case
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services import evidence as evidence_service
from ..services import gpa as gpa_service, grants as grants_service
from ..services.grant_sections import ensure_grant_sections_for_student

router = APIRouter(prefix="/students", tags=["students"])

_STATIC_ROOT = Path(__file__).resolve().parent.parent / "static"
_SECTION_UPLOAD_DIR = _STATIC_ROOT / "uploads" / "sections"
_EVENT_UPLOAD_DIR = _STATIC_ROOT / "uploads" / "events"


async def _read_upload_limited(upload: UploadFile, max_bytes: int) -> bytes:
    data = await upload.read()
    if len(data) > max_bytes:
        mb = len(data) / (1024 * 1024)
        raise HTTPException(
            status_code=400,
            detail=f"Rasm hajmi 3.5 MB dan oshmasligi kerak (yuklangan: {mb:.2f} MB).",
        )
    return data


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


@router.post("/", response_model=schemas.Student)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    if db.query(models.Student).filter(models.Student.login == student.login).first():
        raise HTTPException(status_code=400, detail="Login already exists")
    if db.query(models.Student).filter(models.Student.email == student.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    db_student = models.Student(
        first_name=student.first_name,
        last_name=student.last_name,
        email=student.email,
        login=student.login,
        password_hash=hash_password(student.password),
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)

    for grade in student.grades:
        db_grade = models.Grade(
            student_id=db_student.id,
            course=grade.course,
            score=grade.score_100,
        )
        db.add(db_grade)
    if student.grades:
        gpa = gpa_service.calculate_gpa([g.score_100 for g in student.grades])
        db_student.gpa = gpa
        db_student.grant_status = grants_service.determine_grant_status(gpa)

    db.commit()
    db.refresh(db_student)

    ensure_grant_sections_for_student(db, db_student.id)

    return db_student


@router.post("/login")
def login(credentials: schemas.Login, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.login == credentials.login).first()
    if not student or student.password_hash != hash_password(credentials.password):
        raise HTTPException(status_code=401, detail="Invalid HEMIS login or password")
    ensure_grant_sections_for_student(db, student.id)
    return {
        "message": "HEMIS login successful",
        "student_id": student.id,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "email": student.email,
    }


@router.get("/", response_model=list[schemas.Student])
def list_students(db: Session = Depends(get_db)):
    return db.query(models.Student).all()


@router.get("/grant-criteria", response_model=list[schemas.GrantCriterionMeta])
def list_grant_criteria():
    """Grant jadvalidagi 11 ta mezon (nom va maks. ball)."""
    from ..grant_criteria import GRANT_CRITERIA

    return [schemas.GrantCriterionMeta(**c) for c in GRANT_CRITERIA]


@router.post("/{student_id}/sections", response_model=schemas.Section)
async def add_section(
    student_id: int,
    name: str = Form(..., description="Section nomi (matn)"),
    image: UploadFile | None = File(None, description="Ixtiyoriy rasm fayli"),
    db: Session = Depends(get_db),
):
    """`multipart/form-data`: `name` (string) va ixtiyoriy `image` (fayl)."""
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    image_url = None
    if image and image.filename:
        data = await _read_upload_limited(image, evidence_service.MAX_IMAGE_BYTES)
        if not data:
            raise HTTPException(status_code=400, detail="Bo'sh rasm fayli yuklandi.")
        _SECTION_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        suffix = Path(image.filename).suffix or ".bin"
        safe_name = f"{uuid.uuid4().hex}{suffix}"
        dest = _SECTION_UPLOAD_DIR / safe_name
        dest.write_bytes(data)
        image_url = f"/frontend/uploads/sections/{safe_name}"

    section_db = models.Section(
        student_id=student_id,
        name=name,
        image_url=image_url,
        grant_criterion_id=None,
    )
    db.add(section_db)
    db.commit()
    db.refresh(section_db)
    return section_db


def _normalize_image_url(url: str | None) -> str | None:
    if url is None:
        return None
    s = url.strip()
    return s if s else None


@router.post("/sections/{section_id}/events", response_model=schemas.Event)
def add_event(section_id: int, event: schemas.EventCreate, db: Session = Depends(get_db)):
    section = db.query(models.Section).filter(models.Section.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    image_url = _normalize_image_url(event.image_url)
    if image_url and not evidence_service.can_add_image_to_section(db, section_id):
        raise HTTPException(
            status_code=400,
            detail=f"Bu bo'limda maksimal {evidence_service.MAX_IMAGES_PER_SECTION} ta rasm mumkin (section muqova + tadbir rasmlari).",
        )
    event_db = models.Event(
        section_id=section_id,
        name=event.name,
        score=event.score_100,
        image_url=image_url,
    )
    db.add(event_db)
    db.commit()
    db.refresh(event_db)
    return event_db


@router.post("/sections/{section_id}/events/upload", response_model=schemas.Event)
async def add_event_with_file(
    section_id: int,
    name: str = Form(...),
    score_100: float = Form(...),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    """Tadbir yaratish + rasm fayl (3.5 MB gacha, bo'limda jami 4 tadan oshmasin)."""
    section = db.query(models.Section).filter(models.Section.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    image_url = None
    if image and image.filename:
        if not evidence_service.can_add_image_to_section(db, section_id):
            raise HTTPException(
                status_code=400,
                detail=f"Bu bo'limda maksimal {evidence_service.MAX_IMAGES_PER_SECTION} ta rasm mumkin.",
            )
        data = await _read_upload_limited(image, evidence_service.MAX_IMAGE_BYTES)
        if not data:
            raise HTTPException(status_code=400, detail="Bo'sh rasm fayli.")
        _EVENT_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        suffix = Path(image.filename).suffix or ".bin"
        safe_name = f"{uuid.uuid4().hex}{suffix}"
        dest = _EVENT_UPLOAD_DIR / safe_name
        dest.write_bytes(data)
        image_url = f"/frontend/uploads/events/{safe_name}"

    event_db = models.Event(
        section_id=section_id,
        name=name,
        score=score_100,
        image_url=image_url,
    )
    db.add(event_db)
    db.commit()
    db.refresh(event_db)
    return event_db


@router.get("/{student_id}/evidence-summary", response_model=schemas.EvidenceSummary)
def get_evidence_summary(student_id: int, db: Session = Depends(get_db)):
    """Barcha bo'limlar bo'yicha rasm soni (section + tadbirlar), umumiy jami."""
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    sections_sorted = sorted(
        student.sections,
        key=lambda s: (
            s.grant_criterion_id is None,
            s.grant_criterion_id or 0,
            s.id,
        ),
    )
    sections_info: list[schemas.SectionEvidenceInfo] = []
    total = 0
    for sec in sections_sorted:
        c = evidence_service.section_image_count(db, sec.id)
        total += c
        sections_info.append(
            schemas.SectionEvidenceInfo(
                section_id=sec.id,
                name=sec.name,
                image_count=c,
                max_images=evidence_service.MAX_IMAGES_PER_SECTION,
                remaining_slots=max(0, evidence_service.MAX_IMAGES_PER_SECTION - c),
                grant_criterion_id=sec.grant_criterion_id,
            )
        )

    return schemas.EvidenceSummary(
        max_images_per_section=evidence_service.MAX_IMAGES_PER_SECTION,
        max_image_size_mb=3.5,
        total_images=total,
        sections=sections_info,
    )


@router.get("/{student_id}/sections", response_model=list[schemas.Section])
def get_student_sections(student_id: int, db: Session = Depends(get_db)):
    """Faqat shu talabaga tegishli bo'limlar (dashboard ro'yxati uchun)."""
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return (
        db.query(models.Section)
        .filter(models.Section.student_id == student_id)
        .order_by(
            case((models.Section.grant_criterion_id.is_(None), 1), else_=0),
            models.Section.grant_criterion_id,
            models.Section.id,
        )
        .all()
    )


@router.get("/sections", response_model=list[schemas.Section])
def get_sections(db: Session = Depends(get_db)):
    return db.query(models.Section).all()


@router.get("/sections/{section_id}/events", response_model=list[schemas.Event])
def get_section_events(section_id: int, db: Session = Depends(get_db)):
    section = db.query(models.Section).filter(models.Section.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    return section.events


@router.get("/sections/{section_id}/stats")
def section_stats(section_id: int, db: Session = Depends(get_db)):
    section = db.query(models.Section).filter(models.Section.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    total_events = len(section.events)
    image_count = evidence_service.section_image_count(db, section_id)
    students = db.query(models.Student).all()
    participation = []
    for s in students:
        for sec in s.sections:
            if sec.id == section_id:
                participation.append({
                    "student_id": s.id,
                    "student_name": f"{s.first_name} {s.last_name}",
                    "events": len(sec.events),
                    "images": evidence_service.section_image_count(db, section_id),
                })
    return {
        "section_id": section_id,
        "section_name": section.name,
        "total_events": total_events,
        "total_images": image_count,
        "max_images_per_section": evidence_service.MAX_IMAGES_PER_SECTION,
        "remaining_image_slots": max(0, evidence_service.MAX_IMAGES_PER_SECTION - image_count),
        "max_image_size_mb": 3.5,
        "participation": participation,
    }
