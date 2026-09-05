import uuid

from pydantic import BaseModel


class PlaceSchema(BaseModel):
    id: uuid.UUID
    name: str
    city: str
    address: str

class PlaceDetailSchema(PlaceSchema):
    seats_pattern: str
