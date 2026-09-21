from telegram import Update
from telegram.ext import ContextTypes
from bot.api_client import create_order, get_my_orders, cancel_order, get_order, APIError


async def order_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = context.user_data.get("token")
    if not token:
        await update.message.reply_text("Please /login first")
        return

    parts = update.message.text.split()
    if len(parts) < 4:
        await update.message.reply_text(
            "Usage: /order service_id URL quantity\n"
            "Example: /order 12345 https://instagram.com/p/abc 1000"
        )
        return

    service_id = parts[1]
    target_url = parts[2]
    try:
        quantity = int(parts[3])
    except ValueError:
        await update.message.reply_text("Quantity must be a number")
        return

    try:
        result = await create_order(token, service_id, target_url, quantity)
        await update.message.reply_text(
            f"Order placed!\n"
            f"ID: {result['id'][:8]}\n"
            f"Status: {result['status']}\n"
            f"Charge: ${result['charge']}"
        )
    except APIError as e:
        await update.message.reply_text(f"Order failed: {e}")


async def myorders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = context.user_data.get("token")
    if not token:
        await update.message.reply_text("Please /login first")
        return

    try:
        orders = await get_my_orders(token)
        if not orders:
            await update.message.reply_text("No orders yet")
            return

        text = "Your Orders:\n\n"
        for o in orders[:10]:
            status_emoji = {
                "completed": "completed",
                "in_progress": "in progress",
                "pending": "pending",
                "error": "error",
            }.get(o["status"], o["status"])
            text += f"ID: {o['id'][:8]} | {status_emoji} | {o['quantity']} qty | ${o['charge']}\n"

        await update.message.reply_text(text)
    except APIError as e:
        await update.message.reply_text(f"Error: {e}")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = context.user_data.get("token")
    if not token:
        await update.message.reply_text("Please /login first")
        return

    parts = update.message.text.split()
    if len(parts) < 2:
        await update.message.reply_text("Usage: /status order_id")
        return

    try:
        order = await get_order(token, parts[1])
        await update.message.reply_text(
            f"Order: {order['id'][:8]}\n"
            f"Status: {order['status']}\n"
            f"Progress: {order['current_count']}/{order['quantity']}\n"
            f"Charge: ${order['charge']}\n"
            f"URL: {order['target_url']}"
        )
    except APIError as e:
        await update.message.reply_text(f"Error: {e}")


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = context.user_data.get("token")
    if not token:
        await update.message.reply_text("Please /login first")
        return

    parts = update.message.text.split()
    if len(parts) < 2:
        await update.message.reply_text("Usage: /cancel order_id")
        return

    try:
        result = await cancel_order(token, parts[1])
        await update.message.reply_text(f"Order {result['id'][:8]} cancelled. Refunded ${result['charge']}")
    except APIError as e:
        await update.message.reply_text(f"Error: {e}")
