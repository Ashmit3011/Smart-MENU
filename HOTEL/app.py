import streamlit as st
import json
import os
from datetime import datetime
import time

MENU_FILE = "menu.json"
ORDER_FILE = "orders.json"

# Utility functions
def load_json(file):
    if not os.path.exists(file):
        with open(file, 'w', encoding='utf-8') as f:
            json.dump([], f)
    with open(file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(file, data):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def generate_order_id():
    orders = load_json(ORDER_FILE)
    return len(orders) + 1

# App config
st.set_page_config(page_title="Smart Table Ordering", layout="wide")

# State
if "cart" not in st.session_state:
    st.session_state.cart = []
if "table" not in st.session_state:
    st.session_state.table = ""
if "order_id" not in st.session_state:
    st.session_state.order_id = None
if "last_status" not in st.session_state:
    st.session_state.last_status = None

# Header
st.title("🍽️ Smart Table Ordering")
st.info("🎉 Get a Free Donut!\n\nOrder above ₹200 and enjoy a delicious free donut 🍩 with your meal!")

# Table number
st.text_input("Enter Table Number", key="table", value=st.session_state.table)

# Load menu and categories
menu = load_json(MENU_FILE)
categories = sorted(set(item.get("category", "Uncategorized") for item in menu if "category" in item))

# Create tabs if there are categories
if categories:
    tabs = st.tabs(categories)
    for index, category in enumerate(categories):
        with tabs[index]:
            st.subheader(f"{category} Menu")
            for item in [m for m in menu if m.get("category") == category]:
                tags = ""
                if item.get("spicy"): tags += " 🌶️"
                if item.get("veg"): tags += " 🥦"
                if item.get("popular"): tags += " ⭐"

                with st.container():
                    st.markdown(f"**{item['name']}** {tags}")
                    st.caption(f"₹{item['price']}")
                    qty = st.number_input(f"Quantity for {item['name']}", min_value=0, step=1, key=f"qty_{item['id']}")
                    if qty > 0:
                        existing = next((c for c in st.session_state.cart if c['id'] == item['id']), None)
                        if existing:
                            existing['qty'] = qty
                        else:
                            st.session_state.cart.append({
                                "id": item["id"],
                                "name": item["name"],
                                "price": item["price"],
                                "qty": qty
                            })
else:
    st.warning("⚠️ No categories found in menu. Please check your menu.json.")

# Cart
st.markdown("## 🛒 Your Cart")
total = 0
if st.session_state.cart:
    for item in st.session_state.cart:
        st.write(f"- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")
        total += item['qty'] * item['price']

    st.markdown(f"**Total: ₹{total}**")
    if total >= 200:
        st.success("🎉 Congrats! You’ll get a free donut with your order.")

    if st.button("✅ Place Order"):
        if not st.session_state.table.strip():
            st.error("Please enter your table number.")
        else:
            new_order = {
                "id": generate_order_id(),
                "table": st.session_state.table.strip(),
                "cart": st.session_state.cart,
                "status": "Pending",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            orders = load_json(ORDER_FILE)
            orders.append(new_order)
            save_json(ORDER_FILE, orders)
            st.session_state.order_id = new_order["id"]
            st.session_state.last_status = "Pending"
            st.success(f"🎉 Order placed successfully! Table: {new_order['table']}")
            st.balloons()
            st.session_state.cart = []
            st.rerun()
else:
    st.info("Your cart is empty. Add items from the menu.")

# Auto-refresh order tracking
if st.session_state.order_id:
    st.markdown("---")
    st.header("🔍 Track Your Order")

    orders = load_json(ORDER_FILE)
    order = next((o for o in orders if o["id"] == st.session_state.order_id), None)
    if order:
        if order["status"] != st.session_state.last_status:
            st.toast(f"📢 Status Updated: {order['status']}")
            st.session_state.last_status = order["status"]

        st.success(f"Order #{order['id']} for Table {order['table']}")
        st.markdown(f"**Status:** `{order['status']}`")

        # Progress bar
        status_stages = ["Pending", "Preparing", "Served", "Completed"]
        current_index = status_stages.index(order["status"]) if order["status"] in status_stages else 0
        progress = (current_index + 1) / len(status_stages)
        st.progress(progress, text=f"{order['status']}")

        with st.expander("🧾 View Your Order"):
            total = 0
            for item in order["cart"]:
                line = f"- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}"
                st.markdown(line)
                total += item['qty'] * item['price']
            st.markdown(f"**Total: ₹{total}**")

    # Auto-refresh after 5 seconds
    st.experimental_rerun()
    time.sleep(5)
