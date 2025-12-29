from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.database import get_db
from app.services.user_service import UserService

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    if query:
        await query.answer()
        user = query.from_user
    else:
        user = update.effective_user
        
    db = next(get_db())
    service = UserService(db)
     
    db_user = service.register_user(user.id, user.username, user.full_name)
    
    vip_badge = " 👑 **VIP MEMBER**" if db_user.is_vip else ""
    
    message = (
        f"Halo {user.first_name}! Selamat datang di Bot Investasi.{vip_badge}\n"
        "Gunakan menu di bawah ini untuk memulai."
    )
    
    keyboard = [
        [InlineKeyboardButton("💰 Topup", callback_data="topup_start"), InlineKeyboardButton("💳 Saldo", callback_data="check_balance")],
        [InlineKeyboardButton("💸 Withdraw", callback_data="withdraw_start")],
        [InlineKeyboardButton("🏆 Bonus & Event", callback_data="event_start"), InlineKeyboardButton("📜 Riwayat", callback_data="history_start")],
        [InlineKeyboardButton("ℹ️ Info / FAQ", callback_data="info_start")],
        [InlineKeyboardButton("🧮 Calculator", callback_data="calc_start"), InlineKeyboardButton("🔗 Connect Wallet", callback_data="connect_wallet")]
    ]
    
    if query:
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bantuan:\n"
        "/start - Mulai bot\n"
        "/topup - Isi saldo\n"
        "/withdraw - Tarik dana\n"
        "/saldo - Cek saldo"
    )

async def check_balance_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    db = next(get_db())
    service = UserService(db)
    
    balance = service.get_balance(user_id)
    
    keyboard = [[InlineKeyboardButton("🔙 Kembali ke Menu", callback_data="back_to_menu")]]
    await query.edit_message_text(f"💰 Saldo Anda saat ini: Rp {balance:,.0f}", reply_markup=InlineKeyboardMarkup(keyboard))

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db = next(get_db())
    service = UserService(db)
    
    balance = service.get_balance(user_id)
    # Command usually just replies, but we can add inline button too if we want. For now, prompt instruction is menu navigation.
    await update.message.reply_text(f"💰 Saldo Anda saat ini: Rp {balance:,.0f}")
