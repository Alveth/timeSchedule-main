import streamlit as st
import datetime as dt
import pandas as pd

st.title("Hello your schedule")
month = dt.date.today().month
year = dt.date.today().year

if month <= 4 and month >= 9:
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
st.dataframe(df,hide_index=True,width=1000)

