from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EchoRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    sender: str = "anonymous"


class EchoResponse(BaseModel):
    message: str
    sender: str
    success: bool


class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None


class TodoUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    completed: bool | None = None


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    action: str
    details: str | None
    todo_id: int | None
    created_at: datetime


class TodoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    updated_at: datetime
    logs: list[AuditLogResponse] = []