from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.api_client import get_me, APIError


async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = context.user_data.get("token")
    if not token:
        await update.message.reply_text("Please /login first")
        return

    try:
        user = await get_me(token)
        context.user_data["user"] = user
        balance = float(user.get("balance", 0))
        earnings = float(user.get("affiliate_earnings", 0))

        buttons = [
            [InlineKeyboardButton("Add Funds", callback_data="fund_start")],
            [InlineKeyboardButton("Order History", callback_data="show_orders")],
        ]
        reply_markup = InlineKeyboardMarkup(buttons)

        await update.message.reply_text(
            f"*Your Wallet*\n\n"
            f"Balance: *₦{balance:,.2f}*\n"
            f"Referral Earnings: *₦{earnings:,.2f}*\n\n"
            f"Use /fund to add money to your wallet.",
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )
    except APIError as e:
        await update.message.reply_text(f"Error: {e}")


async def topup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Use /fund to add money to your wallet via Paystack or Flutterwave."
    )


async def topup_confirm_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Use /fund for instant payments via card or mobile money."
    )
