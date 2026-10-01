from datetime import UTC, datetime

from sqlalchemy import ColumnElement, func, or_, select
from sqlalchemy.orm import InstrumentedAttribute

from app.models.enums import StudentStatus
from app.models.student import Student
from app.repositories.base import BaseRepository


def _prefix(column: InstrumentedAttribute[str], q: str) -> ColumnElement[bool]:
    """Index-friendly, injection-safe `column LIKE 'q%'` (wildcards in q are escaped)."""
    escaped = q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return column.like(f"{escaped}%", escape="\\")


class StudentRepository(BaseRepository[Student]):
    model = Student

    def get_active(self, id_: int) -> Student | None:
        stmt = select(Student).where(Student.id == id_, Student.deleted_at.is_(None))
        return self.db.scalars(stmt).first()

    def get_by_admission_number(self, number: str) -> Student | None:
        return self.db.scalars(select(Student).where(Student.admission_number == number)).first()

    def search(
        self,
        *,
        q: str | None,
        classroom_id: int | None,
        status: StudentStatus | None,
        offset: int,
        limit: int,
    ) -> tuple[list[Student], int]:
        conditions: list[ColumnElement[bool]] = [Student.deleted_at.is_(None)]
        if q:
            # Prefix search can use indexes; for "contains" search add SQLite FTS5 later.
            conditions.append(
                or_(
                    _prefix(Student.admission_number, q),
                    _prefix(Student.first_name, q),
                    _prefix(Student.last_name, q),
                )
            )
        if classroom_id is not None:
            conditions.append(Student.classroom_id == classroom_id)
        if status is not None:
            conditions.append(Student.status == status)

        total = self.db.scalar(select(func.count(Student.id)).where(*conditions)) or 0
        items = self.db.scalars(
            select(Student).where(*conditions).order_by(Student.id).offset(offset).limit(limit)
        ).all()
        return list(items), total

    def soft_delete(self, student: Student) -> None:
        student.deleted_at = datetime.now(UTC)
        student.status = StudentStatus.INACTIVE
