from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.enums import Gender, StudentStatus
from app.schemas.common import PageParams

Name = Annotated[str, Field(min_length=1, max_length=80, strip_whitespace=True)]
Phone = Annotated[str, Field(pattern=r"^\+?[0-9]{7,15}$")]


class StudentBase(BaseModel):
    first_name: Name
    last_name: Name
    date_of_birth: date
    gender: Gender
    email: EmailStr | None = None
    phone: Phone | None = None
    guardian_name: Annotated[str, Field(min_length=1, max_length=120)]
    guardian_phone: Phone
    address: str | None = Field(None, max_length=1000)
    classroom_id: int | None = None

    @field_validator("date_of_birth")
    @classmethod
    def _dob_in_past(cls, v: date) -> date:
        if v >= date.today():
            raise ValueError("date_of_birth must be in the past")
        return v


class StudentCreate(StudentBase):
    admission_number: Annotated[str, Field(min_length=3, max_length=30, pattern=r"^[A-Za-z0-9\-/]+$")]


class StudentUpdate(BaseModel):
    """PATCH semantics: only fields that are sent are changed."""

    first_name: Name | None = None
    last_name: Name | None = None
    date_of_birth: date | None = None
    gender: Gender | None = None
    email: EmailStr | None = None
    phone: Phone | None = None
    guardian_name: Annotated[str, Field(min_length=1, max_length=120)] | None = None
    guardian_phone: Phone | None = None
    address: str | None = Field(None, max_length=1000)
    classroom_id: int | None = None
    status: StudentStatus | None = None


class StudentRead(StudentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    admission_number: str
    status: StudentStatus
    created_at: datetime
    updated_at: datetime


class StudentFilters(PageParams):
    q: str | None = Field(None, min_length=1, max_length=80, description="Prefix search")
    classroom_id: int | None = None
    status: StudentStatus | None = None
