from pydantic import BaseModel

class AnswerResponse(BaseModel):
    text: str
    score: float
    metadata: list
