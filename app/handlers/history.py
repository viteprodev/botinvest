from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from app.database import get_db
from app.models.transaction import Transaction
from app.services.user_service import UserService

async def history_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    db = next(get_db())
    service = UserService(db)
    user = service.user_repo.get_by_telegram_id(user_id)
    
    keyboard = [[InlineKeyboardButton("🔙 Kembali ke Menu", callback_data="back_to_menu")]]
    
    if not user:
        await query.edit_message_text("Data tidak ditemukan.", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # Get last 10 transactions
    transactions = db.query(Transaction).filter(Transaction.user_id == user.id).order_by(Transaction.created_at.desc()).limit(10).all()
    
    if not transactions:
        await query.edit_message_text("📜 **Riwayat Transaksi**\n\nBelum ada transaksi.", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        return
        
    text = "📜 **Riwayat Transaksi (Terakhir 10)**\n\n"
    for tx in transactions:
        status_icon = "⏳" if tx.status.name == "PENDING" else ("✅" if tx.status.name == "APPROVED" else "❌")
        # tx.type is an enum, convert to string
        tx_type = tx.type.value if hasattr(tx.type, 'value') else str(tx.type)
        
        date_str = tx.created_at.strftime("%d-%m %H:%M")
        text += f"{status_icon} **{tx_type}** Rp {tx.amount:,.0f}\n"
        text += f"📅 {date_str} | ID: #{tx.id}\n\n"
        
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

history_handler_obj = CallbackQueryHandler(history_menu, pattern="^history_start$")
