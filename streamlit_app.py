import streamlit as st
import datetime as dt
import pandas as pd

st.title("Hello your schedule")
month = dt.date.today().month
year = dt.date.today().year

if month <= 4 or month >= 9:  # 修正：前期条件
    st.text("前期週間予定表")
else:
    st.text("後期週間予定表")

df = pd.DataFrame({
    "時間割":["1-2","3-4","5-6","7-8"],
    "月曜日":["","","キャリアデザイン3","英語"],
    "火曜日":["クラウドコンピューティング","クラウドコンピューティング","Linux実習2","Linux実習2"],
    "水曜日":["AIシステム開発","AIシステム開発","機械学習",""],
    "木曜日":["","","サーバーサイドプログラム2","サーバーサイドプログラム2"],
    "金曜日":["","ロジカルシンキング","サーバーサイドプログラム2","HR"]
})

# DataFrame を HTML に変換
html_table = df.to_html(index=False)

# CSS で文字中央揃え & インデックス非表示
styled_html = f"""
<style>
table {{
    border-collapse: collapse;
    width: 100%;
}}
th, td {{
    border: 1px solid black;
    padding: 8px;
    text-align: center;  /* 中央揃え */
    vertical-align: middle; /* 垂直方向も中央揃え */
}}
th:first-child, td:first-child {{
    white-space: nowrap;  /* 最初の列だけ改行禁止 */
}}
</style>
{html_table}
"""

st.components.v1.html(styled_html, height=400)
