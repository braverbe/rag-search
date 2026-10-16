
from fastapi import FastAPI
from app.app_answerer import router as answer_router
from app.app_rag.router import router as rag_router
app = FastAPI()

app.include_router(answer_router)
app.include_router(rag_router)
