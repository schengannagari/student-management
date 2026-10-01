from datetime import date

from sqlalchemy import Date, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, SoftDeleteMixin, TimestampMixin
from app.models.enums import Gender, StudentStatus
from app.models.types import str_enum

# Case-insensitive collation lets SQLite serve `LIKE 'abc%'` straight from the index.
# (On PostgreSQL, replace with a citext column or a lower() functional index.)
CI = "NOCASE"


class Student(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "students"
    __table_args__ = (
        # Indexes chosen for the real query patterns (list by class / status / name search).
        Index("ix_students_name", "last_name", "first_name"),
        Index("ix_students_classroom_status", "classroom_id", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    admission_number: Mapped[str] = mapped_column(String(30, collation=CI), unique=True)
    first_name: Mapped[str] = mapped_column(String(80, collation=CI), index=True)
    last_name: Mapped[str] = mapped_column(String(80, collation=CI))
    date_of_birth: Mapped[date] = mapped_column(Date)
    gender: Mapped[Gender] = mapped_column(str_enum(Gender))
    email: Mapped[str | None] = mapped_column(String(254))
    phone: Mapped[str | None] = mapped_column(String(20))
    guardian_name: Mapped[str] = mapped_column(String(120))
    guardian_phone: Mapped[str] = mapped_column(String(20))
    address: Mapped[str | None] = mapped_column(Text)
    status: Mapped[StudentStatus] = mapped_column(str_enum(StudentStatus), default=StudentStatus.ACTIVE)
    classroom_id: Mapped[int | None] = mapped_column(ForeignKey("classrooms.id"), index=True)

    # Optimistic locking: concurrent edits of one row raise instead of silently overwriting.
    version: Mapped[int] = mapped_column(default=1)
    __mapper_args__ = {"version_id_col": version}
