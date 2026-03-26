from pydantic import BaseModel, computed_field
from typing import List, Optional

# 1. Baho uchun asosiy model
class GradeBase(BaseModel):
    course: str
    score_100: float  # Universitetdagi 100 ballik tizim (masalan: 95)
    credit: int       # Fanning krediti (masalan: 6)

    @computed_field
    @property
    def score_5(self) -> int:
        """100 ballikni 5 ballik tizimga o'tkazish mantiqi"""
        if self.score_100 >= 90: return 5
        elif self.score_100 >= 80: return 4
        elif self.score_100 >= 70: return 3
        elif self.score_100 >= 60: return 2
        else: return 0

# 2. Baho yaratish va bazadan olish modellari
class GradeCreate(GradeBase):
    pass

class Grade(GradeBase):
    id: int
    class Config:
        from_attributes = True # Pydantic v2 uchun (eski orm_mode)

# 3. Talaba uchun asosiy model
class StudentBase(BaseModel):
    first_name: str
    last_name: str
    email: str

class StudentCreate(StudentBase):
    login: str
    password: str
    grades: Optional[List[GradeCreate]] = []
class Login(BaseModel):
    login: str
    password: str


# Section (create + response) uchun schema
class SectionCreate(BaseModel):
    name: str

# 5. Bo'lim (Section) schema'lari
class Section(BaseModel):
    id: int
    student_id: int
    name: str
    image_url: Optional[str] = None
    grant_criterion_id: Optional[int] = None  # 1..11 grant mezoni; None — qo'lda yaratilgan

    class Config:
        from_attributes = True


# 6. Event schema'lari
class EventCreate(BaseModel):
    name: str
    score_100: float
    image_url: Optional[str] = None


class Event(BaseModel):
    id: int
    section_id: int
    name: str
    score: float
    image_url: Optional[str] = None

    # Backend ORM'da `score` saqlanadi, lekin frontend/endpointlarda `score_100` kutilishi mumkin.
    @computed_field
    @property
    def score_100(self) -> float:
        return self.score

    class Config:
        from_attributes = True


class GrantCriterionMeta(BaseModel):
    id: int
    name: str
    max_points: int


class SectionEvidenceInfo(BaseModel):
    section_id: int
    name: str
    image_count: int
    max_images: int
    remaining_slots: int
    grant_criterion_id: Optional[int] = None


class EvidenceSummary(BaseModel):
    max_images_per_section: int
    max_image_size_mb: float
    total_images: int
    sections: List[SectionEvidenceInfo]

# 4. Yakuniy Talaba modeli (GPA hisoblash bilan)
class Student(StudentBase):
    id: int
    login: str
    grades: List[Grade] = []

    @computed_field
    @property
    def gpa(self) -> float:
        """GPA = sum(baho_5 * kredit) / sum(kreditlar)"""
        if not self.grades:
            return 0.0
        
        total_points = sum(g.score_5 * g.credit for g in self.grades)
        total_credits = sum(g.credit for g in self.grades)
        
        return round(total_points / total_credits, 2) if total_credits > 0 else 0.0

    @property
    def grant_status(self) -> str:
        return "Grant" if self.gpa >= 4.5 else "To'lov-kontrakt"

    class Config:
        from_attributes = True