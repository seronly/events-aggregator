import uuid

from pydantic import BaseModel, EmailStr, Field


class TicketCreateQuerySchema(BaseModel):
    event_id: uuid.UUID
    first_name: str = Field(min_length=1, max_length=255)
    last_name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    seat: str = Field(min_length=1, max_length=50)


class TicketCreateSchema(BaseModel):
    ticket_id: uuid.UUID


class TicketDeleteSchema(BaseModel):
    success: bool
