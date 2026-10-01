from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError
from app.core.security import create_access_token, verify_password
from app.repositories.user import UserRepository


class AuthService:
    def __init__(self, db: Session) -> None:
        self.users = UserRepository(db)

    def login(self, username: str, password: str) -> str:
        user = self.users.get_by_username(username)
        # Same error for unknown user / bad password / disabled: no account enumeration.
        if not user or not user.is_active or not verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid credentials")
        return create_access_token(user.id, user.role.value)
