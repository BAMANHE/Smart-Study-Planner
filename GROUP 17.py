"""
Campus Food Delivery and Order Management System
Course: 1203 ST - Programming Fundamentals
Option 2

A menu-driven console application for a campus canteen.
"""

import json
from datetime import datetime
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "orders_log.json"

MENU = {
    "01": {"name": "Chicken & Chips", "category": "Meals", "price": 12000},
    "02": {"name": "Beef Pilau", "category": "Meals", "price": 10000},
    "03": {"name": "Vegetable Rice", "category": "Meals", "price": 8000},
    "04": {"name": "Rice Beans", "category": "Meals", "price": 10000},
    "05": {"name": "Posh Fish", "category": "Meals", "price": 15000},
    "06": {"name": "Soda", "category": "Drinks", "price": 2500},
    "07": {"name": "Mineral Water", "category": "Drinks", "price": 1500},
    "08": {"name": "Fresh Juice", "category": "Drinks", "price": 4000},
    "09": {"name": "Samosa", "category": "Snacks", "price": 2000},
    "10": {"name": "Chapati", "category": "Snacks", "price": 1500},
    "11": {"name": "Crisps", "category": "Snacks", "price": 2000},
    "12": {"name": "Gnuts", "category": "Snacks", "price": 2000},
}

RIDER_NAMES = ["MUKEMBO", "TIMOTHY", "MERCY", "DANIEL", "MALIK"]
STATUSES = ["Pending", "Out for Delivery", "Delivered"]
STATUS_FLOW = {
    "Pending": "Out for Delivery",
    "Out for Delivery": "Delivered",
}


def money(amount):
    """Format a number as Uganda Shillings."""
    return f"UGX {amount:,.0f}"


def get_next_order_id(orders):
    """Return the next simple sequential order number, starting at 01."""
    return f"{len(orders) + 1:02d}"


def calculate_delivery_fee(distance_km):
    """Calculate delivery fee using the delivery distance in kilometres."""
    if distance_km <= 2:
        return 1000
    if distance_km <= 5:
        return 2000
    if distance_km <= 10:
        return 3000
    return 5000


def read_positive_float(prompt):
    """Read a positive decimal number, such as a delivery distance in km."""
    while True:
        value = input(prompt).strip()
        try:
            number = float(value)
            if number > 0:
                return number
            print("Please enter a number greater than zero.")
        except ValueError:
            print("Invalid input. Enter a valid number, for example 3 or 4.5.")


def load_orders():
    """Load saved completed orders. Return an empty list if the file is missing/corrupt."""
    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, list):
            raise ValueError("The log must contain a list of orders.")

        # Keep order numbers simple and sequential (01, 02, 03, ...).
        # This also converts records created by an older version that used
        # long timestamp-based order IDs.
        for number, order in enumerate(data, start=1):
            if isinstance(order, dict):
                order["order_id"] = f"{number:02d}"
        return data
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"\nWarning: Could not load saved orders ({error}).")
        print("The system will continue with an empty order history.\n")
        return []


def save_orders(orders):
    """Save all completed orders to the log file."""
    try:
        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(orders, file, indent=4)
        return True
    except OSError as error:
        print(f"Error: Could not save the order log: {error}")
        return False


def display_menu():
    """Display all menu items grouped by category."""
    print("\n" + "=" * 68)
    print("CAMPUS CANTEEN MENU")
    print("=" * 68)

    current_category = None
    for code, item in MENU.items():
        if item["category"] != current_category:
            current_category = item["category"]
            print(f"\n{current_category.upper()}")
            print("-" * 68)
        print(f"{code:4} | {item['name']:<22} | {money(item['price']):>12}")
    print("=" * 68)


def read_non_empty(prompt):
    """Read a non-empty string."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Input cannot be empty. Please try again.")


def read_positive_int(prompt):
    """Read a positive whole number."""
    while True:
        value = input(prompt).strip()
        try:
            number = int(value)
            if number > 0:
                return number
            print("Please enter a number greater than zero.")
        except ValueError:
            print("Invalid input. Enter a whole number.")


def choose_menu_item():
    """Ask the user for a valid menu item code."""
    while True:
        code = input("Enter item code (or DONE to finish): ").strip().upper()
        if code == "DONE":
            return None
        if code in MENU:
            return code
        print("Invalid item code. Please choose a code shown on the menu.")


def calculate_order_totals(items, distance_km):
    """Calculate subtotal, distance-based delivery fee and grand total."""
    subtotal = sum(line["quantity"] * line["unit_price"] for line in items)
    delivery_fee = calculate_delivery_fee(distance_km)
    return subtotal, delivery_fee, subtotal + delivery_fee


def create_order(orders):
    """Take a new customer order and assign an available rider."""
    display_menu()
    customer_name = read_non_empty("\nCustomer name: ")
    customer_contact = read_non_empty("Customer contact: ")

    items = []
    print("\nSelect items. Enter DONE when finished.")
    while True:
        code = choose_menu_item()
        if code is None:
            if items:
                break
            print("You must add at least one item.")
            continue

        quantity = read_positive_int(f"Quantity for {MENU[code]['name']}: ")

        existing = next((line for line in items if line["code"] == code), None)
        if existing:
            existing["quantity"] += quantity
        else:
            items.append({
                "code": code,
                "name": MENU[code]["name"],
                "category": MENU[code]["category"],
                "unit_price": MENU[code]["price"],
                "quantity": quantity,
            })
        print(f"Added {quantity} x {MENU[code]['name']}.")

    print("\nDELIVERY FEE RATES")
    print("0–2 km     : UGX 1,000")
    print("Over 2–5 km : UGX 2,000")
    print("Over 5–10 km: UGX 3,000")
    print("Over 10 km  : UGX 5,000")
    distance_km = read_positive_float("Delivery distance (km): ")
    subtotal, delivery_fee, total = calculate_order_totals(items, distance_km)

    available_riders = [
        rider for rider in RIDER_NAMES
        if not any(
            order.get("rider") == rider and
            order.get("status") in {"Pending", "Out for Delivery"}
            for order in orders
        )
    ]

    if not available_riders:
        print("\nNo rider is currently available. Complete/deliver an existing order first.")
        return

    print("\nORDER SUMMARY")
    print("-" * 68)
    for line in items:
        line_total = line["quantity"] * line["unit_price"]
        print(f"{line['quantity']} x {line['name']:<22} {money(line_total):>12}")
    print("-" * 68)
    print(f"{'Subtotal:':<45}{money(subtotal):>12}")
    print(f"{'Delivery distance:':<45}{distance_km:g} km")
    print(f"{'Delivery fee:':<45}{money(delivery_fee):>12}")
    print(f"{'TOTAL:':<45}{money(total):>12}")

    print("\nAvailable riders:")
    for index, rider in enumerate(available_riders, start=1):
        print(f"{index}. {rider}")

    while True:
        choice = input("Choose rider number: ").strip()
        try:
            index = int(choice)
            if 1 <= index <= len(available_riders):
                rider = available_riders[index - 1]
                break
            print("Choose one of the displayed rider numbers.")
        except ValueError:
            print("Invalid input. Enter a rider number.")

    order = {
        "order_id": get_next_order_id(orders),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "customer_name": customer_name,
        "customer_contact": customer_contact,
        "items": items,
        "subtotal": subtotal,
        "delivery_distance_km": distance_km,
        "delivery_fee": delivery_fee,
        "total": total,
        "rider": rider,
        "status": "Pending",
    }

    orders.append(order)
    print(f"\nOrder {order['order_id']} created successfully.")
    print(f"Rider assigned: {rider}")
    print(f"Current status: Pending")

    # The order is saved immediately so it is not lost if the programme closes.
    if save_orders(orders):
        print("Order saved successfully.")


def list_orders(orders):
    """Display all saved orders."""
    if not orders:
        print("\nNo orders are currently recorded.")
        return

    print("\n" + "=" * 95)
    print("ORDER LIST")
    print("=" * 95)
    print(f"{'Order ID':<23}{'Customer':<18}{'Rider':<12}{'Status':<20}{'Total':>15}")
    print("-" * 95)
    for order in orders:
        print(
            f"{order['order_id']:<23}"
            f"{order['customer_name'][:17]:<18}"
            f"{order['rider']:<12}"
            f"{order['status']:<20}"
            f"{money(order['total']):>15}"
        )


def update_order_status(orders):
    """Move an order to the next valid status only."""
    active_orders = [
        order for order in orders
        if order.get("status") in {"Pending", "Out for Delivery"}
    ]

    if not active_orders:
        print("\nThere are no active orders requiring a status update.")
        return

    print("\nACTIVE ORDERS")
    for index, order in enumerate(active_orders, start=1):
        next_status = STATUS_FLOW[order["status"]]
        print(
            f"{index}. {order['order_id']} | {order['customer_name']} | "
            f"{order['status']} -> {next_status}"
        )

    while True:
        choice = input("Select order number (0 to cancel): ").strip()
        try:
            index = int(choice)
            if index == 0:
                return
            if 1 <= index <= len(active_orders):
                order = active_orders[index - 1]
                break
            print("Choose a valid order number.")
        except ValueError:
            print("Invalid input.")

    next_status = STATUS_FLOW[order["status"]]
    order["status"] = next_status

    if save_orders(orders):
        print(f"Order {order['order_id']} is now '{next_status}'.")


def revenue_and_best_seller(orders):
    """Display revenue, best-selling item and status counts."""
    completed_orders = [o for o in orders if o.get("status") == "Delivered"]
    total_revenue = sum(o.get("total", 0) for o in completed_orders)

    item_quantities = {}
    for order in completed_orders:
        for line in order.get("items", []):
            item_quantities[line["name"]] = (
                item_quantities.get(line["name"], 0) + line["quantity"]
            )

    best_seller = "No delivered item yet"
    best_quantity = 0
    if item_quantities:
        best_seller, best_quantity = max(item_quantities.items(), key=lambda pair: pair[1])

    status_counts = {status: 0 for status in STATUSES}
    for order in orders:
        status = order.get("status")
        if status in status_counts:
            status_counts[status] += 1

    print("\n" + "=" * 68)
    print("SALES AND ORDER REPORT")
    print("=" * 68)
    print(f"Day's revenue from delivered orders : {money(total_revenue)}")
    print(f"Best-selling item                   : {best_seller}")
    print(f"Quantity sold                        : {best_quantity}")
    print("\nORDER STATUS COUNTS")
    for status in STATUSES:
        print(f"{status:<25}: {status_counts[status]}")
    print("=" * 68)


def search_orders(orders):
    """Search for orders by order ID, customer name or contact."""
    if not orders:
        print("\nNo orders available to search.")
        return

    query = read_non_empty("Search by order ID, customer name or contact: ").lower()
    matches = [
        order for order in orders
        if query in order["order_id"].lower()
        or query in order["customer_name"].lower()
        or query in order["customer_contact"].lower()
    ]

    if not matches:
        print("No matching orders found.")
        return

    for order in matches:
        print("\n" + "-" * 68)
        print(f"Order ID : {order['order_id']}")
        print(f"Customer : {order['customer_name']}")
        print(f"Contact  : {order['customer_contact']}")
        print(f"Rider    : {order['rider']}")
        print(f"Status   : {order['status']}")
        print(f"Distance : {order.get('delivery_distance_km', 'N/A')} km")
        print(f"Delivery : {money(order.get('delivery_fee', 0))}")
        print(f"Total    : {money(order['total'])}")
        print("Items:")
        for line in order["items"]:
            print(f"  {line['quantity']} x {line['name']}")


def main_menu():
    """Run the main looping driver programme."""
    orders = load_orders()

    while True:
        print("\n" + "=" * 68)
        print("CAMPUS FOOD DELIVERY AND ORDER MANAGEMENT SYSTEM")
        print("=" * 68)
        print("1. Display menu")
        print("2. Take a new order")
        print("3. View all orders")
        print("4. Update order status")
        print("5. Search orders")
        print("6. Sales and reporting")
        print("7. Exit")
        print("=" * 68)

        choice = input("Enter your choice (1-7): ").strip()

        if choice == "1":
            display_menu()
        elif choice == "2":
            create_order(orders)
        elif choice == "3":
            list_orders(orders)
        elif choice == "4":
            update_order_status(orders)
        elif choice == "5":
            search_orders(orders)
        elif choice == "6":
            revenue_and_best_seller(orders)
        elif choice == "7":
            print("\nThank you for using the Campus Food Delivery System.")
            break
        else:
            print("Invalid choice. Please select a number from 1 to 7.")


if __name__ == "__main__":
    main_menu()
