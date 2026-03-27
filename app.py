from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from functools import wraps
from typing import Dict, List, Optional

from flask import Flask, abort, redirect, render_template, request, session, url_for


app = Flask(__name__)
app.secret_key = "tyana-jewels-demo-secret"
DATABASE_PATH = os.path.join(app.root_path, "tyana_jewels.db")
ADMIN_USERNAME = os.environ.get("TYANA_ADMIN_USERNAME", "owner")
ADMIN_PASSWORD = os.environ.get("TYANA_ADMIN_PASSWORD", "tyana123")


@dataclass(frozen=True)
class Product:
    slug: str
    name: str
    category: str
    price: int
    sale_price: int
    finish: str
    is_best_seller: bool
    is_new_arrival: bool
    rating: float
    reviews: int
    stock: str
    short_description: str
    details: str
    material: str
    care: str
    shipping: str
    image: str
    badges: List[str]
    variants: Dict[str, List[str]]


PRODUCTS: List[Product] = [
    Product(
        slug="starlit-hoops",
        name="Starlit Hoops",
        category="Earrings",
        price=1199,
        sale_price=899,
        finish="Gold",
        is_best_seller=True,
        is_new_arrival=False,
        rating=4.8,
        reviews=126,
        stock="In stock",
        short_description="Lightweight anti-tarnish hoops that give your everyday fits a polished glow.",
        details="A sleek oval silhouette designed for all-day wear, from college looks to dinner plans.",
        material="18K gold-plated stainless steel with anti-tarnish finish.",
        care="Store dry and wipe gently after use. Avoid perfume contact for longer shine.",
        shipping="Ships in 24 hours. Free delivery on prepaid orders above Rs. 1499.",
        image="images/products/starlit-hoops.svg",
        badges=["Best Seller", "Anti-Tarnish"],
        variants={"Finish": ["Gold", "Rose Gold"]},
    ),
    Product(
        slug="moonflow-chain",
        name="Moonflow Chain",
        category="Necklaces",
        price=1499,
        sale_price=1199,
        finish="Gold",
        is_best_seller=True,
        is_new_arrival=True,
        rating=4.9,
        reviews=89,
        stock="Low stock",
        short_description="A smooth layering chain with an elevated luxe finish and zero-fuss styling.",
        details="Perfect solo or stacked, with a fluid profile that catches light beautifully.",
        material="Water-resistant stainless steel base with premium anti-tarnish coating.",
        care="Keep away from harsh chemicals. Clean with a soft microfiber cloth.",
        shipping="Express metro shipping available. COD supported on select pin codes.",
        image="images/products/moonflow-chain.svg",
        badges=["New", "Layering Favorite"],
        variants={"Length": ["16 in", "18 in"], "Finish": ["Gold"]},
    ),
    Product(
        slug="aura-stack-rings",
        name="Aura Stack Rings",
        category="Rings",
        price=999,
        sale_price=749,
        finish="Gold",
        is_best_seller=False,
        is_new_arrival=True,
        rating=4.7,
        reviews=63,
        stock="In stock",
        short_description="Three modern stackable rings made to mix, match, and repeat all week.",
        details="Minimal yet statement-making, this set creates an effortless curated-hand look.",
        material="Hypoallergenic anti-tarnish stainless steel.",
        care="Avoid abrasive surfaces. Keep separately to prevent scratches.",
        shipping="Standard shipping in 3-5 business days across India.",
        image="images/products/aura-stack-rings.svg",
        badges=["New Arrival", "Budget Pick"],
        variants={"Size": ["6", "7", "8"]},
    ),
    Product(
        slug="celeste-cuff",
        name="Celeste Cuff",
        category="Bracelets",
        price=1399,
        sale_price=1099,
        finish="Gold",
        is_best_seller=True,
        is_new_arrival=False,
        rating=4.8,
        reviews=51,
        stock="In stock",
        short_description="A clean open cuff that adds instant structure and shine to every look.",
        details="Modern, easy to style, and designed to feel premium without the heavy price tag.",
        material="Gold-tone stainless steel with anti-tarnish protection.",
        care="Remove before swimming and wipe clean after wear.",
        shipping="Packed in gift-ready premium pouches. Dispatch within 24 hours.",
        image="images/products/celeste-cuff.svg",
        badges=["Best Seller", "Giftable"],
        variants={"Finish": ["Gold", "Silver"]},
    ),
    Product(
        slug="nova-drops",
        name="Nova Drops",
        category="Earrings",
        price=1299,
        sale_price=999,
        finish="Rose Gold",
        is_best_seller=False,
        is_new_arrival=True,
        rating=4.6,
        reviews=37,
        stock="In stock",
        short_description="Glossy drop earrings with a soft statement curve for brunch-to-party styling.",
        details="A polished shape that feels trend-forward yet wearable enough for every week.",
        material="Rose gold-tone anti-tarnish stainless steel.",
        care="Use a soft pouch and avoid rubbing against metal surfaces.",
        shipping="Free shipping on prepaid orders above Rs. 1499.",
        image="images/products/nova-drops.svg",
        badges=["Trending", "Anti-Tarnish"],
        variants={"Finish": ["Rose Gold", "Gold"]},
    ),
    Product(
        slug="glowlink-pendant",
        name="Glowlink Pendant",
        category="Necklaces",
        price=1599,
        sale_price=1299,
        finish="Gold",
        is_best_seller=False,
        is_new_arrival=False,
        rating=4.8,
        reviews=74,
        stock="In stock",
        short_description="A sparkle-led pendant necklace with a refined center detail and easy everyday charm.",
        details="Designed to work with basics, occasion fits, and all your layered necklace moods.",
        material="Premium plated stainless steel with zircon detail.",
        care="Avoid direct contact with perfumes and lotions for better longevity.",
        shipping="Ships PAN India with tracking updates on SMS and email.",
        image="images/products/glowlink-pendant.svg",
        badges=["Party Edit", "Customer Favorite"],
        variants={"Length": ["16 in", "18 in", "20 in"]},
    ),
]

PRODUCT_MAP = {product.slug: product for product in PRODUCTS}
CATEGORIES = ["All", "Rings", "Earrings", "Necklaces", "Bracelets"]
FINISHES = ["All", "Gold", "Rose Gold", "Silver"]
POLICY_PAGES = {
    "shipping": {
        "title": "Shipping Policy",
        "intro": "Fast, reliable, and transparent delivery helps Tyana Jewels feel premium from first click to unboxing.",
        "points": [
            "Orders dispatch within 24 to 48 hours unless a product is marked as delayed.",
            "Prepaid orders above Rs. 1499 ship free across India.",
            "Tracking updates are sent by email and SMS after dispatch.",
        ],
    },
    "returns": {
        "title": "Returns & Exchanges",
        "intro": "We keep returns simple while protecting hygiene and product quality.",
        "points": [
            "Damaged or incorrect items can be reported within 48 hours of delivery.",
            "Eligible items may be exchanged for size or finish based on stock availability.",
            "Sale items and earrings are final sale unless they arrive damaged.",
        ],
    },
    "care": {
        "title": "Jewellery Care",
        "intro": "Our anti-tarnish finishes are made for repeat wear, but a little care keeps every piece glowing longer.",
        "points": [
            "Store each piece separately in a dry pouch or box.",
            "Avoid direct contact with perfumes, sanitizers, and harsh chemicals.",
            "Wipe gently with a soft cloth after use to maintain shine.",
        ],
    },
    "faq": {
        "title": "Frequently Asked Questions",
        "intro": "Quick answers to common shopping questions for first-time and repeat customers.",
        "points": [
            "Most products are anti-tarnish and designed for everyday wear.",
            "Cash on delivery is available for select pin codes and order values.",
            "If a product goes out of stock, join the waitlist through our contact page or Instagram.",
        ],
    },
    "privacy": {
        "title": "Privacy Policy",
        "intro": "Tyana Jewels uses customer data only to support ordering, delivery, and communication.",
        "points": [
            "We collect only the details needed to process orders and support customers.",
            "Payment information is handled securely by trusted checkout providers.",
            "Marketing emails are optional and can be unsubscribed from any time.",
        ],
    },
    "terms": {
        "title": "Terms & Conditions",
        "intro": "Clear policies help both our customers and our team have a smooth shopping experience.",
        "points": [
            "Product colors may vary slightly depending on lighting and screen settings.",
            "Pricing, offers, and stock status can change without prior notice.",
            "Misuse of promotions or fraudulent orders may be canceled.",
        ],
    },
}


def get_logo_path() -> Optional[str]:
    static_root = app.static_folder or ""
    relative_path = "images/Tyana Logo.png"
    absolute_path = os.path.join(static_root, *relative_path.split("/"))
    if os.path.exists(absolute_path):
        return relative_path
    return None


def get_db_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    connection = get_db_connection()
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            city TEXT NOT NULL,
            pin_code TEXT NOT NULL,
            payment_method TEXT NOT NULL,
            subtotal INTEGER NOT NULL,
            shipping_cost INTEGER NOT NULL,
            total INTEGER NOT NULL,
            items_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    connection.commit()
    connection.close()


def create_order(payload: Dict[str, object]) -> int:
    connection = get_db_connection()
    cursor = connection.execute(
        """
        INSERT INTO orders (
            customer_name,
            email,
            phone,
            address,
            city,
            pin_code,
            payment_method,
            subtotal,
            shipping_cost,
            total,
            items_json,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            payload["customer_name"],
            payload["email"],
            payload["phone"],
            payload["address"],
            payload["city"],
            payload["pin_code"],
            payload["payment_method"],
            payload["subtotal"],
            payload["shipping_cost"],
            payload["total"],
            json.dumps(payload["items"]),
            payload["created_at"],
        ),
    )
    connection.commit()
    order_id = int(cursor.lastrowid)
    connection.close()
    return order_id


def fetch_orders() -> List[sqlite3.Row]:
    connection = get_db_connection()
    orders = connection.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    connection.close()
    return orders


def fetch_order(order_id: int) -> Optional[sqlite3.Row]:
    connection = get_db_connection()
    order = connection.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    connection.close()
    return order


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login", next=request.path))
        return view(*args, **kwargs)

    return wrapped_view


def money(value: int) -> str:
    return f"Rs. {value:,}"


def get_cart_items() -> List[Dict[str, object]]:
    cart = session.get("cart", {})
    items: List[Dict[str, object]] = []
    for slug, quantity in cart.items():
        product = PRODUCT_MAP.get(slug)
        if not product:
            continue
        items.append(
            {
                "product": product,
                "quantity": quantity,
                "line_total": product.sale_price * quantity,
            }
        )
    return items


def cart_count() -> int:
    return sum(item["quantity"] for item in get_cart_items())


def cart_subtotal() -> int:
    return sum(int(item["line_total"]) for item in get_cart_items())


@app.context_processor
def inject_globals():
    subtotal = cart_subtotal()
    shipping_cost = 0 if subtotal >= 1499 or subtotal == 0 else 99
    return {
        "brand_name": "Tyana Jewels",
        "tagline": "Where Grace Meets Glow",
        "categories": CATEGORIES,
        "logo_path": get_logo_path(),
        "cart_count": cart_count(),
        "cart_subtotal_value": subtotal,
        "cart_shipping_value": shipping_cost,
        "is_admin": bool(session.get("is_admin")),
        "money": money,
    }


@app.route("/", methods=["GET"])
def home():
    best_sellers = [p for p in PRODUCTS if p.is_best_seller][:4]
    new_arrivals = [p for p in PRODUCTS if p.is_new_arrival][:4]
    reviews = [
        {
            "name": "Aarohi",
            "quote": "The finish looks way more expensive than the price. I wear my hoops almost every day.",
            "handle": "@aarohi.styles",
        },
        {
            "name": "Sana",
            "quote": "Packaging was super cute and the bracelet still looks fresh after weeks of wear.",
            "handle": "@sanaedits",
        },
        {
            "name": "Mitali",
            "quote": "Perfect for gifting. The pendant looked elegant, modern, and not overdone.",
            "handle": "@mitalimood",
        },
    ]
    return render_template(
        "home.html",
        best_sellers=best_sellers,
        new_arrivals=new_arrivals,
        reviews=reviews,
    )


@app.route("/shop", methods=["GET"])
def shop():
    selected_category = request.args.get("category", "All")
    selected_finish = request.args.get("finish", "All")
    selected_badge = request.args.get("badge", "All")

    filtered = PRODUCTS
    if selected_category != "All":
        filtered = [p for p in filtered if p.category == selected_category]
    if selected_finish != "All":
        filtered = [p for p in filtered if p.finish == selected_finish]
    if selected_badge == "Best Sellers":
        filtered = [p for p in filtered if p.is_best_seller]
    elif selected_badge == "New Arrivals":
        filtered = [p for p in filtered if p.is_new_arrival]

    return render_template(
        "shop.html",
        products=filtered,
        finishes=FINISHES,
        selected_category=selected_category,
        selected_finish=selected_finish,
        selected_badge=selected_badge,
    )


@app.route("/product/<slug>", methods=["GET"])
def product_detail(slug: str):
    product = PRODUCT_MAP.get(slug)
    if not product:
        abort(404)
    related = [p for p in PRODUCTS if p.category == product.category and p.slug != product.slug][:3]
    return render_template("product.html", product=product, related=related)


@app.route("/cart/add/<slug>", methods=["POST"])
def add_to_cart(slug: str):
    product = PRODUCT_MAP.get(slug)
    if not product:
        abort(404)
    cart = session.get("cart", {})
    cart[slug] = cart.get(slug, 0) + 1
    session["cart"] = cart
    return redirect(request.referrer or url_for("cart"))


@app.route("/buy-now/<slug>", methods=["POST"])
def buy_now(slug: str):
    product = PRODUCT_MAP.get(slug)
    if not product:
        abort(404)
    session["cart"] = {slug: 1}
    return redirect(url_for("checkout"))


@app.route("/cart/update/<slug>", methods=["POST"])
def update_cart(slug: str):
    product = PRODUCT_MAP.get(slug)
    if not product:
        abort(404)
    quantity = int(request.form.get("quantity", 1))
    cart = session.get("cart", {})
    if quantity <= 0:
        cart.pop(slug, None)
    else:
        cart[slug] = quantity
    session["cart"] = cart
    return redirect(url_for("cart"))


@app.route("/cart", methods=["GET"])
def cart():
    items = get_cart_items()
    subtotal = cart_subtotal()
    shipping_cost = 0 if subtotal >= 1499 or subtotal == 0 else 99
    return render_template(
        "cart.html",
        items=items,
        shipping_cost=shipping_cost,
        total=subtotal + shipping_cost,
    )


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    items = get_cart_items()
    if not items:
        return redirect(url_for("shop"))
    subtotal = cart_subtotal()
    shipping_cost = 0 if subtotal >= 1499 else 99
    total = subtotal + shipping_cost

    if request.method == "POST":
        line_items = [
            {
                "slug": item["product"].slug,
                "name": item["product"].name,
                "price": item["product"].sale_price,
                "quantity": item["quantity"],
                "line_total": item["line_total"],
            }
            for item in items
        ]
        order_id = create_order(
            {
                "customer_name": request.form.get("name", "Customer"),
                "email": request.form.get("email", ""),
                "phone": request.form.get("phone", ""),
                "address": request.form.get("address", ""),
                "city": request.form.get("city", ""),
                "pin_code": request.form.get("pin", ""),
                "payment_method": request.form.get("payment_method", "UPI"),
                "subtotal": subtotal,
                "shipping_cost": shipping_cost,
                "total": total,
                "items": line_items,
                "created_at": datetime.now().strftime("%d %b %Y, %I:%M %p"),
            }
        )
        order = {
            "id": order_id,
            "name": request.form.get("name", "Customer"),
            "city": request.form.get("city", ""),
            "payment_method": request.form.get("payment_method", "UPI"),
            "total": total,
        }
        session["last_order"] = order
        session["cart"] = {}
        return redirect(url_for("order_success"))

    return render_template(
        "checkout.html",
        items=items,
        subtotal=subtotal,
        shipping_cost=shipping_cost,
        total=total,
    )


@app.route("/order-success", methods=["GET"])
def order_success():
    order = session.get("last_order")
    if not order:
        return redirect(url_for("home"))
    return render_template("order_success.html", order=order)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("is_admin"):
        return redirect(url_for("admin_dashboard"))

    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["is_admin"] = True
            return redirect(request.args.get("next") or url_for("admin_dashboard"))
        error = "Incorrect username or password."

    return render_template("admin_login.html", error=error)


@app.route("/admin/logout", methods=["POST"])
@admin_required
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("admin_login"))


@app.route("/admin/dashboard", methods=["GET"])
@admin_required
def admin_dashboard():
    orders = fetch_orders()
    total_orders = len(orders)
    total_revenue = sum(int(order["total"]) for order in orders)
    total_customers = len({order["email"] for order in orders})
    latest_orders = orders[:5]
    return render_template(
        "admin_dashboard.html",
        orders=latest_orders,
        total_orders=total_orders,
        total_revenue=total_revenue,
        total_customers=total_customers,
        total_products=len(PRODUCTS),
    )


@app.route("/admin/orders", methods=["GET"])
@admin_required
def admin_orders():
    orders = fetch_orders()
    return render_template("admin_orders.html", orders=orders)


@app.route("/admin/orders/<int:order_id>", methods=["GET"])
@admin_required
def admin_order_detail(order_id: int):
    order = fetch_order(order_id)
    if not order:
        abort(404)
    items = json.loads(order["items_json"])
    return render_template("admin_order_detail.html", order=order, items=items)


@app.route("/admin/products", methods=["GET"])
@admin_required
def admin_products():
    return render_template("admin_products.html", products=PRODUCTS)


@app.route("/admin/customers", methods=["GET"])
@admin_required
def admin_customers():
    orders = fetch_orders()
    customers: Dict[str, Dict[str, object]] = {}
    for order in orders:
        email = order["email"]
        if email not in customers:
            customers[email] = {
                "name": order["customer_name"],
                "email": email,
                "phone": order["phone"],
                "city": order["city"],
                "orders": 0,
                "spent": 0,
            }
        customers[email]["orders"] += 1
        customers[email]["spent"] += int(order["total"])
    customer_list = sorted(customers.values(), key=lambda row: row["spent"], reverse=True)
    return render_template("admin_customers.html", customers=customer_list)


@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET"])
def contact():
    return render_template("contact.html")


@app.route("/policies/<slug>", methods=["GET"])
def policy_page(slug: str):
    page = POLICY_PAGES.get(slug)
    if not page:
        abort(404)
    return render_template("policy.html", page=page)


init_db()


if __name__ == "__main__":
    app.run(debug=True)
