from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters, CommandHandler
from app.database import get_db
from app.services.payment_service import PaymentService

INPUT_AMOUNT = range(1)

async def start_withdraw_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.message.reply_text("Silakan ketik nominal yang ingin ditarik (Contoh: 50000):")
    return INPUT_AMOUNT

async def process_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text.isdigit():
        await update.message.reply_text("Mohon masukkan angka saja.")
        return INPUT_AMOUNT
        
    amount = float(obj=text)
    user_id = update.effective_user.id
    
    db = next(get_db())
    service = PaymentService(db)
    
    keyboard = [[InlineKeyboardButton("🔙 Kembali ke Menu", callback_data="back_to_menu")]]
    
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
