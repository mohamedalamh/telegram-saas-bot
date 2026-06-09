from telegram import Update
from telegram.ext import ContextTypes
from keyboards import main_menu

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Ø£Ù‡Ù„Ø§Ù‹ Ø¨Ùƒ ÙÙŠ Ø§Ù„Ù†Ø¸Ø§Ù…",
        reply_markup=main_menu()
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.data == "add_token":
        await query.message.reply_text(
            "Ø£Ø±Ø³Ù„ ØªÙˆÙƒÙ† Ø§Ù„Ø¨ÙˆØª"
        )

    elif query.data == "start_bot":
        await query.message.reply_text(
            "Ø³ÙŠØªÙ… ØªØ´ØºÙŠÙ„ Ø§Ù„Ø¨ÙˆØª"
        )

    elif query.data == "stop_bot":
        await query.message.reply_text(
            "Ø³ÙŠØªÙ… Ø¥ÙŠÙ‚Ø§Ù Ø§Ù„Ø¨ÙˆØª"
        )

    elif query.data == "settings":
        await query.message.reply_text(
            "Ø§Ù„Ø¥Ø¹Ø¯Ø§Ø¯Ø§Øª"
        )

    elif query.data == "subscription":
        await query.message.reply_text(
            "Ù…Ø¹Ù„ÙˆÙ…Ø§Øª Ø§Ù„Ø§Ø´ØªØ±Ø§Ùƒ"
        )
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    await update.message.reply_text(
        f"Ø§Ø³ØªÙ„Ù…Øª:\n{text}"
    )
