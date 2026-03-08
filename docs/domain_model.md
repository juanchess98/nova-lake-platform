# NovaLake Domain Model

## Overview

The NovaLake platform is based on a simplified commerce domain representing a fictional e-commerce company.

The domain model captures both commercial and operational entities required to analyze sales performance, customer activity, payment execution, and shipment behavior.

---

# Core Entities

The current platform scope includes six primary entities:

- customers
- products
- orders
- order_items
- payments
- shipments

These entities represent the core analytical foundation of the NovaLake commerce platform.

---

# Entity Descriptions

## Customers

Represents individual users who place orders on the platform.

Typical attributes include:

- customer_id
- email
- first_name
- last_name
- country
- city
- signup_date
- customer_segment
- is_active

Customers may place multiple orders over time.

---

## Products

Represents items available for purchase.

Typical attributes include:

- product_id
- product_name
- category
- subcategory
- brand
- unit_price
- cost
- created_at
- is_active

Products may appear in multiple order items.

---

## Orders

Represents transactions initiated by customers.

Typical attributes include:

- order_id
- customer_id
- order_timestamp
- order_status
- currency
- subtotal_amount
- tax_amount
- shipping_amount
- total_amount
- payment_method

Each order belongs to a single customer and may contain multiple order items.

---

## Order Items

Represents individual products purchased within an order.

Typical attributes include:

- order_item_id
- order_id
- product_id
- quantity
- unit_price
- discount_amount
- line_total

An order may contain multiple order items.

---

## Payments

Represents payment attempts or completed payments associated with orders.

Typical attributes include:

- payment_id
- order_id
- payment_timestamp
- payment_method
- payment_status
- payment_amount
- currency

Each order may have one or more payment-related records depending on business rules and simulation design.

---

## Shipments

Represents shipment execution and delivery status for orders.

Typical attributes include:

- shipment_id
- order_id
- shipment_timestamp
- delivery_timestamp
- shipment_status
- carrier
- shipping_country

Each order may generate a shipment record depending on order lifecycle and fulfillment logic.

---

# Entity Relationships

The relationships between entities are illustrated conceptually below.

- One customer can place many orders.
- One order can contain many order items.
- One product can appear in many order items.
- One order can have one or more payment records.
- One order can have zero or one shipment record in the initial model.

---

# Domain Model Diagram (Conceptual)

Customer
   |
   | 1..N
   v
Orders ----------- Payments
   |
   | 1..N
   v
Order_Items
   ^
   |
   | N..1
Products

Orders
   |
   | 0..1
   v
Shipments

---

# Analytical Value of the Domain

This domain model supports multiple analytical perspectives:

## Commercial Analysis
- revenue trends
- sales by country
- top products
- customer revenue contribution

## Payment Analysis
- payment success rates
- payment method usage
- failed or pending payment visibility

## Fulfillment Analysis
- shipment status monitoring
- order-to-shipment timing
- delivery performance visibility

---

# Future Domain Expansion

Future platform modules may introduce additional domain entities including:

- inventory_snapshots
- order_status_history
- customer behavior events
- returns
- promotions

These additions will support more advanced analytical capabilities, operational monitoring, and AI-assisted exploration.