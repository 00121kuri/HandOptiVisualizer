import streamlit as st

st.text("Hello World!")
if st.button("風船を飛ばす！", type="primary"):
    st.balloons()