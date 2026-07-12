from flask import Flask, render_template

from database import (
    products_collection,
    price_history_collection,
)

app = Flask(__name__)


@app.route("/")
def home():
    products = list(
        products_collection.find().sort(
            "created_at",
            -1,
        )
    )

    dashboard_products = []

    for product in products:
        history_records = list(
            price_history_collection.find(
                {
                    "product_id": product["_id"]
                }
            ).sort(
                "checked_at",
                1,
            )
        )

        history_labels = []
        history_prices = []

        for record in history_records:
            checked_at = record.get("checked_at")

            if checked_at:
                history_labels.append(
                    checked_at.strftime(
                        "%d %b %Y, %I:%M %p"
                    )
                )
            else:
                history_labels.append(
                    "Unknown time"
                )

            history_prices.append(
                record.get("price", 0)
            )

        dashboard_products.append({
            "id": str(product["_id"]),
            "title": product.get(
                "title",
                "Unknown Product",
            ),
            "url": product.get(
                "url",
                "#",
            ),
            "site": product.get(
                "site",
                "Unknown",
            ),
            "current_price": product.get(
                "current_price",
                0,
            ),
            "target_price": product.get(
                "target_price",
                0,
            ),
            "active": product.get(
                "active",
                False,
            ),
            "history_labels": history_labels,
            "history_prices": history_prices,
        })

    return render_template(
        "index.html",
        products=dashboard_products,
    )


if __name__ == "__main__":
    app.run(
        debug=True,
    )