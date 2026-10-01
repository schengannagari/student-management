from collections.abc import Callable
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError, PermissionDeniedError
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.enums import Role
from app.models.user import User
from app.services.auth import AuthService
from app.services.classroom import ClassroomService
from app.services.student import StudentService

DbSession = Annotated[Session, Depends(get_db)]
_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    db: DbSession,
) -> User:
    if creds is None:
        raise AuthenticationError("Missing bearer token")
    try:
        payload = decode_access_token(creds.credentials)
        user = db.get(User, int(payload["sub"]))
    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        raise AuthenticationError("Invalid or expired token") from exc
    if user is None or not user.is_active:
        raise AuthenticationError("Invalid or expired token")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: Role) -> Callable[[User], User]:
    """RBAC guard: `dependencies=[Depends(require_roles(Role.ADMIN))]`."""

    def checker(user: CurrentUser) -> User:
        if user.role not in roles:
            raise PermissionDeniedError()
        return user

    return checker


def get_student_service(db: DbSession) -> StudentService:
    return StudentService(db)


def get_classroom_service(db: DbSession) -> ClassroomService:
    return ClassroomService(db)


def get_auth_service(db: DbSession) -> AuthService:
    return AuthService(db)


StudentSvc = Annotated[StudentService, Depends(get_student_service)]
ClassroomSvc = Annotated[ClassroomService, Depends(get_classroom_service)]
AuthSvc = Annotated[AuthService, Depends(get_auth_service)]

WRITERS = Depends(require_roles(Role.ADMIN, Role.REGISTRAR))
READERS = Depends(require_roles(Role.ADMIN, Role.REGISTRAR, Role.TEACHER))
