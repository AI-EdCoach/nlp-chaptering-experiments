from pydantic import BaseModel


class ModelBase(BaseModel):
    name: str
    cost: int


class ModelRead(ModelBase):
    id: int
