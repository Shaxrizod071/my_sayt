"""Grant ijtimoiy faollik: bo‘lim bo‘yicha rasm cheklovlari."""

from typing import Optional

from sqlalchemy.orm import Session

from .. import models

# Har bir bo‘limda (section + uning tadbirlari) jami rasm soni
MAX_IMAGES_PER_SECTION = 4
# Bitta rasm fayli uchun maksimal hajm (bayt)
MAX_IMAGE_BYTES = int(3.5 * 1024 * 1024)


def section_image_count(db: Session, section_id: int) -> int:
    """Section muqova rasmi + tadbirlarda `image_url` bo‘lgan yozuvlar."""
    sec = db.query(models.Section).filter(models.Section.id == section_id).first()
    if not sec:
        return 0
    n = 1 if _has_url(sec.image_url) else 0
    ev_q = (
        db.query(models.Event)
        .filter(models.Event.section_id == section_id)
        .all()
    )
    n += sum(1 for e in ev_q if _has_url(e.image_url))
    return n


def _has_url(url: Optional[str]) -> bool:
    return bool(url and str(url).strip())


def can_add_image_to_section(db: Session, section_id: int) -> bool:
    return section_image_count(db, section_id) < MAX_IMAGES_PER_SECTION
