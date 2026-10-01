from sqlalchemy import select

from app.models.classroom import Classroom
from app.repositories.base import BaseRepository


class ClassroomRepository(BaseRepository[Classroom]):
    model = Classroom

    def list_all(self) -> list[Classroom]:
        stmt = select(Classroom).order_by(Classroom.academic_year.desc(), Classroom.grade, Classroom.section)
        return list(self.db.scalars(stmt).all())
