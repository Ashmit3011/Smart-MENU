import streamlit as st

st.set_page_config(page_title="Smart Menu", layout="wide")

st.title("🍽️ Welcome to Smart Table Ordering")
st.markdown("Navigate to different sections:")

col1, col2 = st.columns(2)

with col1:
    st.page_link("pages/1_🍽️_Menu.py", label="🧾 View Menu & Order", icon="🍽️")

with col2:
    st.page_link("pages/2_🧾_Track_Order.py", label="🔍 Track Your Order", icon="🔍")
