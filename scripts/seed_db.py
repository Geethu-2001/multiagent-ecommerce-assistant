"""Seed deterministic fictional data. Re-running replaces demo rows safely."""
import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy import text
from multiagent.agents.database import get_owner_engine
from init_db import main as init_schema

FIRST = ["Aarav", "Ananya", "Vihaan", "Diya", "Ishaan", "Meera", "Kabir", "Aadhya", "Reyansh", "Sara", "Arjun", "Ira", "Dev", "Nila", "Rohan", "Tara", "Advik", "Mira", "Kian", "Leela", "Neil", "Riya", "Om", "Sana", "Krish", "Avni", "Yash", "Maya", "Ayan", "Pia", "Ritvik", "Noor"]
LAST = ["Sharma", "Nair", "Iyer", "Rao", "Menon", "Patel", "Das", "Kapoor", "Gupta", "Khan", "Pillai", "Joshi", "Reddy", "Bose", "Verma"]
CATEGORIES = [("Electronics", "Devices and accessories"), ("Clothing", "Everyday apparel"), ("Home", "Home and kitchen products"), ("Books", "Fiction and learning"), ("Sports", "Fitness and outdoor products"), ("Beauty", "Personal care")]
PRODUCTS = [("Wireless Headphones", "NovaSound", 2499), ("USB-C Charger", "VoltNest", 899), ("Smart Watch", "PulseArc", 4999), ("Bluetooth Speaker", "NovaSound", 1799), ("Laptop Stand", "DeskBloom", 1299), ("Cotton T-Shirt", "ThreadRoot", 599), ("Denim Jeans", "ThreadRoot", 1599), ("Running Shoes", "StridePeak", 3299), ("Ceramic Mug", "Hearthly", 349), ("Desk Lamp", "LumaNest", 1099), ("Cookware Set", "Hearthly", 2899), ("Water Bottle", "TrailMint", 499), ("Yoga Mat", "TrailMint", 999), ("Travel Backpack", "RoamCraft", 2199), ("Notebook Set", "PaperHarbor", 299), ("Python Basics Book", "LearnLeaf", 799), ("Mystery Novel", "PageTurn", 449), ("Face Moisturizer", "PurePetal", 699), ("Sunscreen SPF 50", "PurePetal", 549), ("Desk Organizer", "DeskBloom", 649)]

def main():
    init_schema()
    rng = random.Random(20261027)
    engine = get_owner_engine()
    now = datetime.now(timezone.utc).replace(microsecond=0)
    with engine.begin() as conn:
        # Clear only known demo tables in dependency order.
        conn.execute(text("TRUNCATE shipments, payments, order_items, orders, products, users, categories RESTART IDENTITY CASCADE"))
        category_ids = {}
        for name, description in CATEGORIES:
            result = conn.execute(text("INSERT INTO categories(name,description) VALUES (:n,:d) RETURNING id"), {"n": name, "d": description})
            category_ids[name] = result.scalar_one()
        user_ids = []
        for i in range(32):
            first, last = FIRST[i], LAST[i % len(LAST)]
            tier = ["bronze", "silver", "gold", "platinum"][i % 4]
            result = conn.execute(text("INSERT INTO users(first_name,last_name,email,phone,created_at,is_active,customer_tier) VALUES (:f,:l,:e,:p,:c,:a,:t) RETURNING id"), {
                "f": first, "l": last, "e": f"{first.lower()}.{i+1}@example.test", "p": f"+91-90000-{i+1:05d}",
                "c": now - timedelta(days=20+i*11), "a": i % 13 != 0, "t": tier})
            user_ids.append(result.scalar_one())
        product_ids = []
        for i in range(45):
            pname, brand, price = PRODUCTS[i % len(PRODUCTS)]
            category = CATEGORIES[i % len(CATEGORIES)][0]
            result = conn.execute(text("""INSERT INTO products(sku,name,description,category_id,brand,unit_price,currency,stock_quantity,reorder_level,is_active,created_at)
            VALUES (:sku,:name,:desc,:cat,:brand,:price,'INR',:stock,:reorder,:active,:created) RETURNING id"""), {
                "sku": f"SKU-{i+1:04d}", "name": f"{pname} {i//len(PRODUCTS)+1}" if i >= len(PRODUCTS) else pname,
                "desc": f"Fictional {pname.lower()} from {brand}.", "cat": category_ids[category], "brand": brand,
                "price": Decimal(price + (i % 5)*75), "stock": [0,2,4,8,15,32,60][i%7], "reorder": [5,8,10][i%3],
                "active": i % 17 != 0, "created": now - timedelta(days=i*3)})
            product_ids.append(result.scalar_one())
        order_statuses = ["delivered", "shipped", "processing", "confirmed", "pending", "cancelled", "returned"]
        for i in range(60):
            uid = user_ids[i % 27]  # Keep five customers with no orders for left-join demos.
            status = order_statuses[i % len(order_statuses)]
            item_count = 1 + (i % 3)
            selected = rng.sample(product_ids[:39], item_count)  # Leave several products never ordered.
            items = []
            subtotal = Decimal("0.00")
            for pid in selected:
                row = conn.execute(text("SELECT unit_price FROM products WHERE id=:id"), {"id": pid}).first()
                unit = Decimal(str(row[0])); qty = 1 + rng.randrange(3)
                line = unit * qty
                items.append((pid, qty, unit, line))
                subtotal += line
            discount = (subtotal * Decimal("0.05")).quantize(Decimal("0.01")) if i % 9 == 0 else Decimal("0.00")
            shipping = Decimal("0.00") if subtotal > 2500 else Decimal("99.00")
            tax = ((subtotal-discount) * Decimal("0.05")).quantize(Decimal("0.01"))
            total = subtotal-discount+tax+shipping
            payment_status = "paid" if status in {"delivered","shipped","processing"} else ("failed" if i % 11 == 0 else "pending")
            order_date = now - timedelta(days=(i*3) % 210)
            order_number = f"ORD-{i+1:04d}"
            order_id = conn.execute(text("""INSERT INTO orders(order_number,user_id,order_date,status,subtotal,discount_amount,tax_amount,shipping_fee,total_amount,currency,payment_status,shipping_address)
            VALUES (:num,:uid,:date,:status,:sub,:disc,:tax,:ship,:total,'INR',:ps,:addr) RETURNING id"""), {
                "num": order_number, "uid": uid, "date": order_date, "status": status, "sub": subtotal, "disc": discount,
                "tax": tax, "ship": shipping, "total": total, "ps": payment_status, "addr": f"{100+i} Sample Road, Bengaluru, Karnataka"}).scalar_one()
            for pid, qty, unit, line in items:
                conn.execute(text("INSERT INTO order_items(order_id,product_id,quantity,unit_price,discount_amount,line_total) VALUES (:o,:p,:q,:u,0,:l)"), {"o": order_id, "p": pid, "q": qty, "u": unit, "l": line})
            pay_status = "paid" if payment_status == "paid" else ("failed" if payment_status == "failed" else "pending")
            conn.execute(text("INSERT INTO payments(order_id,payment_reference,payment_method,amount,currency,status,paid_at,created_at) VALUES (:o,:r,:m,:a,'INR',:s,:paid,:c)"), {
                "o": order_id, "r": f"PAY-DEMO-{i+1:05d}", "m": ["card","UPI","net_banking","cash_on_delivery","wallet"][i%5],
                "a": total, "s": pay_status, "paid": order_date if pay_status == "paid" else None, "c": order_date})
            if status not in {"pending", "cancelled"} and i % 8 != 0:
                ship_status = "delivered" if status == "delivered" else ("delayed" if i % 10 == 0 else "in_transit")
                shipped = order_date + timedelta(days=1)
                eta = order_date + timedelta(days=5)
                delivered = order_date + timedelta(days=4) if ship_status == "delivered" else None
                conn.execute(text("INSERT INTO shipments(order_id,carrier,tracking_number,shipping_status,shipped_at,estimated_delivery_at,delivered_at,created_at) VALUES (:o,:c,:t,:s,:sh,:eta,:d,:cr)"), {
                    "o": order_id, "c": ["BlueDart","Delhivery","India Post"][i%3], "t": f"TRACK-DEMO-{i+1:05d}", "s": ship_status,
                    "sh": shipped, "eta": eta, "d": delivered, "cr": order_date})
    print("Seed complete: 32 users, 45 products, 60 orders, order items, payments, shipments and categories.")

if __name__ == "__main__":
    main()
