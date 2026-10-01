from fastapi import APIRouter, status

from app.api.deps import READERS, WRITERS, ClassroomSvc
from app.schemas.classroom import ClassroomCreate, ClassroomRead

router = APIRouter(prefix="/classrooms", tags=["classrooms"])


@router.post("", response_model=ClassroomRead, status_code=status.HTTP_201_CREATED, dependencies=[WRITERS])
def create_classroom(body: ClassroomCreate, svc: ClassroomSvc) -> ClassroomRead:
    return ClassroomRead.model_validate(svc.create(body))


@router.get("", response_model=list[ClassroomRead], dependencies=[READERS])
def list_classrooms(svc: ClassroomSvc) -> list[ClassroomRead]:
    return [ClassroomRead.model_validate(c) for c in svc.list()]
