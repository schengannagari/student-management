from fastapi import APIRouter

from app.api.deps import AuthSvc, CurrentUser
from app.schemas.auth import LoginRequest, TokenResponse, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, svc: AuthSvc) -> TokenResponse:
    return TokenResponse(access_token=svc.login(body.username, body.password))


@router.get("/me", response_model=UserRead)
def me(user: CurrentUser) -> UserRead:
    return UserRead.model_validate(user)
