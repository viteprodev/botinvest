from pydantic import BaseModel

class CalculatorRequest(BaseModel):
    amount: float

class CalculatorResponse(BaseModel):
    capital: float
    roi_monthly: float
    roi_yearly: float
    total_yearly: float
    is_valid_amount: bool
