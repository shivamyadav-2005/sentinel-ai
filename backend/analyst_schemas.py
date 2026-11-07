
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AnalystChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    question: str = Field(min_length=1, max_length=1000)
    findings: list[dict] = Field(min_length=1)


class AnalystChatResponse(BaseModel):
    answer: str
    priority: Literal["HIGH", "MEDIUM", "LOW"]
    source: Literal["rule_based_analysis"]

    risk_score: int | None = Field(default=None, ge=0, le=100)
    risk_level: Literal["HIGH", "MEDIUM", "LOW", "INFO"] | None = None
    risk_explanation: str | None = None
