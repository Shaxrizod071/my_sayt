from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from .database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    login = Column(String, unique=True, index=True)
    password_hash = Column(String)
    gpa = Column(Float, default=0.0)
    grant_status = Column(String, default="contract")  # or "grant"

    grades = relationship("Grade", back_populates="student", cascade="all, delete")
    sections = relationship("Section", back_populates="student", cascade="all, delete")


class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    course = Column(String)
    score = Column(Float)

    student = relationship("Student", back_populates="grades")


class Section(Base):
    __tablename__ = "sections"
    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "grant_criterion_id",
            name="uq_section_student_grant_criterion",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    name = Column(String, index=True)
    image_url = Column(String, nullable=True)
    # 1..11: grant jadvalidagi mezon; NULL — eski/qo'lda yaratilgan bo'limlar
    grant_criterion_id = Column(Integer, nullable=True, index=True)

    student = relationship("Student", back_populates="sections")
    events = relationship("Event", back_populates="section", cascade="all, delete")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("sections.id"))
    name = Column(String)
    score = Column(Float)
    image_url = Column(String, nullable=True)
    section = relationship("Section", back_populates="events")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    message = Column(String)
    sent = Column(Integer, default=0)  # 0 = not sent, 1 = sent

    student = relationship("Student")
