# NovaLake Use Case (Module 1 Baseline)

## Context

NovaLake supports analytics for a fictional multi-country e-commerce business. Module 1 establishes the baseline lakehouse to consolidate commerce and operational data into trusted analytical products.

## Module 1 Scope

Module 1 delivers:
- reproducible synthetic commerce source data
- raw -> bronze -> silver -> gold batch pipelines
- six operational datasets (`customers`, `products`, `orders`, `order_items`, `payments`, `shipments`)
- six gold analytical products for business and operations monitoring

This module is the platform baseline for all future NovaLake evolution.

## Business Objectives

- monitor daily and geographic revenue performance
- understand product and customer value contribution
- monitor payment reliability and method behavior
- monitor shipment throughput, delays, and delivery outcomes

## Key Questions Answered

### Commercial
- How much revenue is generated daily?
- Which countries drive most revenue?
- Which products are top revenue contributors?
- Which customers drive lifetime revenue concentration?

### Payments
- What is the payment success rate over time?
- Which payment methods show higher failure or pending rates?
- How much payment volume is attempted by method/date?

### Fulfillment
- How many shipments are delivered, delayed, or still in transit?
- What is average delivery time by carrier/country?
- Where is delivery reliability weaker?

## Gold Data Products in Module 1

- `daily_revenue`
  - Daily revenue and order productivity trend.
- `sales_by_country`
  - Country-level sales performance and average order value.
- `top_products`
  - Product ranking by revenue, units sold, and order reach.
- `customer_revenue`
  - Customer-level lifetime revenue and order behavior profile.
- `payment_success_rate`
  - Payment outcome quality by date and payment method.
- `shipment_delivery_summary`
  - Shipment status mix, delivery rate, and average delivery time.

## Stakeholders

- Leadership: business growth and market-level performance visibility
- Finance: revenue integrity and payment execution monitoring
- Operations: order-to-shipment execution and delivery reliability
- Data Engineering: pipeline correctness, reproducibility, and evolution readiness
- Data Analytics: curated gold products for recurring analysis

## Success Criteria

Business:
- reliable revenue, country, product, customer, payment, and shipment insights
- faster analytical turnaround with trusted curated outputs

Platform:
- stable end-to-end execution of all Module 1 pipelines
- clear medallion layering and entity relationships
- documented architecture baseline that supports modular growth

## Evolution Alignment

Module 1 is intentionally batch/local-first. Future modules add storage evolution, CDC, streaming, metadata intelligence, and AI assistance without discarding Module 1 domain and data contracts.
