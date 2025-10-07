import streamlit as st
import datetime as dt

st.title("Hello your schedule")
month = dt.date.today().month
year = dt.date.today().year

if month <= 4 and month >= 9:
    st.text("前期週間予定表")
else:
    st.text("後期週間予定表")
