from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.services import ratings

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/rankings")
def get_rankings(db: Session = Depends(get_db)):
    students = db.query(models.Student).all()
    list_in = [{"id": s.id, "gpa": s.gpa} for s in students]
    return ratings.calculate_rankings(list_in)
 