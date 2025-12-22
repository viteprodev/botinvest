from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler

INFO_TEXTS = {
    "faq": (
        "❓ **FAQ (Frequently Asked Questions)**\n\n"
        "**Q: Bagaimana cara Topup?**\n"
        "A: Klik menu Topup, pilih nominal, transfer sesuai instruksi, dan upload bukti.\n\n"
        "**Q: Berapa lama proses withdraw?**\n"
        "A: Maksimal 1x24 jam kerja.\n\n"
        "**Q: Apakah aman?**\n"
        "A: Ya, kami diawasi oleh lembaga terkait."
    ),
    "rules": (
        "📜 **Peraturan**\n\n"
        "1. Dilarang melakukan spam.\n"
        "2. Bukti transfer harus asli.\n"
        "3. Segala bentuk kecurangan akan menyebabkan akun dibanned permanen."
    ),
    "legal": (
        "⚖️ **Lembaga Hukum**\n\n"
        "Bot Investasi ini beroperasi di bawah naungan PT Investasi Sejahtera.\n"
        "Terdaftar dan diawasi oleh:\n"
        "- Kementerian Keuangan\n"
        "- Bank Indonesia\n"
        "- Otoritas Jasa Keuangan (OJK)"
    ),
    "privacy": (
        "🔒 **Kebijakan Privasi**\n\n"
        "Data diri Anda aman bersama kami. Kami tidak membagikan data kepada pihak ketiga tanpa persetujuan Anda."
    )
}

async def info_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("❓ FAQ", callback_data="info_faq"), InlineKeyboardButton("📜 Peraturan", callback_data="info_rules")],
        [InlineKeyboardButton("⚖️ Lembaga Hukum", callback_data="info_legal"), InlineKeyboardButton("🔒 Privasi", callback_data="info_privacy")],
        [InlineKeyboardButton("🔙 Kembali ke Menu", callback_data="back_to_menu")]
    ]
    
    await query.edit_message_text(
        "ℹ️ **Pusat Informasi**\n\nSilakan pilih topik informasi yang ingin Anda baca:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_info_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    topic = query.data.split("_")[1] # info_faq -> faq
    text = INFO_TEXTS.get(topic, "Informasi tidak ditemukan.")
    
    keyboard = [[InlineKeyboardButton("🔙 Kembali", callback_data="info_start")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

info_handlers = [
    CallbackQueryHandler(info_menu, pattern="^info_start$"),
    CallbackQueryHandler(show_info_detail, pattern="^info_")
]
