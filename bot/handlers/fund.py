import httpx
from decimal import Decimal
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.config import BACKEND_API_URL


AMOUNTS = [500, 1000, 2000, 5000, 10000]


async def fund_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = context.user_data.get("token")
    if not token:
        await update.message.reply_text("Please /login first")
        return

    buttons = [[InlineKeyboardButton(f"₦{a:,}", callback_data=f"fund_{a}")] for a in AMOUNTS]
    buttons.append([InlineKeyboardButton("Custom Amount", callback_data="fund_custom")])
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(
        "Choose amount to add to your wallet:",
        reply_markup=reply_markup,
    )


async def fund_amount_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data == "fund_custom":
        context.user_data["awaiting_custom_amount"] = True
        await query.edit_message_text("Enter the amount in NGN (e.g. 3500):")
        return

    amount = int(data.replace("fund_", ""))
    context.user_data["fund_amount"] = amount

    buttons = [
        [InlineKeyboardButton("Paystack (Card/Bank)", callback_data="pay_provider_paystack")],
        [InlineKeyboardButton("Flutterwave (Card/Mobile)", callback_data="pay_provider_flutterwave")],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(
        f"Amount: *₦{amount:,}*\n\nChoose payment method:",
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )


async def custom_amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_custom_amount"):
        return

    try:
        amount = int(update.message.text.replace(",", "").replace("₦", "").strip())
        if amount < 100:
            await update.message.reply_text("Minimum amount is ₦100")
            return
    except ValueError:
        await update.message.reply_text("Please enter a valid number")
        return

    context.user_data["awaiting_custom_amount"] = False
    context.user_data["fund_amount"] = amount

    buttons = [
        [InlineKeyboardButton("Paystack (Card/Bank)", callback_data="pay_provider_paystack")],
        [InlineKeyboardButton("Flutterwave (Card/Mobile)", callback_data="pay_provider_flutterwave")],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(
        f"Amount: *₦{amount:,}*\n\nChoose payment method:",
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )


async def provider_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    token = context.user_data.get("token")
    amount = context.user_data.get("fund_amount")
    user = context.user_data.get("user")

    if not token or not amount or not user:
        await query.edit_message_text("Session expired. Please /fund again")
        return

    provider = query.data.replace("pay_provider_", "")

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            if provider == "paystack":
                response = await client.post(
                    f"{BACKEND_API_URL}/api/v1/payments/paystack/initialize",
                    headers={"Authorization": f"Bearer {token}"},
                    params={"amount_naira": amount},
                )
                data = response.json()
                if response.status_code != 200:
                    raise Exception(data.get("detail", "Failed"))
                pay_url = data["authorization_url"]
                btn_text = f"Pay ₦{amount:,} via Paystack"
            else:
                response = await client.post(
                    f"{BACKEND_API_URL}/api/v1/payments/flutterwave/initialize",
                    headers={"Authorization": f"Bearer {token}"},
                    json={
                        "amount_naira": amount,
                        "email": user.get("email", ""),
                        "name": user.get("username", ""),
                    },
                )
                data = response.json()
                if response.status_code != 200:
                    raise Exception(data.get("detail", "Failed"))
                pay_url = data["payment_link"]
                btn_text = f"Pay ₦{amount:,} via Flutterwave"

        buttons = [[InlineKeyboardButton(btn_text, url=pay_url)]]
        buttons.append([InlineKeyboardButton("Check Status", callback_data="check_payment")])
        reply_markup = InlineKeyboardMarkup(buttons)

        await query.edit_message_text(
            f"*₦{amount:,}* ready for payment.\n\n"
            "Click the button below to complete payment.\n"
            "After payment, your wallet will be credited automatically.",
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )

    except Exception as e:
        await query.edit_message_text(f"Error: {str(e)}\nPlease try again with /fund")
