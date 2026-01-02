from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import users, transactions, calculator, auth, events

app = FastAPI(
    title="BotInvest API",
    description="API Backend for BotInvest Telegram Bot",
    version="1.0.0",
)

# CORS Middleware
origins = [
    "http://localhost",
    "http://localhost:3000",
    "*" # For development mostly
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(events.router, prefix="/events", tags=["Events"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
app.include_router(calculator.router, prefix="/calculator", tags=["Calculator"])

@app.get("/")
def read_root():
    return {"message": "Welcome to BotInvest API"}
