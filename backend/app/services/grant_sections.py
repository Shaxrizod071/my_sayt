"""Har bir talaba uchun 11 ta grant bo'limini (Section) avtomatik yaratish."""

from sqlalchemy.orm import Session

from .. import models
from ..grant_criteria import GRANT_CRITERIA


def ensure_grant_sections_for_student(db: Session, student_id: int) -> int:
    """
    grant_criterion_id 1..11 bo'yicha yo'q bo'limlarni yaratadi.
    Qaytaradi: yangi qo'shilgan sectionlar soni.
    """
    rows = (
        db.query(models.Section.grant_criterion_id)
        .filter(models.Section.student_id == student_id)
        .all()
    )
    existing = {r[0] for r in rows if r[0] is not None}
    added = 0
    for c in GRANT_CRITERIA:
        cid = c["id"]
        if cid in existing:
            continue
        db.add(
            models.Section(
                student_id=student_id,
                name=c["name"],
                grant_criterion_id=cid,
                image_url=None,
            )
        )
        added += 1
    if added:
        db.commit()
    return added


def bootstrap_grant_sections_all_students() -> None:
    """Barcha mavjud talabalar uchun 11 ta bo'limni to'ldiradi (startup / migratsiya)."""
    from ..database import SessionLocal

    db = SessionLocal()
    try:
        for st in db.query(models.Student).all():
            ensure_grant_sections_for_student(db, st.id)
    finally:
        db.close()
