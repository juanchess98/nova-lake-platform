CREATE SCHEMA IF NOT EXISTS ops;

CREATE TABLE IF NOT EXISTS ops.customers (
    customer_id BIGINT PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    country_code CHAR(2) NOT NULL,
    signup_date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS ops.products (
    product_id BIGINT PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    list_price NUMERIC(12,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS ops.orders (
    order_id BIGINT PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    order_timestamp TIMESTAMP NOT NULL,
    status TEXT NOT NULL,
    currency CHAR(3) NOT NULL,
    total_amount NUMERIC(12,2) NOT NULL,
    payment_method TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ops.order_items (
    order_item_id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(12,2) NOT NULL,
    line_amount NUMERIC(12,2) NOT NULL
);
