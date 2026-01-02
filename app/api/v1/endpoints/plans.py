from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.plan import PlanResponse, InvestCreate
from app.api import deps
from sqlalchemy.orm import Session

router = APIRouter()

# Mock Plans Data (simulating a database table)
MOCK_PLANS = [
    {
        "id": 1,
        "name": "Starter Plan",
        "roi_daily": 3.5,
        "duration_days": 7,
        "min_amount": 50.0,
        "max_amount": 500.0,
        "description": "Perfect for beginners testing the platform.",
        "features": ["Daily Accrual", "24/7 Support", "Cancel Anytime"],
        "color_gradient": "from-blue-500 to-cyan-400",
        "is_popular": False
    },
    {
        "id": 2,
        "name": "Golden Growth",
        "roi_daily": 5.0,
        "duration_days": 15,
        "min_amount": 500.0,
        "max_amount": 2500.0,
        "description": "Accelerated growth for serious investors.",
        "features": ["Daily Accrual", "VIP Support", "Compound Interest"],
        "color_gradient": "from-amber-400 to-yellow-600",
        "is_popular": True
    },
    {
        "id": 3,
        "name": "Diamond Elite",
        "roi_daily": 7.5,
        "duration_days": 30,
        "min_amount": 2500.0,
        "max_amount": 10000.0,
        "description": "Maximum returns for high-volume portfolios.",
        "features": ["Daily Accrual", "Personal Manager", "Instant Withdrawals"],
        "color_gradient": "from-purple-500 to-pink-500",
        "is_popular": False
    }
]

@router.get("/", response_model=List[PlanResponse])
def get_plans():
    return MOCK_PLANS

@router.post("/invest")
def create_investment(
    investment: InvestCreate,
    db: Session = Depends(deps.get_db)
):
    # Logic to deduct balance and create investment
    # 1. Get User
    # 2. Check Balance >= investment.amount
    # 3. Create Investment Record
    # 4. Deduct Balance
    # 5. Commit
    
    # For MVP, we just verify balance for now.
    from app.repositories.user_repository import UserRepository
    repo = UserRepository(db)
    user = repo.get_by_telegram_id(investment.telegram_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user.balance < investment.amount:
         raise HTTPException(status_code=400, detail="Insufficient balance")
         
    # Mock success
    return {"status": "success", "message": f"Invested ${investment.amount} in plan {investment.plan_id}"}
