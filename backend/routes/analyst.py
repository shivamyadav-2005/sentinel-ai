
from fastapi import APIRouter

from backend.analyst_schemas import (
    AnalystChatRequest,
    AnalystChatResponse,
)
from backend.services.analyst import analyze_question

router = APIRouter(prefix="/analyst", tags=["Analyst"])


@router.post("/chat", response_model=AnalystChatResponse)
def analyst_chat(
    request: AnalystChatRequest,
) -> AnalystChatResponse:
    result = analyze_question(
        question=request.question,
        findings=request.findings,
    )

    return AnalystChatResponse(**result)
