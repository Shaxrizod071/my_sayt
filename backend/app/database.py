from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # replace with your postgres/mysql URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_schema():
    """Mavjud SQLite jadvaliga yangi ustunlar qo'shish (create_all faqat yangi jadvallar uchun)."""
    if not inspect(engine).has_table("sections"):
        return

    def section_cols():
        return {c["name"] for c in inspect(engine).get_columns("sections")}

    cols = section_cols()
    if "image_url" not in cols:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE sections ADD COLUMN image_url VARCHAR"))
        cols = section_cols()
    if "grant_criterion_id" not in cols:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE sections ADD COLUMN grant_criterion_id INTEGER"))

    # Mavjud SQLite uchun: bir talaba + bir mezon takrorlanmasin
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    "CREATE UNIQUE INDEX IF NOT EXISTS uq_section_student_grant_criterion "
                    "ON sections (student_id, grant_criterion_id) "
                    "WHERE grant_criterion_id IS NOT NULL"
                )
            )
    except Exception:
        pass
