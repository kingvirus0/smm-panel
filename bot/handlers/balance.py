from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.api_client import get_me, topup, APIError


async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = context.user_data.get("token")
    if not token:
        await update.message.reply_text("Please /login first")
        return

    try:
        user = await get_me(token)
        context.user_data["user"] = user
        await update.message.reply_text(
            f"Balance: ${user['balance']}\n"
            f"Referral Earnings: ${user['affiliate_earnings']}"
        )
    except APIError as e:
        await update.message.reply_text(f"Error: {e}")


async def topup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = context.user_data.get("token")
    if not token:
        await update.message.reply_text("Please /login first")
        return

    keyboard = [
        [InlineKeyboardButton("USDT (TRC20)", callback_data="topup_crypto_usdt")],
        [InlineKeyboardButton("Bitcoin", callback_data="topup_crypto_btc")],
        [InlineKeyboardButton("Bank Transfer", callback_data="topup_manual_bank")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Select payment method:\n\n"
        "After sending payment, use:\n"
        "/topupconfirm amount method tx_reference\n"
        "Example: /topupconfirm 50 crypto_usdt ABC123XYZ",
        reply_markup=reply_markup,
    )


async def topup_confirm_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = context.user_data.get("token")
    if not token:
        await update.message.reply_text("Please /login first")
        return

    parts = update.message.text.split()
    if len(parts) < 3:
        await update.message.reply_text(
            "Usage: /topupconfirm amount method tx_reference\n"
            "Methods: crypto_usdt, crypto_btc, manual_bank, manual_other"
        )
        return

    try:
        amount = float(parts[1])
        method = parts[2]
        tx_ref = parts[3] if len(parts) > 3 else None

        result = await topup(token, amount, method, tx_ref)
        await update.message.reply_text(
            f"Top-up request submitted!\n"
            f"Amount: ${amount}\n"
            f"Method: {method}\n"
            f"Status: Pending approval"
        )
    except APIError as e:
        await update.message.reply_text(f"Error: {e}")
    except ValueError:
        await update.message.reply_text("Invalid amount")
