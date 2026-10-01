import logging

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.student import Student
from app.repositories.classroom import ClassroomRepository
from app.repositories.student import StudentRepository
from app.schemas.common import Page
from app.schemas.student import StudentCreate, StudentFilters, StudentRead, StudentUpdate
from app.services._tx import transaction

log = logging.getLogger(__name__)


class StudentService:
    """Business rules + transaction boundaries. Add new student features here."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.students = StudentRepository(db)
        self.classrooms = ClassroomRepository(db)

    def _ensure_classroom(self, classroom_id: int | None) -> None:
        if classroom_id is not None and self.classrooms.get(classroom_id) is None:
            raise NotFoundError(f"Classroom {classroom_id} does not exist")

    def create(self, data: StudentCreate) -> Student:
        if self.students.get_by_admission_number(data.admission_number):
            raise ConflictError(f"Admission number {data.admission_number} already exists")
        self._ensure_classroom(data.classroom_id)
        with transaction(self.db):
            student = self.students.add(Student(**data.model_dump()))
        log.info("student created id=%s adm=%s", student.id, student.admission_number)
        return student

    def get(self, student_id: int) -> Student:
        student = self.students.get_active(student_id)
        if student is None:
            raise NotFoundError(f"Student {student_id} not found")
        return student

    def list(self, filters: StudentFilters) -> Page[StudentRead]:
        items, total = self.students.search(
            q=filters.q,
            classroom_id=filters.classroom_id,
            status=filters.status,
            offset=filters.offset,
            limit=filters.size,
        )
        return Page.build([StudentRead.model_validate(s) for s in items], total, filters.page, filters.size)

    def update(self, student_id: int, data: StudentUpdate) -> Student:
        student = self.get(student_id)
        changes = data.model_dump(exclude_unset=True)
        self._ensure_classroom(changes.get("classroom_id"))
        with transaction(self.db):
            for field, value in changes.items():
                setattr(student, field, value)
        log.info("student updated id=%s fields=%s", student_id, sorted(changes))
        return student

    def delete(self, student_id: int) -> None:
        student = self.get(student_id)
        with transaction(self.db):
            self.students.soft_delete(student)
        log.info("student soft-deleted id=%s", student_id)
