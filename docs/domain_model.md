# NovaLake Domain Model (Module 1 Baseline)

## Overview

NovaLake Module 1 models a simplified e-commerce domain with six operational entities that support both commercial and operational analytics.

Entities:
- `customers`
- `products`
- `orders`
- `order_items`
- `payments`
- `shipments`

This model is the baseline domain contract for future platform modules.

## Entity Details

### Customers

One row per customer profile.

Key attributes:
- `customer_id`
- `email`
- `first_name`
- `last_name`
- `country`
- `city`
- `signup_date`
- `customer_segment`
- `is_active`

### Products

One row per product in catalog.

Key attributes:
- `product_id`
- `product_name`
- `category`
- `subcategory`
- `brand`
- `unit_price`
- `cost`
- `created_at`
- `is_active`

### Orders

One row per order header.

Key attributes:
- `order_id`
- `customer_id`
- `order_timestamp`
- `order_status`
- `currency`
- `subtotal_amount`
- `tax_amount`
- `shipping_amount`
- `total_amount`
- `payment_method`

### Order Items

One row per product line within an order.

Key attributes:
- `order_item_id`
- `order_id`
- `product_id`
- `quantity`
- `unit_price`
- `discount_amount`
- `line_total`

### Payments

Payment execution events for orders.

Key attributes:
- `payment_id`
- `order_id`
- `payment_timestamp`
- `payment_method`
- `payment_status`
- `payment_amount`
- `currency`

Notes:
- One order can have multiple payment attempts.
- Payment status supports operational reliability analysis.

### Shipments

Shipment and delivery lifecycle records.

Key attributes:
- `shipment_id`
- `order_id`
- `shipment_timestamp`
- `delivery_timestamp`
- `shipment_status`
- `carrier`
- `shipping_country`

Notes:
- Typically generated for non-cancelled orders.
- Delivery timestamp may be null for in-progress deliveries.

## Relationship Model

- One customer -> many orders
- One order -> many order_items
- One product -> many order_items
- One order -> one or many payments
- One order -> zero or one shipment (Module 1 simulation default)

## Conceptual Diagram

`customers (1) -> (N) orders`

`orders (1) -> (N) order_items`

`products (1) -> (N) order_items`

`orders (1) -> (N) payments`

`orders (1) -> (0..1) shipments`

## Analytical Coverage Enabled by the Domain

- Revenue and sales trend analysis
- Product and category performance analysis
- Customer value segmentation
- Payment execution reliability monitoring
- Shipment and delivery performance monitoring

## Future Domain Evolution

Future modules may extend this baseline with entities such as:
- `inventory_snapshots`
- `order_status_history`
- `returns`
- `promotions`
- event-level behavioral streams

These additions should preserve compatibility with Module 1 core entity contracts.
