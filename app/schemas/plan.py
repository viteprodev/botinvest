from pydantic import BaseModel
from typing import List, Optional

class PlanBase(BaseModel):
    name: str
    roi_daily: float
    duration_days: int
    min_amount: float
    max_amount: float
    description: Optional[str] = None
    features: List[str] = []
    color_gradient: str  # e.g., "from-blue-500 to-cyan-400"

class PlanCreate(PlanBase):
    pass

class PlanResponse(PlanBase):
    id: int
    is_popular: bool = False

    class Config:
        from_attributes = True

class InvestCreate(BaseModel):
    telegram_id: int
    plan_id: int
    amount: float
