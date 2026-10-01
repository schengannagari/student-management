"""Domain exceptions. The API layer maps these to HTTP responses in one place."""


class AppError(Exception):
    status_code = 500
    code = "internal_error"
    default_message = "Internal server error"

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message
        super().__init__(self.message)


class NotFoundError(AppError):
    status_code, code, default_message = 404, "not_found", "Resource not found"


class ConflictError(AppError):
    status_code, code, default_message = 409, "conflict", "Resource conflict"


class AuthenticationError(AppError):
    status_code, code, default_message = 401, "unauthenticated", "Authentication required"


class PermissionDeniedError(AppError):
    status_code, code, default_message = 403, "forbidden", "Insufficient permissions"
