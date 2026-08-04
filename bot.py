from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)
from config import BOT_TOKEN, ADMIN_ID, UPI_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("💳 Buy Now", callback_data="buy")]]
    await update.message.reply_text(
        "👋 Welcome!\nClick below to purchase.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "buy":
        await query.message.reply_text(
            f"💰 Pay to this UPI ID:\n\n{UPI_ID}\n\n"
            "Payment ke baad apna UTR bhejo."
        )

async def receive_utr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    utr = update.message.text

    await context.bot.send_message(
        ADMIN_ID,
        f"🆕 Payment Request\n\n"
        f"User: @{update.effective_user.username}\n"
        f"ID: {update.effective_user.id}\n"
        f"UTR: {utr}"
    )

    await update.message.reply_text(
        "✅ UTR receive ho gaya.\n"
        "Admin verification ke baad access mil jayega."
    )

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_utr))

app.run_polling()
