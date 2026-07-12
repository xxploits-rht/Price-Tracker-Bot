from datetime import datetime

from pymongo import MongoClient

from config import MONGO_URI


client = MongoClient(MONGO_URI)

database = client["price_tracker"]

products_collection = database["products"]
price_history_collection = database["price_history"]


def save_product(product_data):
    existing_product = products_collection.find_one({
        "url": product_data["url"],
        "chat_id": product_data["chat_id"]
    })

    if existing_product:
        return existing_product["_id"], False

    document = {
        "title": product_data["title"],
        "url": product_data["url"],
        "site": product_data["site"],
        "current_price": product_data["price"],
        "target_price": product_data["target_price"],
        "telegram_user_id": product_data["telegram_user_id"],
        "chat_id": product_data["chat_id"],
        "active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

    result = products_collection.insert_one(document)

    price_history_collection.insert_one({
        "product_id": result.inserted_id,
        "price": product_data["price"],
        "checked_at": datetime.now()
    })

    return result.inserted_id, True