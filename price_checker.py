import asyncio
from datetime import datetime

from telegram import Bot

from config import BOT_TOKEN
from database import (
    products_collection,
    price_history_collection,
)
from scraper import scrape_product


async def send_price_alert(
    bot,
    product,
    latest_price,
):
    message = (
        "🔔 PRICE DROP ALERT!\n\n"
        f"📦 {product['title']}\n\n"
        f"💰 Current Price: ৳{latest_price:,}\n"
        f"🎯 Target Price: ৳{product['target_price']:,}\n\n"
        f"🔗 Buy Now:\n{product['url']}"
    )

    await bot.send_message(
        chat_id=product["chat_id"],
        text=message,
    )


async def check_prices():
    if not BOT_TOKEN:
        raise ValueError(
            "BOT_TOKEN was not found in the .env file."
        )

    bot = Bot(token=BOT_TOKEN)

    products = products_collection.find({
        "active": True
    })

    print("Checking tracked product prices...\n")

    async with bot:
        for product in products:
            try:
                latest = await asyncio.to_thread(
                    scrape_product,
                    product["url"],
                )

                old_price = product["current_price"]
                new_price = latest["price"]
                target_price = product["target_price"]

                print("-----------------------------")
                print("Product:", latest["title"])
                print("Old Price:", old_price)
                print("New Price:", new_price)
                print("Target Price:", target_price)

                price_history_collection.insert_one({
                    "product_id": product["_id"],
                    "price": new_price,
                    "checked_at": datetime.now(),
                })

                products_collection.update_one(
                    {"_id": product["_id"]},
                    {
                        "$set": {
                            "title": latest["title"],
                            "current_price": new_price,
                            "updated_at": datetime.now(),
                        }
                    },
                )

                if new_price <= target_price:
                    await send_price_alert(
                        bot,
                        product,
                        new_price,
                    )

                    print("Telegram alert sent!")
                else:
                    print("No price drop.")

            except Exception as error:
                print(
                    f"Error checking product "
                    f"{product.get('title', 'Unknown')}: "
                    f"{error}"
                )


if __name__ == "__main__":
    asyncio.run(check_prices())