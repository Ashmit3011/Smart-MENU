import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="Smart Table Ordering", layout="centered")

# Load menu
menu_path = os.path.join(os.path.dirname(__file__), "menu.json")

if not os.path.exists(menu_path):
    st.error("menu.json not found!")
    st.stop()

with open(menu_path, "r", encoding="utf-8") as f:
    menu = json.load(f)

categories = sorted(set(item["category"] for item in menu if "category" in item))
if not categories:
    st.warning("⚠️ No categories found in menu. Please check your menu.json.")
    st.stop()

# UI
st.markdown("## 🍽️ Smart Table Ordering")
st.info("🎉 Get a Free Donut!\nOrder above ₹200 and enjoy a delicious free donut 🍩 with your meal!")

table_number = st.text_input("Enter Table Number")
if not table_number:
    st.stop()

# Cart
if "cart" not in st.session_state:
    st.session_state.cart = []

tabs = st.tabs(categories)
for idx, cat in enumerate(categories):
    with tabs[idx]:
        for item in [i for i in menu if i["category"] == cat]:
            col1, col2 = st.columns([3,1])
            with col1:
                st.markdown(f"**{item['name']}** - ₹{item['price']}")
            with col2:
                if st.button("Add", key=f"add_{item['id']}"):
                    st.session_state.cart.append(item)

# Cart display
st.markdown("## 🛒 Your Cart")
if not st.session_state.cart:
    st.info("Your cart is empty. Add items from the menu.")
else:
    total = sum(item["price"] for item in st.session_state.cart)
    for item in st.session_state.cart:
        st.write(f"- {item['name']} - ₹{item['price']}")
    st.success(f"**Total: ₹{total}**")

    if st.button("Place Order"):
        new_order = {
            "table": table_number,
            "items": st.session_state.cart,
            "total": total,
            "status": "Pending",
            "timestamp": datetime.now().isoformat()
        }
        if os.path.exists("orders.json"):
            with open("orders.json", "r") as f:
                orders = json.load(f)
        else:
            orders = []
        orders.append(new_order)
        with open("orders.json", "w") as f:
            json.dump(orders, f, indent=2)
        st.success("✅ Order Placed!")
        st.session_state.cart = []
