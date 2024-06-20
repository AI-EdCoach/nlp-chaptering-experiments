from pydantic import BaseModel


class NewVideoSchema(BaseModel):
    name: str
