from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters, CommandHandler
from app.database import get_db
from app.services.payment_service import PaymentService
import logging
import warnings
from telegram.warnings import PTBUserWarning

warnings.filterwarnings("ignore", category=PTBUserWarning, message="If 'per_message=False'")

logger = logging.getLogger(__name__)

INPUT_AMOUNT = range(1)

async def start_withdraw_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Starting withdrawal flow")
    query = update.callback_query
    await query.answer()
    
    await query.message.reply_text("Silakan ketik nominal yang ingin ditarik (Contoh: 50000):")
    logger.info("Returning INPUT_AMOUNT state")
    return INPUT_AMOUNT

async def process_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Processing withdraw input: {update.message.text}")
    text = update.message.text
    if not text.isdigit():
        logger.warning(f"Invalid input: {text}")
        await update.message.reply_text("Mohon masukkan angka saja.")
        return INPUT_AMOUNT
        
    amount = float(text)
    user_id = update.effective_user.id
    logger.info(f"User {user_id} requesting withdrawal of {amount}")
    
    try:
        db = next(get_db())
        service = PaymentService(db)
        user_repo = service.user_repo # Re-use info
    except Exception as e:
        logger.error(f"Error initializing DB or Service: {e}")
        await update.message.reply_text("Terjadi kesalahan sistem.")
        return ConversationHandler.END
    
    keyboard = [[InlineKeyboardButton("🔙 Kembali ke Menu", callback_data="back_to_menu")]]

    # 1. Validation: Minimum Amount
    if amount < 1000000:
        await update.message.reply_text(
            "⚠️ **Minimal Penarikan**\n"
            "Minimal penarikan dana adalah **Rp 1.000.000**.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return ConversationHandler.END

    # 2. Validation: VIP Only
    user = user_repo.get_by_telegram_id(user_id)
    if not user.is_vip:
        await update.message.reply_text(
            "🔒 **Akses Dibatasi**\n"
            "Penarikan dana hanya tersedia untuk **Member VIP**.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return ConversationHandler.END

    # 3. Validation: 3x Approved Topup
    topup_count = service.count_approved_topups(user.id)
    if topup_count < 3:
        await update.message.reply_text(
            "⚠️ **Syarat Penarikan**\n"
            f"Anda baru melakukan {topup_count}x Topup.\n"
            "Syarat penarikan adalah minimal **3x Topup** yang disetujui.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return ConversationHandler.END
    
    try:
        tx = service.request_withdraw(user_id, amount)
        await update.message.reply_text(
            f"✅ Permintaan withdraw Rp {amount:,.0f} berhasil dibuat.\n"
            f"ID Transaksi: {tx.id}\n"
            "Admin akan memprosesnya.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        # Notify Admins with actions
        from app.services.notification_service import notify_admins
        
        admin_keyboard = [
            [InlineKeyboardButton("✅ Approve", callback_data=f"admin_approve_{tx.id}"),
             InlineKeyboardButton("🚫 Reject", callback_data=f"admin_reject_{tx.id}")]
        ]
        
        msg_admin = (
            f"💸 **Withdrawal Request**\n"
            f"User: {update.effective_user.mention_html()}\n"
            f"ID: `{user_id}`\n"
            f"Amt: **Rp {amount:,.0f}**\n"
            f"Tx ID: #{tx.id}"
        )
        await notify_admins(context, msg_admin, reply_markup=InlineKeyboardMarkup(admin_keyboard))

    except ValueError as e:
        await update.message.reply_text(f"❌ Gagal: {str(e)}", reply_markup=InlineKeyboardMarkup(keyboard))
        
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🔙 Kembali ke Menu", callback_data="back_to_menu")]]
    await update.message.reply_text("Dibatalkan.", reply_markup=InlineKeyboardMarkup(keyboard))
    return ConversationHandler.END

withdraw_handler_obj = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(start_withdraw_flow, pattern="^withdraw_start$"),
        CommandHandler("withdraw", start_withdraw_flow)
    ],
    states={
        INPUT_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_withdraw)]
    },
    fallbacks=[CallbackQueryHandler(cancel, pattern="^cancel$")]
)
