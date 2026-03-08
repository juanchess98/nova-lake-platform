import argparse
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker


@dataclass(frozen=True)
class GenerationConfig:
    seed: int = 42
    customers_count: int = 1_000
    products_count: int = 250
    orders_count: int = 15_000
    target_order_items_count: int = 35_000
    min_payments_count: int = 15_000
    max_payments_count: int = 17_000
    min_shipments_count: int = 12_000
    max_shipments_count: int = 14_000


COUNTRY_CITY_MAP = {
    "US": ["New York", "Los Angeles", "Chicago", "Austin"],
    "CA": ["Toronto", "Vancouver", "Montreal", "Calgary"],
    "MX": ["Mexico City", "Guadalajara", "Monterrey", "Puebla"],
    "CO": ["Bogota", "Medellin", "Cali", "Barranquilla"],
    "ES": ["Madrid", "Barcelona", "Valencia", "Seville"],
    "BR": ["Sao Paulo", "Rio de Janeiro", "Brasilia", "Recife"],
    "AR": ["Buenos Aires", "Cordoba", "Rosario", "Mendoza"],
    "CL": ["Santiago", "Valparaiso", "Concepcion", "Antofagasta"],
}

CATEGORY_SUBCATEGORY_MAP = {
    "Electronics": ["Phones", "Laptops", "Audio", "Accessories"],
    "Home": ["Kitchen", "Furniture", "Decor", "Appliances"],
    "Fashion": ["Men", "Women", "Shoes", "Accessories"],
    "Sports": ["Fitness", "Outdoor", "Cycling", "Team Sports"],
    "Beauty": ["Skincare", "Makeup", "Haircare", "Fragrance"],
    "Books": ["Fiction", "Non-Fiction", "Children", "Education"],
    "Toys": ["STEM", "Board Games", "Plush", "Action Figures"],
}

PAYMENT_METHODS = ["credit_card", "debit_card", "paypal", "bank_transfer", "wallet"]
CARRIERS = ["DHL", "FedEx", "UPS", "USPS", "Servientrega", "Correos"]


class CommerceDataGenerator:
    def __init__(self, config: GenerationConfig) -> None:
        self.config = config
        self.random = random.Random(config.seed)
        self.rng = np.random.default_rng(config.seed)
        self.faker = Faker()
        self.faker.seed_instance(config.seed)

        project_root = Path(__file__).resolve().parents[2]
        self.output_dir = project_root / "data" / "raw"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _random_datetime(self, start: datetime, end: datetime) -> datetime:
        total_seconds = int((end - start).total_seconds())
        return start + timedelta(seconds=self.random.randint(0, total_seconds))

    def generate_customers(self) -> pd.DataFrame:
        countries = list(COUNTRY_CITY_MAP.keys())
        segments = self.rng.choice(
            ["Standard", "Premium", "VIP"],
            size=self.config.customers_count,
            p=[0.75, 0.20, 0.05],
        )

        records = []
        start_date = datetime(2020, 1, 1)
        end_date = datetime(2026, 3, 1)

        for idx in range(1, self.config.customers_count + 1):
            first_name = self.faker.first_name()
            last_name = self.faker.last_name()
            country = self.random.choice(countries)
            city = self.random.choice(COUNTRY_CITY_MAP[country])
            signup_date = self._random_datetime(start_date, end_date).date().isoformat()
            customer_id = f"CUST{idx:06d}"

            # Force uniqueness by embedding the deterministic index in the local-part.
            email_local = f"{first_name}.{last_name}.{idx}".lower().replace("'", "")
            email = f"{email_local}@{self.faker.free_email_domain()}"

            records.append(
                {
                    "customer_id": customer_id,
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "country": country,
                    "city": city,
                    "signup_date": signup_date,
                    "customer_segment": segments[idx - 1],
                    "is_active": bool(self.rng.random() < 0.92),
                }
            )

        customers = pd.DataFrame(records)
        if not customers["email"].is_unique:
            raise ValueError("Customer emails must be unique.")
        return customers

    def generate_products(self) -> pd.DataFrame:
        categories = list(CATEGORY_SUBCATEGORY_MAP.keys())
        brands = [self.faker.company() for _ in range(50)]

        records = []
        start_date = datetime(2019, 1, 1)
        end_date = datetime(2026, 3, 1)

        for idx in range(1, self.config.products_count + 1):
            category = self.random.choice(categories)
            subcategory = self.random.choice(CATEGORY_SUBCATEGORY_MAP[category])
            brand = self.random.choice(brands)

            # Category-specific price ranges keep product catalog more realistic.
            if category == "Electronics":
                unit_price = self.rng.uniform(80, 1800)
            elif category == "Home":
                unit_price = self.rng.uniform(20, 600)
            elif category == "Fashion":
                unit_price = self.rng.uniform(10, 250)
            elif category == "Sports":
                unit_price = self.rng.uniform(15, 450)
            elif category == "Beauty":
                unit_price = self.rng.uniform(8, 180)
            elif category == "Books":
                unit_price = self.rng.uniform(6, 90)
            else:  # Toys
                unit_price = self.rng.uniform(8, 220)

            unit_price = round(float(unit_price), 2)
            cost_ratio = float(self.rng.uniform(0.45, 0.75))
            cost = round(unit_price * cost_ratio, 2)

            records.append(
                {
                    "product_id": f"PROD{idx:06d}",
                    "product_name": f"{brand} {subcategory} {self.faker.word().title()}",
                    "category": category,
                    "subcategory": subcategory,
                    "brand": brand,
                    "unit_price": unit_price,
                    "cost": cost,
                    "created_at": self._random_datetime(start_date, end_date).isoformat(sep=" "),
                    "is_active": bool(self.rng.random() < 0.95),
                }
            )

        return pd.DataFrame(records)

    def generate_orders(self, customers: pd.DataFrame) -> pd.DataFrame:
        customer_ids = customers["customer_id"].to_numpy()

        statuses = self.rng.choice(
            ["completed", "pending", "cancelled"],
            size=self.config.orders_count,
            p=[0.78, 0.15, 0.07],
        )
        payment_methods = self.rng.choice(
            PAYMENT_METHODS,
            size=self.config.orders_count,
            p=[0.52, 0.20, 0.16, 0.07, 0.05],
        )

        start_ts = datetime(2023, 1, 1)
        end_ts = datetime(2026, 3, 1)

        records = []
        for idx in range(1, self.config.orders_count + 1):
            records.append(
                {
                    "order_id": f"ORD{idx:08d}",
                    "customer_id": str(self.random.choice(customer_ids)),
                    "order_timestamp": self._random_datetime(start_ts, end_ts).isoformat(sep=" "),
                    "order_status": statuses[idx - 1],
                    "currency": "USD",
                    # Monetary fields are finalized after order_items generation.
                    "subtotal_amount": 0.0,
                    "tax_amount": 0.0,
                    "shipping_amount": 0.0,
                    "total_amount": 0.0,
                    "payment_method": payment_methods[idx - 1],
                }
            )

        return pd.DataFrame(records)

    def generate_order_items(self, orders: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
        order_ids = orders["order_id"].to_numpy()
        product_ids = products["product_id"].to_numpy()
        price_map = products.set_index("product_id")["unit_price"].to_dict()

        # Distribution tuned for ~35k rows from 15k orders.
        item_counts = self.rng.choice([1, 2, 3, 4, 5], size=len(order_ids), p=[0.24, 0.38, 0.23, 0.11, 0.04])

        total_items = int(item_counts.sum())
        target = self.config.target_order_items_count

        # Adjust toward target while keeping at least one item per order.
        if total_items < target:
            deficit = target - total_items
            boost_idx = self.rng.choice(len(item_counts), size=deficit, replace=True)
            item_counts[boost_idx] += 1
        elif total_items > target:
            excess = total_items - target
            candidate_idx = np.where(item_counts > 1)[0]
            if len(candidate_idx) > 0:
                reduce_idx = self.rng.choice(candidate_idx, size=excess, replace=True)
                item_counts[reduce_idx] -= 1

        rows = []
        item_id = 1

        for order_id, count in zip(order_ids, item_counts):
            for _ in range(int(count)):
                product_id = str(self.random.choice(product_ids))
                quantity = int(self.rng.integers(1, 6))
                unit_price = float(price_map[product_id])

                gross_amount = round(quantity * unit_price, 2)
                if self.rng.random() < 0.22:
                    discount_amount = round(float(self.rng.uniform(0.0, min(gross_amount * 0.30, 50.0))), 2)
                else:
                    discount_amount = 0.0

                line_total = round(gross_amount - discount_amount, 2)

                rows.append(
                    {
                        "order_item_id": f"ITEM{item_id:08d}",
                        "order_id": order_id,
                        "product_id": product_id,
                        "quantity": quantity,
                        "unit_price": round(unit_price, 2),
                        "discount_amount": discount_amount,
                        "line_total": line_total,
                    }
                )
                item_id += 1

        return pd.DataFrame(rows)

    def finalize_order_amounts(
        self,
        orders: pd.DataFrame,
        order_items: pd.DataFrame,
        customers: pd.DataFrame,
    ) -> pd.DataFrame:
        subtotal_by_order = order_items.groupby("order_id", as_index=True)["line_total"].sum().round(2)
        customer_country = customers.set_index("customer_id")["country"].to_dict()

        tax_rates = {
            "US": 0.08,
            "CA": 0.12,
            "MX": 0.16,
            "CO": 0.19,
            "ES": 0.21,
            "BR": 0.17,
            "AR": 0.18,
            "CL": 0.19,
        }

        orders = orders.copy()
        orders["subtotal_amount"] = orders["order_id"].map(subtotal_by_order).fillna(0.0).round(2)

        tax_amounts = []
        shipping_amounts = []
        total_amounts = []

        for row in orders.itertuples(index=False):
            country = customer_country.get(row.customer_id, "US")
            tax_rate = tax_rates.get(country, 0.10)
            tax_amount = round(row.subtotal_amount * tax_rate, 2)

            if row.order_status == "cancelled":
                shipping_amount = 0.0
            elif row.subtotal_amount >= 120:
                shipping_amount = 0.0
            else:
                shipping_amount = float(self.random.choice([4.99, 6.99, 8.99, 10.99]))

            total_amount = round(row.subtotal_amount + tax_amount + shipping_amount, 2)
            tax_amounts.append(tax_amount)
            shipping_amounts.append(round(shipping_amount, 2))
            total_amounts.append(total_amount)

        orders["tax_amount"] = tax_amounts
        orders["shipping_amount"] = shipping_amounts
        orders["total_amount"] = total_amounts

        return orders

    def generate_payments(self, orders: pd.DataFrame) -> pd.DataFrame:
        base_rows = []
        retry_rows = []

        max_extra = self.config.max_payments_count - len(orders)
        extra_attempt_budget = max(0, min(max_extra, int(len(orders) * 0.12)))

        retry_candidates = orders.sample(n=extra_attempt_budget, random_state=self.config.seed)
        retry_candidate_ids = set(retry_candidates["order_id"].tolist())

        payment_id_counter = 1

        for row in orders.itertuples(index=False):
            order_ts = pd.Timestamp(row.order_timestamp)
            first_payment_ts = order_ts + pd.Timedelta(minutes=int(self.rng.integers(1, 181)))

            if row.order_status == "completed":
                first_status = str(self.rng.choice(["paid", "pending", "failed"], p=[0.94, 0.03, 0.03]))
            elif row.order_status == "pending":
                first_status = str(self.rng.choice(["pending", "paid", "failed"], p=[0.75, 0.15, 0.10]))
            else:
                first_status = str(self.rng.choice(["failed", "pending", "paid"], p=[0.70, 0.25, 0.05]))

            amount = row.total_amount
            if self.rng.random() < 0.03:
                amount = round(float(row.total_amount * self.rng.uniform(0.9, 1.1)), 2)

            base_rows.append(
                {
                    "payment_id": f"PAY{payment_id_counter:08d}",
                    "order_id": row.order_id,
                    "payment_timestamp": first_payment_ts.isoformat(sep=" "),
                    "payment_method": row.payment_method,
                    "payment_status": first_status,
                    "payment_amount": amount,
                    "currency": "USD",
                }
            )
            payment_id_counter += 1

            if row.order_id in retry_candidate_ids and len(retry_rows) < max_extra:
                second_payment_ts = first_payment_ts + pd.Timedelta(minutes=int(self.rng.integers(10, 721)))
                second_status = str(self.rng.choice(["paid", "failed", "pending"], p=[0.60, 0.30, 0.10]))

                retry_rows.append(
                    {
                        "payment_id": f"PAY{payment_id_counter:08d}",
                        "order_id": row.order_id,
                        "payment_timestamp": second_payment_ts.isoformat(sep=" "),
                        "payment_method": str(self.random.choice(PAYMENT_METHODS)),
                        "payment_status": second_status,
                        "payment_amount": row.total_amount,
                        "currency": "USD",
                    }
                )
                payment_id_counter += 1

        payments = pd.DataFrame(base_rows + retry_rows).sort_values("payment_timestamp").reset_index(drop=True)

        if len(payments) < self.config.min_payments_count or len(payments) > self.config.max_payments_count:
            raise ValueError(
                f"Payments out of target range: {len(payments)} not in "
                f"[{self.config.min_payments_count}, {self.config.max_payments_count}]"
            )

        return payments

    def generate_shipments(self, orders: pd.DataFrame, customers: pd.DataFrame) -> pd.DataFrame:
        customer_country = customers.set_index("customer_id")["country"].to_dict()

        eligible = orders[orders["order_status"] != "cancelled"].copy()
        max_shipments = min(self.config.max_shipments_count, len(eligible))
        min_shipments = min(self.config.min_shipments_count, max_shipments)
        target_shipments = int(self.rng.integers(min_shipments, max_shipments + 1))

        selected = eligible.sample(n=target_shipments, random_state=self.config.seed).reset_index(drop=True)

        rows = []
        for idx, row in enumerate(selected.itertuples(index=False), start=1):
            order_ts = pd.Timestamp(row.order_timestamp)
            shipment_ts = order_ts + pd.Timedelta(hours=int(self.rng.integers(2, 97)))
            shipment_status = str(self.rng.choice(["delivered", "shipped", "delayed"], p=[0.72, 0.22, 0.06]))

            if shipment_status == "shipped":
                delivery_ts = pd.NaT
            elif shipment_status == "delayed" and self.rng.random() < 0.30:
                delivery_ts = pd.NaT
            elif shipment_status == "delayed":
                delivery_ts = shipment_ts + pd.Timedelta(days=int(self.rng.integers(5, 15)))
            else:
                delivery_ts = shipment_ts + pd.Timedelta(days=int(self.rng.integers(1, 9)))

            rows.append(
                {
                    "shipment_id": f"SHP{idx:08d}",
                    "order_id": row.order_id,
                    "shipment_timestamp": shipment_ts.isoformat(sep=" "),
                    "delivery_timestamp": None if pd.isna(delivery_ts) else delivery_ts.isoformat(sep=" "),
                    "shipment_status": shipment_status,
                    "carrier": str(self.random.choice(CARRIERS)),
                    "shipping_country": customer_country.get(row.customer_id, "US"),
                }
            )

        return pd.DataFrame(rows)

    def validate_consistency(
        self,
        customers: pd.DataFrame,
        products: pd.DataFrame,
        orders: pd.DataFrame,
        order_items: pd.DataFrame,
        payments: pd.DataFrame,
        shipments: pd.DataFrame,
    ) -> None:
        if not set(orders["customer_id"]).issubset(set(customers["customer_id"])):
            raise ValueError("orders.customer_id contains unknown customers")

        if not set(order_items["order_id"]).issubset(set(orders["order_id"])):
            raise ValueError("order_items.order_id contains unknown orders")

        if not set(order_items["product_id"]).issubset(set(products["product_id"])):
            raise ValueError("order_items.product_id contains unknown products")

        if not set(payments["order_id"]).issubset(set(orders["order_id"])):
            raise ValueError("payments.order_id contains unknown orders")

        if not set(shipments["order_id"]).issubset(set(orders["order_id"])):
            raise ValueError("shipments.order_id contains unknown orders")

        # Core arithmetic integrity checks.
        line_check = (
            (order_items["quantity"] * order_items["unit_price"] - order_items["discount_amount"]).round(2)
            == order_items["line_total"].round(2)
        )
        if not bool(line_check.all()):
            raise ValueError("order_items.line_total arithmetic check failed")

        subtotal_by_order = order_items.groupby("order_id")["line_total"].sum().round(2)
        merged = orders[["order_id", "subtotal_amount"]].copy()
        merged["calc_subtotal"] = merged["order_id"].map(subtotal_by_order).fillna(0.0).round(2)

        if not bool((merged["subtotal_amount"].round(2) == merged["calc_subtotal"]).all()):
            raise ValueError("orders.subtotal_amount does not match SUM(order_items.line_total)")

        total_check = (
            (orders["subtotal_amount"] + orders["tax_amount"] + orders["shipping_amount"]).round(2)
            == orders["total_amount"].round(2)
        )
        if not bool(total_check.all()):
            raise ValueError("orders.total_amount arithmetic check failed")

        order_ts = pd.to_datetime(orders.set_index("order_id")["order_timestamp"])

        payments_check = pd.to_datetime(payments["payment_timestamp"]).values >= order_ts.loc[payments["order_id"]].values
        if not bool(np.all(payments_check)):
            raise ValueError("payments.payment_timestamp must be >= orders.order_timestamp")

        shipment_order_ts = order_ts.loc[shipments["order_id"]].values
        shipment_ts = pd.to_datetime(shipments["shipment_timestamp"]).values
        if not bool(np.all(shipment_ts >= shipment_order_ts)):
            raise ValueError("shipments.shipment_timestamp must be >= orders.order_timestamp")

        delivered_mask = shipments["delivery_timestamp"].notna()
        if delivered_mask.any():
            delivery_ts = pd.to_datetime(shipments.loc[delivered_mask, "delivery_timestamp"]).values
            base_ship_ts = pd.to_datetime(shipments.loc[delivered_mask, "shipment_timestamp"]).values
            if not bool(np.all(delivery_ts >= base_ship_ts)):
                raise ValueError("delivery_timestamp must be >= shipment_timestamp")

    def write_outputs(
        self,
        customers: pd.DataFrame,
        products: pd.DataFrame,
        orders: pd.DataFrame,
        order_items: pd.DataFrame,
        payments: pd.DataFrame,
        shipments: pd.DataFrame,
    ) -> None:
        customers.to_csv(self.output_dir / "customers.csv", index=False)
        products.to_csv(self.output_dir / "products.csv", index=False)
        orders.to_csv(self.output_dir / "orders.csv", index=False)
        order_items.to_csv(self.output_dir / "order_items.csv", index=False)
        payments.to_csv(self.output_dir / "payments.csv", index=False)
        shipments.to_csv(self.output_dir / "shipments.csv", index=False)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate synthetic commerce datasets for NovaLake Module 1")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for deterministic generation")
    parser.add_argument("--customers", type=int, default=1_000, help="Number of customers")
    parser.add_argument("--products", type=int, default=250, help="Number of products")
    parser.add_argument("--orders", type=int, default=15_000, help="Number of orders")
    parser.add_argument("--order-items", type=int, default=35_000, help="Target number of order_items")
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()
    config = GenerationConfig(
        seed=args.seed,
        customers_count=args.customers,
        products_count=args.products,
        orders_count=args.orders,
        target_order_items_count=args.order_items,
    )

    generator = CommerceDataGenerator(config)

    print("[NovaLake] Generating customers...")
    customers = generator.generate_customers()

    print("[NovaLake] Generating products...")
    products = generator.generate_products()

    print("[NovaLake] Generating orders...")
    orders = generator.generate_orders(customers)

    print("[NovaLake] Generating order_items...")
    order_items = generator.generate_order_items(orders, products)

    print("[NovaLake] Finalizing order monetary fields...")
    orders = generator.finalize_order_amounts(orders, order_items, customers)

    print("[NovaLake] Generating payments...")
    payments = generator.generate_payments(orders)

    print("[NovaLake] Generating shipments...")
    shipments = generator.generate_shipments(orders, customers)

    print("[NovaLake] Validating consistency rules...")
    generator.validate_consistency(customers, products, orders, order_items, payments, shipments)

    print("[NovaLake] Writing CSV files to data/raw/ ...")
    generator.write_outputs(customers, products, orders, order_items, payments, shipments)

    print("[NovaLake] Data generation completed.")
    print(
        "[NovaLake] Row counts -> "
        f"customers={len(customers)}, products={len(products)}, orders={len(orders)}, "
        f"order_items={len(order_items)}, payments={len(payments)}, shipments={len(shipments)}"
    )


if __name__ == "__main__":
    main()
