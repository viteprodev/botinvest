from fastapi import APIRouter
from app.schemas.calculator import CalculatorRequest, CalculatorResponse

router = APIRouter()

@router.post("/calculate", response_model=CalculatorResponse)
def calculate_roi(request: CalculatorRequest):
    amount = request.amount
    
    if amount <= 0:
        return CalculatorResponse(
            capital=amount,
            roi_monthly=0,
            roi_yearly=0,
            total_yearly=0,
            is_valid_amount=False
        )

    roi_monthly = amount * 0.05
    roi_yearly = amount * 0.60
    total_yearly = amount + roi_yearly

    return CalculatorResponse(
        capital=amount,
        roi_monthly=roi_monthly,
        roi_yearly=roi_yearly,
        total_yearly=total_yearly,
        is_valid_amount=True
    )
