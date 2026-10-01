from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class ClassroomCreate(BaseModel):
    grade: Annotated[int, Field(ge=1, le=12)]
    section: Annotated[str, Field(min_length=1, max_length=5)]
    academic_year: Annotated[str, Field(pattern=r"^\d{4}-\d{4}$")]


class ClassroomRead(ClassroomCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
