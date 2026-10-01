from enum import StrEnum


class Gender(StrEnum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class StudentStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    GRADUATED = "graduated"
    TRANSFERRED = "transferred"


class Role(StrEnum):
    ADMIN = "admin"
    REGISTRAR = "registrar"  # can create/update students
    TEACHER = "teacher"  # read-only
