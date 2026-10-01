from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

from app.core.exceptions import ConflictError


@contextmanager
def transaction(db: Session) -> Iterator[None]:
    """Commit on success; roll back and translate DB races into domain errors."""
    try:
        yield
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Violates a uniqueness or reference constraint") from exc
    except StaleDataError as exc:
        db.rollback()
        raise ConflictError("Record was modified by someone else; reload and retry") from exc
    except Exception:
        db.rollback()
        raise
