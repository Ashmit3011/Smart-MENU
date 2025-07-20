import streamlit as st
st.set_page_config(page_title="Page Title", layout="wide", initial_sidebar_state="collapsed")
import json
import os
from datetime import datetime
import time

ORDER_FILE = "orders.json"

def load_json(file):
    if not os.path.exists(file):
        return []
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

st.set_page_config(page_title="Track Your Order", layout="wide")

st.title("🔍 Track Your Order")

order_id = st.number_input("Enter Your Order ID", min_value=1001, step=1, format="%d")

if st.button("Check Status"):
    orders = load_json(ORDER_FILE)
    order = next((o for o in orders if o["id"] == order_id), None)

    if order:
        st.success(f"Order #{order['id']} for Table {order['table']}")
        current_status = order["status"]
        st.markdown(f"**Status:** `{current_status}`")

        status_stages = ["Pending", "Preparing", "Served", "Completed"]
        progress = (status_stages.index(current_status)+1) / len(status_stages)
        st.progress(progress, text=current_status)

        with st.expander("🧾 View Your Order"):
            total = 0
            for item in order["cart"]:
                st.markdown(f"- {item['name']} x {item['qty']} = ₹{item['qty'] * item['price']}")
                total += item['qty'] * item['price']
            st.markdown(f"**Total: ₹{total}**")
    else:
        st.error("Order not found. Please check your ID.")
