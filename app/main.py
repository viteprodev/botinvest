import logging
import sys
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from telegram.ext import Application

from app.database import init_db
from app.bot import create_bot_application

# Logging config
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Global variable to hold the bot application
bot_app: Application = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up FastAPI application...")
    
    # Initialize Database
    init_db()
    
    # Create Bot Application
    global bot_app
    bot_app = create_bot_application()
    
    # Initialize and Start Bot
    await bot_app.initialize()
    await bot_app.start()
    
    # Start Polling (non-blocking in this context, but we need to manage the updater)
    # Since run_polling blocks, we construct the updater manually or start it in a way that doesn't block FastAPI.
    # But wait, run_polling is blocking. We should use start_polling() which is async but we need to keep it running.
    # Actually, Application.start() starts the bot. Application.updater.start_polling() starts the receiving updates.
    
    if bot_app.updater is None:
        # Re-initialize updater if needed? 
        # ApplicationBuilder().build() creates the updater if we don't provide one? Yes.
        pass

    logger.info("Starting Telegram Bot Polling...")
    await bot_app.updater.start_polling()

    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI application...")
    if bot_app.updater.running:
        await bot_app.updater.stop()
    if bot_app.running:
        await bot_app.stop()
    await bot_app.shutdown()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Bot is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
