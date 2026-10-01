from enum import Enum as PyEnum

from sqlalchemy import Enum


def str_enum(e: type[PyEnum]) -> Enum:
    """Portable enum: stored as VARCHAR (not a native DB enum), by value."""
    return Enum(e, native_enum=False, length=20, values_callable=lambda x: [m.value for m in x])
