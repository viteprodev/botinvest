from telegram import Update
from telegram.ext import ContextTypes
from app.config import ADMIN_IDS
from app.database import get_db
from app.services.payment_service import PaymentService
from app.services.setting_service import SettingService

async def set_mandiri(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Akses ditolak.")
        return

    content = " ".join(context.args)
    if not content:
        await update.message.reply_text("Gunakan: /set_mandiri <nomor_rekening_dan_nama>")
        return

    db = next(get_db())
    service = SettingService(db)
    service.set_setting("mandiri_rekening", content)
    
    await update.message.reply_text(f"✅ Rekening Mandiri diperbarui menjadi:\n`{content}`", parse_mode="Markdown")

async def approve_topup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        if query:
            await query.answer("⛔ Akses ditolak.", show_alert=True)
        else:
            await update.message.reply_text("⛔ Akses ditolak.")
        return

    tx_id = None
    if query:
        await query.answer()
        try:
            tx_id = int(query.data.split("_")[-1])
        except ValueError:
            pass
    elif context.args:
        try:
            tx_id = int(context.args[0])
        except ValueError:
            pass
            
    if tx_id is None:
        if not query:
            await update.message.reply_text("Gunakan: /approve <transaction_id>")
        return

    db = next(get_db())
    service = PaymentService(db)
    
    try:
        tx = service.approve_transaction(tx_id)
        
        # Notify user (Best effort)
        try:
            await context.bot.send_message(
                chat_id=tx.user.telegram_id,
                text=f"✅ Topup #{tx_id} sebesar Rp {tx.amount:,.0f} telah DISETUJUI."
            )
        except Exception:
            pass
            
        msg = f"✅ Transaksi #{tx_id} APPROVED oleh {update.effective_user.first_name}."
        if query:
            await query.edit_message_caption(caption=msg + "\n\n" + query.message.caption)
        else:
            await update.message.reply_text(msg)
            
    except ValueError as e:
        msg = f"❌ Error: {str(e)}"
        if query:
            await query.answer(msg, show_alert=True)
        else:
            await update.message.reply_text(msg)

async def reject_topup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        if query:
            await query.answer("⛔ Akses ditolak.", show_alert=True)
        else:
            await update.message.reply_text("⛔ Akses ditolak.")
        return

    tx_id = None
    if query:
        await query.answer()
        try:
            tx_id = int(query.data.split("_")[-1])
        except ValueError:
            pass
    elif context.args:
        try:
            tx_id = int(context.args[0])
        except ValueError:
            pass
            
    if tx_id is None:
        if not query:
            await update.message.reply_text("Gunakan: /reject <transaction_id>")
        return

    db = next(get_db())
    service = PaymentService(db)
    
    try:
        service.reject_transaction(tx_id)
        msg = f"🚫 Transaksi #{tx_id} REJECTED oleh {update.effective_user.first_name}."
        
        if query:
            await query.edit_message_caption(caption=msg + "\n\n" + query.message.caption)
        else:
            await update.message.reply_text(msg)
            
    except ValueError as e:
        msg = f"❌ Error: {str(e)}"
        if query:
            await query.answer(msg, show_alert=True)
        else:
            await update.message.reply_text(msg)
