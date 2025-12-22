from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from app.database import get_db
from app.services.user_service import UserService
from datetime import datetime, timezone

async def connect_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    db = next(get_db())
    service = UserService(db)
    user = service.user_repo.get_by_telegram_id(user_id)
    
    keyboard = [[InlineKeyboardButton("🔙 Kembali ke Menu", callback_data="back_to_menu")]]
    
    if not user:
        await query.message.reply_text("❌ User tidak ditemukan.", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # Check constraints
    # 1. 6 months account age
    now = datetime.now(timezone.utc)
    # Ensure joined_at is timezone-aware if possible, assuming user.joined_at is stored with timezone or is naive UTC
    # Based on models/user.py: joined_at = Column(DateTime(timezone=True), server_default=func.now())
    # So it should be timezone aware.
    
    if user.joined_at:
         # simple delta check
        delta = now - user.joined_at
        days_active = delta.days
        months_active = days_active / 30  # Approximation
        
        if months_active < 6:
            await query.message.reply_text(
                "❌ **Gagal Connect Wallet**\n\n"
                "Syarat tidak terpenuhi:\n"
                f"- Umur akun minimal 6 bulan (Anda: {months_active:.1f} bulan)",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return
            
    # 2. Balance >= 3,000,000
    if user.balance < 3000000:
        await query.message.reply_text(
            "❌ **Gagal Connect Wallet**\n\n"
            "Syarat tidak terpenuhi:\n"
            f"- Saldo minimal Rp 3.000.000 (Anda: Rp {user.balance:,.0f})",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # Success
    await query.message.reply_text(
        "✅ **Connect Wallet Berhasil!**\n\n"
        "Dompet Anda telah terhubung. Silakan cek menu Wallet untuk fitur lebih lanjut.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

wallet_handler_obj = CallbackQueryHandler(connect_wallet, pattern="^connect_wallet$")
