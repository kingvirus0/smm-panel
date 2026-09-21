from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.api_client import login, get_me


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Login", callback_data="login")],
        [InlineKeyboardButton("Help", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome to @justgrowmeBot!\n\n"
        "Your SMM Panel assistant.\n"
        "Use /login to connect your panel account.\n"
        "Use /help to see all commands.",
        reply_markup=reply_markup,
    )


async def login_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Please enter your credentials in this format:\n"
        "/login email@example.com your_password"
    )


async def login_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parts = update.message.text.split(maxsplit=2)
    if len(parts) < 3:
        await update.message.reply_text("Usage: /login email password")
        return

    email = parts[1]
    password = parts[2]

    try:
        result = await login(email, password)
        context.user_data["token"] = result["access_token"]
        context.user_data["refresh_token"] = result["refresh_token"]

        user = await get_me(result["access_token"])
        context.user_data["user"] = user

        await update.message.reply_text(
            f"Logged in as {user['username']}\n"
            f"Balance: ${user['balance']}\n"
            f"Role: {user['role']}"
        )
    except Exception as e:
        await update.message.reply_text(f"Login failed: {str(e)}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "@justgrowmeBot Commands:\n\n"
        "/start - Start the bot\n"
        "/login email password - Login to your account\n"
        "/balance - Check your balance\n"
        "/services - Browse services\n"
        "/order - Place an order\n"
        "/myorders - View your orders\n"
        "/topup - Top up your balance\n"
        "/help - Show this message"
    )
