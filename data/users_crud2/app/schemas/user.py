"""Pydantic schemas for user models."""

from pydantic import BaseModel
from pydantic import Field


class UserCreate(BaseModel):
    """Schema for creating a user."""

    first_name: str = Field(..., min_length=1, max_length=200)
    last_name: str = Field(..., min_length=1, max_length=200)
    email: str = Field(..., max_length=255, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    first_name: str | None = Field(None, min_length=1, max_length=200)
    last_name: str | None = Field(None, min_length=1, max_length=200)
    email: str | None = Field(None, max_length=255, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class UserResponse(BaseModel):
    """Schema for user response."""

    id: int
    first_name: str
    last_name: str
    email: str
