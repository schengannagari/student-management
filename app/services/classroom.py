from sqlalchemy.orm import Session

from app.models.classroom import Classroom
from app.repositories.classroom import ClassroomRepository
from app.schemas.classroom import ClassroomCreate
from app.services._tx import transaction


class ClassroomService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ClassroomRepository(db)

    def create(self, data: ClassroomCreate) -> Classroom:
        with transaction(self.db):  # unique constraint violation -> 409
            return self.repo.add(Classroom(**data.model_dump()))

    def list(self) -> list[Classroom]:
        return self.repo.list_all()
