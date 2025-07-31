from pydantic import BaseModel

class CountResponse(BaseModel):
    quantidade: int
