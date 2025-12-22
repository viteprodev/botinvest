from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from app.database import get_db
from app.services.user_service import UserService

async def event_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🎁 Claim Bonus Rp 500.000", callback_data="claim_bonus")],
        [InlineKeyboardButton("🔙 Kembali ke Menu", callback_data="back_to_menu")]
    ]
    
    text = (
        "🎉 **Event & Hadiah**\n\n"
        "**Bonus Pengguna Baru!**\n"
        "Dapatkan bonus saldo **Rp 500.000** setelah melakukan transaksi Topup pertama kali.\n\n"
        "Klik tombol di bawah untuk klaim!"
    )
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def claim_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    db = next(get_db())
    service = UserService(db)
    
    keyboard = [[InlineKeyboardButton("🔙 Kembali ke Menu", callback_data="back_to_menu")]]
    
    try:
        service.claim_bonus(user_id)
        await query.edit_message_text(
            "✅ **Selamat! Bonus Berhasil Diklaim**\n\n"
            "Saldo tambahan Rp 500.000 telah masuk ke akun Anda.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except ValueError as e:
        await query.edit_message_text(
            f"❌ **Gagal Klaim Bonus**\n\n{str(e)}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

event_handlers = [
    CallbackQueryHandler(event_menu, pattern="^event_start$"),
    CallbackQueryHandler(claim_bonus, pattern="^claim_bonus$")
]
