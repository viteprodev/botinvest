import logging
import sys
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

from app.config import BOT_TOKEN
from app.database import init_db
from app.handlers.start import start, help_command, check_balance_callback, balance_command
from app.handlers.admin import approve_topup, reject_topup, set_mandiri
from app.handlers.topup import topup_handler_obj
from app.handlers.withdraw import withdraw_handler_obj
from app.handlers.calculator import calculator_handler_obj
from app.handlers.wallet import wallet_handler_obj
from app.handlers.event import event_handlers
from app.handlers.history import history_handler_obj
from app.handlers.info import info_handlers
# Ensure models are loaded
from app.models.setting import Setting

# ...

async def main():
    # ...
    # Add handlers
    
    # New Features
    for handler in event_handlers:
        application.add_handler(handler)
    application.add_handler(history_handler_obj)
    for handler in info_handlers:
        application.add_handler(handler)
        
    application.add_handler(topup_handler_obj)
    application.add_handler(withdraw_handler_obj)
    application.add_handler(calculator_handler_obj)
    application.add_handler(wallet_handler_obj)

# Logging config
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def main():
    # Initialize Database
    init_db()
    
    # Build Application
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("saldo", balance_command))
    
    # Admin
    application.add_handler(CommandHandler("approve", approve_topup))
    application.add_handler(CommandHandler("reject", reject_topup))
    application.add_handler(CommandHandler("set_mandiri", set_mandiri))
    application.add_handler(CallbackQueryHandler(approve_topup, pattern="^admin_approve_"))
    application.add_handler(CallbackQueryHandler(reject_topup, pattern="^admin_reject_"))
    
    # Flows
    application.add_handler(topup_handler_obj)
    application.add_handler(withdraw_handler_obj)
    application.add_handler(calculator_handler_obj)
    application.add_handler(wallet_handler_obj)
    
    # Callbacks (Menu)
    application.add_handler(CallbackQueryHandler(check_balance_callback, pattern="^check_balance$"))
    application.add_handler(CallbackQueryHandler(start, pattern="^back_to_menu$"))
    
    logger.info("Bot is running...")
    
    # Render Background Worker requires a long-running process.
    # checking update types
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
