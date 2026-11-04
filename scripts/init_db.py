from sqlalchemy import text
from multiagent.agents.database import get_owner_engine

DDL = [
"CREATE TABLE IF NOT EXISTS categories (id SERIAL PRIMARY KEY, name VARCHAR(100) NOT NULL UNIQUE, description TEXT NOT NULL DEFAULT '', parent_category_id INTEGER REFERENCES categories(id), is_active BOOLEAN NOT NULL DEFAULT TRUE)",
"CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, first_name VARCHAR(80) NOT NULL, last_name VARCHAR(80) NOT NULL, email VARCHAR(200) NOT NULL UNIQUE, phone VARCHAR(30), date_of_birth DATE, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), is_active BOOLEAN NOT NULL DEFAULT TRUE, customer_tier VARCHAR(20) NOT NULL DEFAULT 'bronze' CHECK (customer_tier IN ('bronze','silver','gold','platinum')))",
"CREATE TABLE IF NOT EXISTS products (id SERIAL PRIMARY KEY, sku VARCHAR(40) NOT NULL UNIQUE, name VARCHAR(200) NOT NULL, description TEXT NOT NULL DEFAULT '', category_id INTEGER NOT NULL REFERENCES categories(id), brand VARCHAR(100) NOT NULL, unit_price NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0), currency CHAR(3) NOT NULL DEFAULT 'INR', stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0), reorder_level INTEGER NOT NULL DEFAULT 5 CHECK (reorder_level >= 0), is_active BOOLEAN NOT NULL DEFAULT TRUE, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW())",
"CREATE TABLE IF NOT EXISTS orders (id SERIAL PRIMARY KEY, order_number VARCHAR(30) NOT NULL UNIQUE, user_id INTEGER NOT NULL REFERENCES users(id), order_date TIMESTAMPTZ NOT NULL, status VARCHAR(20) NOT NULL CHECK (status IN ('pending','confirmed','processing','shipped','delivered','cancelled','returned')), subtotal NUMERIC(12,2) NOT NULL CHECK (subtotal >= 0), discount_amount NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (discount_amount >= 0), tax_amount NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (tax_amount >= 0), shipping_fee NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (shipping_fee >= 0), total_amount NUMERIC(12,2) NOT NULL CHECK (total_amount >= 0), currency CHAR(3) NOT NULL DEFAULT 'INR', payment_status VARCHAR(20) NOT NULL CHECK (payment_status IN ('unpaid','pending','paid','failed','refunded')), shipping_address TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW())",
"CREATE TABLE IF NOT EXISTS order_items (id SERIAL PRIMARY KEY, order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE, product_id INTEGER NOT NULL REFERENCES products(id), quantity INTEGER NOT NULL CHECK (quantity > 0), unit_price NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0), discount_amount NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (discount_amount >= 0), line_total NUMERIC(12,2) NOT NULL CHECK (line_total >= 0), created_at TIMESTAMPTZ NOT NULL DEFAULT NOW())",
"CREATE TABLE IF NOT EXISTS payments (id SERIAL PRIMARY KEY, order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE, payment_reference VARCHAR(60) NOT NULL UNIQUE, payment_method VARCHAR(30) NOT NULL CHECK (payment_method IN ('card','UPI','net_banking','cash_on_delivery','wallet')), amount NUMERIC(12,2) NOT NULL CHECK (amount >= 0), currency CHAR(3) NOT NULL DEFAULT 'INR', status VARCHAR(20) NOT NULL CHECK (status IN ('pending','authorized','paid','failed','refunded')), paid_at TIMESTAMPTZ, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW())",
"CREATE TABLE IF NOT EXISTS shipments (id SERIAL PRIMARY KEY, order_id INTEGER NOT NULL UNIQUE REFERENCES orders(id) ON DELETE CASCADE, carrier VARCHAR(60) NOT NULL, tracking_number VARCHAR(80) NOT NULL UNIQUE, shipping_status VARCHAR(30) NOT NULL CHECK (shipping_status IN ('pending','label_created','in_transit','delivered','delayed','returned')), shipped_at TIMESTAMPTZ, estimated_delivery_at TIMESTAMPTZ, delivered_at TIMESTAMPTZ, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW())",
"CREATE INDEX IF NOT EXISTS idx_orders_user_date ON orders(user_id, order_date DESC)",
"CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)",
"CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id)",
"CREATE INDEX IF NOT EXISTS idx_order_items_product ON order_items(product_id)",
"CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status)",
"CREATE INDEX IF NOT EXISTS idx_shipments_status ON shipments(shipping_status)",
]

def main():
    engine = get_owner_engine()
    with engine.begin() as conn:
        for statement in DDL:
            conn.execute(text(statement))
    print("Database schema initialized successfully.")

if __name__ == "__main__":
    main()
