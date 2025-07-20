import streamlit as st
import json
import os

st.set_page_config(page_title="Admin Panel", layout="centered")
st.title("🛠️ Admin Panel")

if not os.path.exists("orders.json"):
    st.info("No orders found.")
    st.stop()

with open("orders.json", "r") as f:
    orders = json.load(f)

status_options = ["Pending", "Preparing", "Ready", "Served"]

for i, order in enumerate(orders):
    with st.expander(f"Order {i+1} - Table {order['table']} - ₹{order['total']}"):
        st.write("Status:", order["status"])
        st.write("Items:", ", ".join(item["name"] for item in order["items"]))
        new_status = st.selectbox("Update Status", status_options, index=status_options.index(order["status"]), key=f"status_{i}")
        if new_status != order["status"]:
            order["status"] = new_status

# Save any updates
with open("orders.json", "w") as f:
    json.dump(orders, f, indent=2)
