from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.api_client import get_categories, get_services, APIError


async def services_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = context.user_data.get("token")
    if not token:
        await update.message.reply_text("Please /login first")
        return

    try:
        categories = await get_categories(token)
        if not categories:
            await update.message.reply_text("No categories available")
            return

        buttons = [[InlineKeyboardButton(cat["name"], callback_data=f"cat_{cat['id']}")] for cat in categories[:20]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text("Select a category:", reply_markup=reply_markup)
    except APIError as e:
        await update.message.reply_text(f"Error: {e}")


async def category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    token = context.user_data.get("token")
    if not token:
        await query.edit_message_text("Please /login first")
        return

    category_id = query.data.replace("cat_", "")

    try:
        services = await get_services(token, category_id)
        if not services:
            await query.edit_message_text("No services in this category")
            return

        text = "Services:\n\n"
        for s in services[:10]:
            text += f"ID: {s['provider_service_id']}\n"
            text += f"Name: {s['name'][:60]}\n"
            text += f"Price: ${s['price_per_1000']}/1K | Min: {s['min_quantity']} | Max: {s['max_quantity']}\n\n"

        text += "\nTo order: /order service_id URL quantity"
        await query.edit_message_text(text)
    except APIError as e:
        await query.edit_message_text(f"Error: {e}")
