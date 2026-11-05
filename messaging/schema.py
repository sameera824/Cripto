from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


class AgentSignal(BaseModel):
    agent_id: str
    timestamp: datetime
    symbol: str
    action_signal: Literal["BUY", "SELL", "NEUTRAL"]
    confidence: float = Field(ge=0.0, le=1.0)
    metrics: dict = Field(default_factory=dict)
    suggested_stop_loss: Optional[float] = None
    suggested_take_profit: Optional[float] = None
    rationale: str = ""
