import streamlit as st
import json
import os
import time
from datetime import datetime

MENU_FILE = "menu.json"
ORDER_FILE = "orders.json"

# --- Debug Info ---
st.write("📁 Current directory:", os.getcwd())
st.write("📄 Files in directory:", os.listdir())

# --- Helper Functions ---
def load_json(file):
    if not os.path.exists(file):
        st.error(f"{file} not found in current directory.")
        st.stop()
    with open(file, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            st.error(f"{file} is not valid JSON!")
            st.stop()

def save_json(file, data):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def generate_order_id():
    orders = load_json(ORDER_FILE) if os.path.exists(ORDER_FILE) else []
    return (max([o["id"] for o in orders], default=1000) + 1)

# --- Streamlit Config ---
st.set_page_config(page_title="Smart Table Ordering", layout="wide")

# --- Session State ---
if "cart" not in st.session_state:
    st.session_state.cart = []
if "table" not in st.session_state:
    st.session_state.table = ""
if "order_id" not in st.session_state:
    st.session_state.order_id = None
if "last_status" not in st.session_state:
    st.session_state.last_status = None

# --- Load Menu ---
menu = load_json(MENU_FILE)

if not menu:
    st.error("❌ menu.json is empty! Please add items to it.")
    st.stop()

# --- UI ---
st.title("🍽️ Smart Table Ordering")
st.info("🎉 Order above ₹200 and get a free donut 🍩!")

st.text_input("Enter Table Number", key="table")

# --- Menu Display ---
categories = sorted(set(item.get("category", "Uncategorized") for item in menu))
tabs = st.tabs(categories)

for index, category in enumerate(categories):
    with tabs[index]:
        st.subheader(f"{category}")
        for item in [m for m in menu if m.get("category") == category]:
            tags = ""
            if item.get("spicy"): tags += " 🌶️"
            if item.get("veg"): tags += " 🥦"
            if item.get("popular"): tags += " ⭐"

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

# --- Cart Display ---
st.markdown("## 🛒 Your Cart")
total = 0
if st.session_state.cart:
    for item in st.session_state.cart:
        st.write(f"- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")
        total += item['qty'] * item['price']

    st.markdown(f"**Total: ₹{total}**")

    if total >= 200:
        st.success("🎉 You get a free donut with your order!")

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
            orders = load_json(ORDER_FILE) if os.path.exists(ORDER_FILE) else []
            orders.append(new_order)
            save_json(ORDER_FILE, orders)
            st.session_state.order_id = new_order["id"]
            st.session_state.last_status = new_order["status"]
            st.success(f"Order placed! Table {new_order['table']} ✅")
            st.balloons()
            st.session_state.cart = []
            st.rerun()
else:
    st.info("Your cart is empty. Add items from the menu.")

# --- Order Tracker ---
if st.session_state.order_id:
    st.markdown("---")
    st.header("🔍 Track Your Order")

    orders = load_json(ORDER_FILE)
    order = next((o for o in orders if o["id"] == st.session_state.order_id), None)

    if order:
        current_status = order["status"]

        if st.session_state.last_status is None:
            st.session_state.last_status = current_status
        elif st.session_state.last_status != current_status:
            st.toast(f"🔔 Status changed to: {current_status}", icon="✅")
            st.session_state.last_status = current_status

        st.success(f"Order #{order['id']} | Table {order['table']}")
        st.markdown(f"**Status:** `{current_status}`")

        stages = ["Pending", "Preparing", "Served", "Completed"]
        idx = stages.index(current_status)
        st.progress((idx + 1) / len(stages), text=current_status)

        with st.expander("🧾 View Order"):
            total = 0
            for item in order["cart"]:
                st.markdown(f"- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")
                total += item['qty'] * item['price']
            st.markdown(f"**Total: ₹{total}**")

        time.sleep(10)
        st.rerun()
