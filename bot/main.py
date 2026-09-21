import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from bot.config import TELEGRAM_BOT_TOKEN
from bot.handlers.start import start, login_command, login_handler, help_command
from bot.handlers.services import services_command, category_callback
from bot.handlers.orders import order_command, myorders_command, status_command, cancel_command
from bot.handlers.balance import balance_command, topup_command, topup_confirm_command
from bot.handlers.fund import (
    fund_command,
    fund_amount_callback,
    custom_amount_handler,
    provider_callback,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        return

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("login", login_command))
    app.add_handler(CommandHandler("balance", balance_command))
    app.add_handler(CommandHandler("fund", fund_command))
    app.add_handler(CommandHandler("services", services_command))
    app.add_handler(CommandHandler("order", order_command))
    app.add_handler(CommandHandler("myorders", myorders_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("cancel", cancel_command))
    app.add_handler(CommandHandler("topup", topup_command))
    app.add_handler(CommandHandler("topupconfirm", topup_confirm_command))

    app.add_handler(CallbackQueryHandler(fund_amount_callback, pattern=r"^fund_"))
    app.add_handler(CallbackQueryHandler(provider_callback, pattern=r"^pay_provider_"))
    app.add_handler(CallbackQueryHandler(category_callback, pattern=r"^cat_"))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, login_handler))

    logger.info("@justgrowmeBot started")
    app.run_polling()


if __name__ == "__main__":
    main()
