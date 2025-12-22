from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters, CommandHandler
from app.database import get_db
from app.services.payment_service import PaymentService
from app.config import ADMIN_IDS
from datetime import datetime


SELECT_AMOUNT, MANUAL_AMOUNT, SELECT_BANK, UPLOAD_PROOF = range(4)

BANKS = {
    "BCA": "090153384250 (BCA Digital) a/n Reza Alvian Aditya",
    "MANDIRI": "0987654321 a/n PT Investasi", # Dynamic
    "BRI": "2240 0101 5552 503 a/n Reza Alvian Aditya",
    "BNI": "1921240097 a/n Reza Alvian Aditya",
    "EWALLET": "081234567890 (Dana/OVO) a/n Reza Alvian Aditya"
}

async def start_topup_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
        # If triggered by button
        target_message = query.edit_message_text
    else:
        # If triggered by command
        target_message = update.message.reply_text

    keyboard = [
        [InlineKeyboardButton("100.000", callback_data="100000")],
        [InlineKeyboardButton("500.000", callback_data="500000")],
        [InlineKeyboardButton("1.000.000", callback_data="1000000")],
        [InlineKeyboardButton("✏️ Nominal Lain", callback_data="manual")],
        [InlineKeyboardButton("❌ Batal", callback_data="cancel")]
    ]
    
    if query:
        await query.edit_message_text("Pilih nominal Topup:", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text("Pilih nominal Topup:", reply_markup=InlineKeyboardMarkup(keyboard))
        
    return SELECT_AMOUNT

async def show_bank_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, is_new_message=False):
    amount = context.user_data["topup_amount"]
    keyboard = [
        [InlineKeyboardButton("BCA", callback_data="BCA"), InlineKeyboardButton("Mandiri", callback_data="MANDIRI")],
        [InlineKeyboardButton("BRI", callback_data="BRI"), InlineKeyboardButton("BNI", callback_data="BNI")],
        [InlineKeyboardButton("E-Wallet (Dana/OVO)", callback_data="EWALLET")],
        [InlineKeyboardButton("❌ Batal", callback_data="cancel")]
    ]
    text = f"Topup: Rp {amount:,.0f}\nSilakan pilih metode pembayaran:"
    
    if is_new_message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    return SELECT_BANK

async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "cancel":
        await query.edit_message_text("Topup dibatalkan.")
        return ConversationHandler.END
        
    if query.data == "manual":
        await query.edit_message_text("Silakan ketik nominal Topup (Minimal Rp 10.000):")
        return MANUAL_AMOUNT
        
    amount = int(query.data)
    
    # Temporary Promo Check
    limit_date = datetime(2025, 12, 26, 23, 59, 59)
    if datetime.now() <= limit_date:
        if amount < 500000:
            await query.edit_message_text(
                "⚠️ **Promo Khusus!**\n\n"
                "Minimal Topup adalah **Rp 500.000** sampai tanggal 26 Desember.",
                parse_mode="Markdown"
            )
            # End conversation or let them try again?
            # User likely needs to click Start/Topup again or Back. 
            # To be safe, we can add a Back button.
            keyboard = [[InlineKeyboardButton("🔙 Kembali ke Menu", callback_data="back_to_menu")]]
            await query.edit_message_text(
                "⚠️ **Promo Khusus!**\n\n"
                "Minimal Topup adalah **Rp 500.000** sampai tanggal 26 Desember.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return ConversationHandler.END
            
    context.user_data["topup_amount"] = amount
    
    return await show_bank_selection(update, context, is_new_message=False)

async def receive_manual_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace(".", "").replace(",", "")
    if not text.isdigit():
        await update.message.reply_text("⚠️ Harap masukkan angka saja.")
        return MANUAL_AMOUNT
        
    amount = int(text)
    if amount < 10000:
        await update.message.reply_text("⚠️ Minimal Topup adalah Rp 10.000.")
        return MANUAL_AMOUNT
        
    # Temporary Promo Check
    limit_date = datetime(2025, 12, 26, 23, 59, 59)
    if datetime.now() <= limit_date:
        if amount < 500000:
            await update.message.reply_text(
                "⚠️ **Promo Khusus!**\n\n"
                "Minimal Topup adalah **Rp 500.000** sampai tanggal 26 Desember.",
                parse_mode="Markdown"
            )
            return MANUAL_AMOUNT
            
    context.user_data["topup_amount"] = amount
    return await show_bank_selection(update, context, is_new_message=True)

async def back_to_bank_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    return await show_bank_selection(update, context, is_new_message=False)

async def get_bank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "cancel":
        keyboard = [[InlineKeyboardButton("🔙 Kembali ke Menu", callback_data="back_to_menu")]]
        await query.edit_message_text("Topup dibatalkan.", reply_markup=InlineKeyboardMarkup(keyboard))
        return ConversationHandler.END
        
    db = next(get_db())
    # Dynamic settings override
    from app.services.setting_service import SettingService
    setting_service = SettingService(db)
    mandiri_acc = setting_service.get_setting("mandiri_rekening", BANKS["MANDIRI"])
    
    # Update local BANKS dict for this request (or just use variable)
    # Better to just use the variable for display if selected
    
    bank_code = query.data
    bank_info = BANKS.get(bank_code, "Hubungi Admin")
    
    if bank_code == "MANDIRI":
        bank_info = mandiri_acc
        
    amount = context.user_data["topup_amount"]
    
    keyboard = [[InlineKeyboardButton("🔄 Ganti Bank", callback_data="change_bank")]]
    
    fee = amount * 0.025
    total_transfer = amount + fee
    
    await query.edit_message_text(
        f"📝 **Rincian Topup**\n"
        f"Nominal: Rp {amount:,.0f}\n"
        f"Biaya Admin (2.5%): Rp {fee:,.0f}\n"
        f"**Total Transfer: Rp {total_transfer:,.0f}**\n\n"
        f"Bank Tujuan: {bank_code}\n"
        f"Rekening: `{bank_info}`\n\n"
        "💡 _Transaksi ini diawasi oleh Kementerian Keuangan dan Bank Indonesia._\n\n"
        "📸 Silakan transfer SESUAI TOTAL dan kirimkan FOTO BUKTI transfer sekarang.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return UPLOAD_PROOF

async def receive_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    # In a real app, download to S3 or similar. Here we just store the file_id or download URL.
    proof_url = photo_file.file_path
    
    amount = context.user_data["topup_amount"]
    user_id = update.effective_user.id
    
    db = next(get_db())
    service = PaymentService(db)
    
    tx = service.create_topup(user_id, amount, proof_url)
    
    keyboard = [[InlineKeyboardButton("🔙 Kembali ke Menu", callback_data="back_to_menu")]]
    await update.message.reply_text(
        f"✅ Bukti diterima!\n"
        f"ID Transaksi: {tx.id}\n"
        "Admin akan memverifikasi secepatnya.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    # Notify Admins
    keyboard = [
        [InlineKeyboardButton("✅ Approve", callback_data=f"admin_approve_{tx.id}"),
         InlineKeyboardButton("🚫 Reject", callback_data=f"admin_reject_{tx.id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    fee = amount * 0.025
    total_transfer = amount + fee

    caption = (
        f"🔔 **Topup Baru**\n"
        f"User: {update.effective_user.mention_html()}\n"
        f"ID: `{user_id}`\n"
        f"Amt: Rp {amount:,.0f}\n"
        f"Fee: Rp {fee:,.0f}\n"
        f"**Total: Rp {total_transfer:,.0f}**\n"
        f"Tx ID: #{tx.id}"
    )

    for admin_id in ADMIN_IDS:
        try:
            # We send the photo using the file_id (proof_url here is likely file_path/id)
            # CAUTION: proof_url from get_file() might be a path or URL. 
            # If it's a file_id (which update.message.photo[-1].file_id is), we should use that.
            # But in receive_proof we did: photo_file = ... get_file(); proof_url = photo_file.file_path
            # Re-using the file_id from the message is safer for internal forwarding if possible.
            # Let's use the file_id from the message directly
            file_id = update.message.photo[-1].file_id
            await context.bot.send_photo(
                chat_id=admin_id,
                photo=file_id,
                caption=caption,
                parse_mode="HTML",
                reply_markup=reply_markup
            )
        except Exception as e:
            print(f"Failed to notify admin {admin_id}: {e}")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🔙 Kembali ke Menu", callback_data="back_to_menu")]]
    await update.message.reply_text("Dibatalkan.", reply_markup=InlineKeyboardMarkup(keyboard))
    return ConversationHandler.END

topup_handler_obj = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(start_topup_flow, pattern="^topup_start$"),
        CommandHandler("topup", start_topup_flow)
    ],
    states={
        SELECT_AMOUNT: [CallbackQueryHandler(get_amount)],
        MANUAL_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_manual_amount)],
        SELECT_BANK: [
            CallbackQueryHandler(back_to_bank_selection, pattern="^change_bank$"),
            CallbackQueryHandler(get_bank)
        ],
        UPLOAD_PROOF: [
            MessageHandler(filters.PHOTO, receive_proof),
            CallbackQueryHandler(back_to_bank_selection, pattern="^change_bank$") 
        ],
    },
    fallbacks=[CallbackQueryHandler(cancel, pattern="^cancel$")]
)
