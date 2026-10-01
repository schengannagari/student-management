from typing import Annotated

from fastapi import APIRouter, Query, Response, status

from app.api.deps import READERS, WRITERS, StudentSvc
from app.schemas.common import Page
from app.schemas.student import StudentCreate, StudentFilters, StudentRead, StudentUpdate

router = APIRouter(prefix="/students", tags=["students"])


@router.post("", response_model=StudentRead, status_code=status.HTTP_201_CREATED, dependencies=[WRITERS])
def create_student(body: StudentCreate, svc: StudentSvc) -> StudentRead:
    return StudentRead.model_validate(svc.create(body))


@router.get("", response_model=Page[StudentRead], dependencies=[READERS])
def list_students(filters: Annotated[StudentFilters, Query()], svc: StudentSvc) -> Page[StudentRead]:
    return svc.list(filters)


@router.get("/{student_id}", response_model=StudentRead, dependencies=[READERS])
def get_student(student_id: int, svc: StudentSvc) -> StudentRead:
    return StudentRead.model_validate(svc.get(student_id))


@router.patch("/{student_id}", response_model=StudentRead, dependencies=[WRITERS])
def update_student(student_id: int, body: StudentUpdate, svc: StudentSvc) -> StudentRead:
    return StudentRead.model_validate(svc.update(student_id, body))


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[WRITERS])
def delete_student(student_id: int, svc: StudentSvc) -> Response:
    svc.delete(student_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
