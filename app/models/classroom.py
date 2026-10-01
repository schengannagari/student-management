from sqlalchemy import SmallInteger, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Classroom(TimestampMixin, Base):
    __tablename__ = "classrooms"
    __table_args__ = (UniqueConstraint("grade", "section", "academic_year"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    grade: Mapped[int] = mapped_column(SmallInteger)
    section: Mapped[str] = mapped_column(String(5))
    academic_year: Mapped[str] = mapped_column(String(9))  # e.g. "2025-2026"
