from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

# This will be used for LLM structured output
class SemanticCrisisResult(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    crisis_detected: bool = Field(..., description="Whether the LLM judged this text as showing crisis risk")
    reason: Optional[str] = Field(default=None, description="Short LLM explanation for its judgment")