from telegram.ext import ApplicationBuilder
from bot.config import TELEGRAM_BOT_TOKEN

bot = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build().bot
