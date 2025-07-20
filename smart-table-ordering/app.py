import streamlit as st
import json
import os
from datetime import datetime
import time

# --- File Paths ---
MENU_FILE = "menu.json"
ORDER_FILE = "orders.json"

# --- Helper Functions ---
def load_json(file):
    if not os.path.exists(file):
        return []
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def generate_order_id():
    orders = load_json(ORDER_FILE)
    return (max([o["id"] for o in orders], default=1000) + 1)

# --- Initialize Session State ---
if "cart" not in st.session_state:
    st.session_state.cart = []
if "table" not in st.session_state:
    st.session_state.table = ""
if "order_id" not in st.session_state:
    st.session_state.order_id = None
if "last_status" not in st.session_state:
    st.session_state.last_status = None

# --- Page Config ---
st.set_page_config(page_title="Smart Table Ordering", layout="wide")

# --- Load Menu ---
menu = load_json(MENU_FILE)

if not menu:
    st.error("Menu is empty or menu.json is missing!")
    st.stop()

# --- UI Header ---
st.title("🍽️ Smart Table Ordering")
st.info("🎉 Order above ₹200 and get a free donut 🍩!")

st.text_input("Enter Table Number", key="table")

# --- Menu by Category ---
categories = sorted(set(item.get("category", "Uncategorized") for item in menu))
tabs = st.tabs(categories)

for i, category in enumerate(categories):
    with tabs[i]:
        st.subheader(category)
        for item in [m for m in menu if m.get("category") == category]:
            tags = ""
            if item.get("spicy"): tags += " 🌶️"
            if item.get("veg"): tags += " 🥦"
            if item.get("popular"): tags += " ⭐"

            st.markdown(f"**{item['name']}** {tags}")
            st.caption(f"₹{item['price']}")
            qty = st.number_input(f"Qty - {item['name']}", min_value=0, step=1, key=f"qty_{item['id']}")
            if qty > 0:
                existing = next((x for x in st.session_state.cart if x["id"] == item["id"]), None)
                if existing:
                    existing["qty"] = qty
                else:
                    st.session_state.cart.append({
                        "id": item["id"],
                        "name": item["name"],
                        "price": item["price"],
                        "qty": qty
                    })

# --- Cart Section ---
st.markdown("---")
st.header("🛒 Your Cart")

total = 0
if st.session_state.cart:
    for item in st.session_state.cart:
        line = f"- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}"
        st.markdown(line)
        total += item['qty'] * item['price']
    st.markdown(f"**Total: ₹{total}**")

    if total >= 200:
        st.success("🎉 You get a free donut!")

    if st.button("✅ Place Order"):
        if not st.session_state.table.strip():
            st.error("Please enter your table number.")
        else:
            order = {
                "id": generate_order_id(),
                "table": st.session_state.table.strip(),
                "cart": st.session_state.cart,
                "status": "Pending",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            orders = load_json(ORDER_FILE)
            orders.append(order)
            save_json(ORDER_FILE, orders)

            st.success(f"🎉 Order placed! Table: {order['table']}")
            st.session_state.order_id = order["id"]
            st.session_state.last_status = order["status"]
            st.session_state.cart = []
            st.balloons()
            st.rerun()
else:
    st.info("Your cart is empty. Add items to continue.")

# --- Track Order Section ---
if st.session_state.order_id:
    st.markdown("---")
    st.header("📦 Track Your Order")

    orders = load_json(ORDER_FILE)
    order = next((o for o in orders if o["id"] == st.session_state.order_id), None)

    if order:
        current_status = order["status"]
        if st.session_state.last_status != current_status:
            st.toast(f"🔔 Status changed to: {current_status}")
            st.session_state.last_status = current_status

        st.success(f"Order #{order['id']} | Table {order['table']}")
        st.markdown(f"**Status:** `{current_status}`")

        steps = ["Pending", "Preparing", "Served", "Completed"]
        progress = (steps.index(current_status) + 1) / len(steps)
        st.progress(progress, text=current_status)

        with st.expander("🧾 View Order Details"):
            total = 0
            for item in order["cart"]:
                st.markdown(f"- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")
                total += item["qty"] * item["price"]
            st.markdown(f"**Total: ₹{total}**")

        time.sleep(10)
        st.rerun()
