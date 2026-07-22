from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    first_name: str = Field(..., max_length=200)
    last_name: str = Field(..., max_length=200)
    email: str = Field(..., max_length=255)


class UserUpdate(BaseModel):
    first_name: str = Field(..., max_length=200)
    last_name: str = Field(..., max_length=200)
    email: str = Field(..., max_length=255)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    email: str
