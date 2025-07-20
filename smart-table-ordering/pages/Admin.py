import streamlit as st
import json
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

ORDER_FILE = "orders.json"
MENU_FILE = "menu.json"
PREV_COUNT_FILE = "prev_order_count.json"

# --- Load/Save Helpers ---
def load_json(file):
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump([], f)
    with open(file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(file, data):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def dashboard_stats(orders):
    return {
        "Total": len(orders),
        "Pending": sum(1 for o in orders if o.get("status") == "Pending"),
        "Preparing": sum(1 for o in orders if o.get("status") == "Preparing"),
        "Served": sum(1 for o in orders if o.get("status") == "Served"),
        "Completed": sum(1 for o in orders if o.get("status") == "Completed")
    }

# --- UI ---
st.set_page_config(page_title="Admin Dashboard", layout="wide")
st.title("🧑‍🍳 Admin Dashboard")

# --- Login ---
with st.sidebar:
    st.header("🔐 Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

if username == "admin" and password == "admin123":
    st_autorefresh(interval=10 * 1000, key="refresh")

    orders_raw = load_json(ORDER_FILE)
    orders = [o for o in orders_raw if isinstance(o, dict) and "id" in o and "status" in o]
    if len(orders) != len(orders_raw):
        save_json(ORDER_FILE, orders)

    menu = load_json(MENU_FILE)

    # 🔔 New Order Notification
    prev_count = 0
    if os.path.exists(PREV_COUNT_FILE):
        with open(PREV_COUNT_FILE, 'r') as f:
            prev_count = json.load(f).get("count", 0)
    current_count = len(orders)
    if current_count > prev_count:
        st.toast(f"🍽️ New order received! Total orders: {current_count}")
        st.audio("https://www.soundjay.com/buttons/sounds/button-3.mp3", format='audio/mp3', autoplay=True)
        with open(PREV_COUNT_FILE, 'w') as f:
            json.dump({"count": current_count}, f)

    # 📊 Order Stats
    stats = dashboard_stats(orders)
    st.subheader("📊 Order Summary")
    cols = st.columns(len(stats))
    for i, (label, count) in enumerate(stats.items()):
        with cols[i]:
            st.metric(label, count)

    # Categorized Order Display
    st.divider()
    for status in ["Pending", "Preparing", "Served"]:
        section_orders = [o for o in orders if o["status"] == status]
        if section_orders:
            st.markdown(f"### 🧾 {status} Orders")
            for order in section_orders:
                with st.expander(f"🪑 Table {order['table']} - Order #{order['id']} [{order['status']}]"):
                    for item in order["cart"]:
                        st.markdown(f"- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")
                    st.markdown(f"**Ordered at:** {order['timestamp']}")
                    new_status = st.selectbox(
                        "Update Status",
                        ["Pending", "Preparing", "Served", "Completed"],
                        index=["Pending", "Preparing", "Served", "Completed"].index(order["status"]),
                        key=f"status_{order['id']}"
                    )
                    if new_status != order["status"]:
                        order["status"] = new_status
                        save_json(ORDER_FILE, orders)
                        st.success(f"✅ Order #{order['id']} updated to {new_status}")
                        st.rerun()

    # Completed Orders
    completed = [o for o in orders if o["status"] == "Completed"]
    if completed:
        st.divider()
        st.markdown("### ✅ Completed Orders")
        for order in completed:
            with st.expander(f"🧾 Order #{order['id']} - Table {order['table']}"):
                total = 0
                for item in order["cart"]:
                    st.markdown(f"- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")
                    total += item['qty'] * item['price']
                st.markdown(f"**Total: ₹{total}**")
                st.caption(f"Ordered at {order['timestamp']}")

        if st.button("🗑 Clear Completed Orders"):
            orders = [o for o in orders if o["status"] != "Completed"]
            save_json(ORDER_FILE, orders)
            st.success("✅ Completed orders cleared!")
            st.rerun()

else:
    st.warning("Please log in to view the admin panel.")
