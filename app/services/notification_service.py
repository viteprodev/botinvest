import logging
import asyncio
from telegram.ext import ContextTypes
from app.config import ADMIN_IDS

logger = logging.getLogger(__name__)

async def notify_admins(context: ContextTypes.DEFAULT_TYPE, message: str, reply_markup=None):
    """
    Sends a notification message to all admins defined in ADMIN_IDS.
    """
    if not ADMIN_IDS:
        logger.warning("No ADMIN_IDS configured. Notification skipped.")
        return

    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(chat_id=admin_id, text=message, reply_markup=reply_markup, parse_mode="HTML")
            logger.info(f"Notification sent to admin {admin_id}")
        except Exception as e:
            logger.error(f"Failed to send notification to admin {admin_id}: {e}")
