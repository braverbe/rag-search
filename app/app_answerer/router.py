from fastapi import APIRouter, Depends

from app.app_answerer.service import AnswererService, get_answer_service

router = APIRouter(prefix="/ask")

@router.get("/{question}")
def get_answer(
    question: str,
    service: AnswererService = Depends(get_answer_service),
):
    return service.get_answer(question=question)
