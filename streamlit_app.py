import streamlit as st
import datetime as dt
import pandas as pd

#メインメニュー消し
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

#タイトル
st.title("Hello your schedule")

#前期後期判別
month =dt.date.today().month
if month >= 4 and month <= 9:
    st.text("前期週間予定表")
else:
    st.text("後期週間予定表")


#日別予定カラム
times = ["1-2", "3-4", "5-6", "7-8"]
if "week" not in st.session_state:
    st.session_state.week = {
        "月曜日": ["", "", "", ""],
        "火曜日": ["", "", "", ""],
        "水曜日": ["", "", "", ""],
        "木曜日": ["", "", "", ""],
        "金曜日": ["", "", "", ""],
    }




#表書き出し
df = pd.DataFrame({
    "時間割":times,
    "月曜日":st.session_state.week["月曜日"],
    "火曜日":st.session_state.week["火曜日"],
    "水曜日":st.session_state.week["水曜日"],
    "木曜日":st.session_state.week["木曜日"],
    "金曜日":st.session_state.week["金曜日"]
})


html_table = df.to_html(index=False)

styled_html = f"""
<style>
table {{
    border-collapse: collapse;
    width: 100%;
    table-layout: fixed;#画面調整
}}

th, td {{
    border: 1px solid black;
    padding: 0.2em;
    text-align: center;
    vertical-align: middle;
    font-size: clamp(10px, 2.8vw, 14px);#文字調整
    word-wrap: break-word;
}}

th:first-child, td:first-child {{
    white-space: nowrap;
}}
</style>
{html_table}
"""

# 高さは余裕をもたせる（切れ防止）
st.components.v1.html(styled_html, height=380)

#授業変更
with st.form("add_schedule"):
    day = st.selectbox(
        "曜日",
        ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日"]
    )

    time = st.selectbox(
        "時間",
        ["1-2", "3-4", "5-6", "7-8"]
    )

    subject = st.text_input("授業名")

    submitted = st.form_submit_button("授業変更")
time_index = times.index(time)

if submitted:
    st.session_state.week[day][time_index] = subject
