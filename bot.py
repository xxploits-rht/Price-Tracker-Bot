import asyncio

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from config import BOT_TOKEN
from database import save_product
from price_checker import check_prices
from scraper import scrape_product


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "🤖 Welcome to Price Tracker Bot!\n\n"
        "Product track করতে লিখুন:\n"
        "/track <product_url> <target_price>\n\n"
        "Example:\n"
        "/track https://www.startech.com.bd/product-link 250000"
    )


async def track(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if len(context.args) != 2:
        await update.message.reply_text(
            "❌ সঠিক format ব্যবহার করুন:\n\n"
            "/track <product_url> <target_price>"
        )
        return

    url = context.args[0]

    try:
        target_price = int(
            context.args[1].replace(",", "")
        )
    except ValueError:
        await update.message.reply_text(
            "❌ Target price অবশ্যই number হতে হবে।\n"
            "Example: 250000"
        )
        return

    await update.message.reply_text(
        "🔍 Product information checking..."
    )

    try:
        product = await asyncio.to_thread(
            scrape_product,
            url,
        )

        product["target_price"] = target_price
        product["telegram_user_id"] = update.effective_user.id
        product["chat_id"] = update.effective_chat.id

        product_id, created = save_product(product)

        if not created:
            await update.message.reply_text(
                "⚠️ এই product আপনি আগেই track করেছেন।"
            )
            return

        await update.message.reply_text(
            "✅ Product tracking started!\n\n"
            f"📦 Title:\n{product['title']}\n\n"
            f"💰 Current Price: ৳{product['price']:,}\n"
            f"🎯 Target Price: ৳{target_price:,}\n\n"
            f"🆔 Product ID:\n{product_id}"
        )

    except Exception as error:
        print("Track error:", error)

        await update.message.reply_text(
            "❌ Product information নেওয়া যায়নি।\n"
            "URL সঠিক কিনা check করুন।"
        )


async def scheduled_price_check(
    context: ContextTypes.DEFAULT_TYPE,
):
    print("Automatic price check started...")

    try:
        await check_prices()
    except Exception as error:
        print("Scheduled price check error:", error)


def main():
    if not BOT_TOKEN:
        raise ValueError(
            "BOT_TOKEN was not found in the .env file."
        )

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("track", track)
    )

    job_queue = application.job_queue

    job_queue.run_repeating(
        scheduled_price_check,
        interval=6 * 60 * 60,
        first=10,
        name="six_hour_price_checker",
    )

    print("Bot Running...")
    print("Automatic price check: every 6 hours")
    print("First automatic check: after 10 seconds")

    application.run_polling()


if __name__ == "__main__":
    main()