from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters, CommandHandler
import warnings
from telegram.warnings import PTBUserWarning

warnings.filterwarnings("ignore", category=PTBUserWarning, message="If 'per_message=False'")

CALC_INPUT = 0

async def start_calculator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(
            "🧮 *Kalkulator Investasi*\n\n"
            "Masukkan jumlah nominal yang ingin Anda investasikan:\n"
            "_(Contoh: 1000000)_",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "🧮 *Kalkulator Investasi*\n\n"
            "Masukkan jumlah nominal yang ingin Anda investasikan:\n"
            "_(Contoh: 1000000)_",
            parse_mode="Markdown"
        )
    return CALC_INPUT

async def calculate_roi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace(".", "").replace(",", "")
    
    if not text.isdigit():
        await update.message.reply_text("⚠️ Harap masukkan angka yang valid.")
        return CALC_INPUT
        
    amount = int(text)
    
    # Simulation: 5% per month, 60% per year
    roi_monthly = amount * 0.05
    roi_yearly = amount * 0.60
    total_yearly = amount + roi_yearly
    
    keyboard = [[InlineKeyboardButton("🔙 Kembali ke Menu", callback_data="back_to_menu")]]
    await update.message.reply_text(
        f"📊 *Hasil Kalkulasi:*\n\n"
        f"Modal: Rp {amount:,.0f}\n"
        f"Estimasi Profit Bulanan (5%): Rp {roi_monthly:,.0f}\n"
        f"Estimasi Profit Tahunan (60%): Rp {roi_yearly:,.0f}\n"
        f"Total 1 Tahun: Rp {total_yearly:,.0f}\n\n"
        "Disclaimer: _Ini hanya estimasi, hasil sebenarnya bisa berbeda._",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ConversationHandler.END

async def cancel_calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Kalkulator ditutup.")
    return ConversationHandler.END

calculator_handler_obj = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(start_calculator, pattern="^calc_start$"),
        CommandHandler("calculator", start_calculator)
    ],
    states={
        CALC_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, calculate_roi)],
    },
    fallbacks=[CommandHandler("cancel", cancel_calc)]
)
