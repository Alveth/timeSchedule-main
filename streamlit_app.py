import streamlit as st
import google.generativeai as genai
from PIL import Image
import datetime as dt1
import calendar as cl1

# --- StreamlitのUI設定 ---
st.set_page_config(page_title="月間カレンダーAI読み取り", layout="wide")

# メインメニュー等を隠す
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("📅 カレンダーAI読み取り＆生成 (年間対応)")

# --- アプリの「記憶力」をセットアップ ---
if "schedule_data" not in st.session_state:
    st.session_state.schedule_data = ""
if "display_year" not in st.session_state:
    st.session_state.display_year = dt1.date.today().year
if "display_month" not in st.session_state:
    st.session_state.display_month = dt1.date.today().month

# --- UI部分 ---
st.info("💡 画像内に年月の記載がない場合の「補完用」として基準年を設定してください。")
col1, col2 = st.columns(2)
with col1:
    current_year = dt1.date.today().year
    years = [current_year - 1, current_year, current_year + 1, current_year + 2]
    # もし画像に年がなかった場合に使う「保険」の年
    fallback_year = st.selectbox("基準年（画像に年がない場合の補完用）", years, index=1)

uploaded_file = st.file_uploader("予定表の画像をアップロード (PNG/JPG)", type=["png", "jpg", "jpeg"],accept_multiple_files=True)

# =========================================================
# Googleカレンダー用ICS作成ロジック
# =========================================================
def create_ics_file(schedule_text):
    ics_content = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//My Calendar App//JP\n"
    lines = schedule_text.strip().split('\n')
    for line in lines:
        if not line.strip(): continue
        parts = line.strip().split(' ', 1)
        if len(parts) == 2:
            date_str, title = parts
            try:
                dt = dt1.datetime.strptime(date_str, "%Y/%m/%d")
                dt_start = dt.strftime("%Y%m%d")
                dt_end = (dt + dt1.timedelta(days=1)).strftime("%Y%m%d")

                ics_content += "BEGIN:VEVENT\n"
                ics_content += f"SUMMARY:{title}\n"
                ics_content += f"DTSTART;VALUE=DATE:{dt_start}\n"
                ics_content += f"DTEND;VALUE=DATE:{dt_end}\n"
                ics_content += "END:VEVENT\n"
            except ValueError:
                continue
    ics_content += "END:VCALENDAR"
    return ics_content

# =========================================================
# カレンダーHTML生成ロジック
# =========================================================
def generate_calendar1(y1, m1): 
    cal1 = [""]*42 
    date1 = dt1.date(y1, m1, 1) 
    wd1 = date1.weekday() 
    if wd1 > 5: wd1 = wd1 - 7 
    wd1 = wd1 + 1 
    cal_max1 = cl1.monthrange(y1, m1)[1] 
    for i1 in range(cal_max1): 
        str1 = str(i1+1) 
        i2 = i1 + wd1 
        cal1[i2] = str1 
    return wd1, cal1 

def get_schedule1(y1, m1, cal1, wd1, str0): 
    cal2 = [""]*len(cal1) 
    a1 = str0.strip().split("\n") 
    for i1 in range(len(a1)): 
        if not a1[i1]: continue
        a2 = a1[i1].strip().split(" ")
        a3 = a2[0].split("/") 
        if len(a3) == 3: 
            y2 = a3[0] 
            m2 = a3[1] 
            if "*" in y2 or int(y2) == y1: 
                if "*" in m2 or int(m2) == m1: 
                    d1 = int(a3[2])
                    a4 = a2 
                    del a4[0] 
                    str1 = str(" ".join(a4)).strip() 
                    cal2[d1-1 + wd1] = cal2[d1-1 + wd1] + str1 + ""
    cal3 = [] 
    for i1 in range(len(cal1)): 
       cal3.append(cal1[i1]) 
       cal3.append(cal2[i1]) 
    return cal3 

def generate_html0(y1, m1, cal1): 
    m0 = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"] 
    str1 = '''
<style media="screen"> 
.header0 {{ height: 30px; line-height: 30px; text-align: left; font-size: 40px; padding: 10px; margin: 0; display: inline-block; font-weight: bold; }}
table {{ table-layout: fixed; width: 100%; }} 
th {{ text-align: center; padding: 0px; }} 
td {{ text-align: left; vertical-align: top; padding: 5px; height: 60px; }}
.calendar0 {{ background: #EEEEE8; }} 
.header1 {{ font-size: 13px; padding: 5px; }}
.calendar_table1 {{ height: 60%; padding: 5px; }}
.days1 {{ background: #FFFFFF; }}
.day1 {{ font-weight: bold; font-size: 14px; }} 
.content1 {{ border-radius: 3px; background: #f0e68c; font-size: 14px; font-family: 'Meiryo UI'; color: #000000; }} 
.w1 {{ color: #FF0000; background: #FFF0F0; }} 
.w7 {{ color: #0000A0; background: #F6F0FF; }}
</style> 
<div class="calendar0">
  <div class="calendar1">
    <table> 
      <tr> 
        <td><div class="header0">{_str01} </div>{_str02} {_str03}</td> 
      </tr> 
    </table> 
'''.format(_str01=m1, _str02=y1, _str03=m0[m1-1]).strip() 

    str2 = '''
    <table class="header1">
      <tr><th>Sunday</th><th>Monday</th><th>Tuesday</th><th>Wednesday</th><th>Thursday</th><th>Friday</th><th>Saturday</th></tr>
    </table> 
    <table class="calendar_table1">
      <tr class="days1">
        <td class = w1><div class=day1>{0[0]}</div><br><div class=content1>{0[1]}</div></td>
        <td class = w2><div class=day1>{0[2]}</div><br><div class=content1>{0[3]}</div></td>
        <td class = w3><div class=day1>{0[4]}</div><br><div class=content1>{0[5]}</div></td>
        <td class = w4><div class=day1>{0[6]}</div><br><div class=content1>{0[7]}</div></td>
        <td class = w5><div class=day1>{0[8]}</div><br><div class=content1>{0[9]}</div></td>
        <td class = w6><div class=day1>{0[10]}</div><br><div class=content1>{0[11]}</div></td>
        <td class = w7><div class=day1>{0[12]}</div><br><div class=content1>{0[13]}</div></td>
      </tr>
      <tr class="days1">
        <td class = w1><div class=day1>{0[14]}</div><br><div class=content1>{0[15]}</div></td>
        <td class = w2><div class=day1>{0[16]}</div><br><div class=content1>{0[17]}</div></td>
        <td class = w3><div class=day1>{0[18]}</div><br><div class=content1>{0[19]}</div></td>
        <td class = w4><div class=day1>{0[20]}</div><br><div class=content1>{0[21]}</div></td>
        <td class = w5><div class=day1>{0[22]}</div><br><div class=content1>{0[23]}</div></td>
        <td class = w6><div class=day1>{0[24]}</div><br><div class=content1>{0[25]}</div></td>
        <td class = w7><div class=day1>{0[26]}</div><br><div class=content1>{0[27]}</div></td>
      </tr>
      <tr class="days1">
        <td class = w1><div class=day1>{0[28]}</div><br><div class=content1>{0[29]}</div></td>
        <td class = w2><div class=day1>{0[30]}</div><br><div class=content1>{0[31]}</div></td>
        <td class = w3><div class=day1>{0[32]}</div><br><div class=content1>{0[33]}</div></td>
        <td class = w4><div class=day1>{0[34]}</div><br><div class=content1>{0[35]}</div></td>
        <td class = w5><div class=day1>{0[36]}</div><br><div class=content1>{0[37]}</div></td>
        <td class = w6><div class=day1>{0[38]}</div><br><div class=content1>{0[39]}</div></td>
        <td class = w7><div class=day1>{0[40]}</div><br><div class=content1>{0[41]}</div></td>
      </tr>
      <tr class="days1">
        <td class = w1><div class=day1>{0[42]}</div><br><div class=content1>{0[43]}</div></td>
        <td class = w2><div class=day1>{0[44]}</div><br><div class=content1>{0[45]}</div></td>
        <td class = w3><div class=day1>{0[46]}</div><br><div class=content1>{0[47]}</div></td>
        <td class = w4><div class=day1>{0[48]}</div><br><div class=content1>{0[49]}</div></td>
        <td class = w5><div class=day1>{0[50]}</div><br><div class=content1>{0[51]}</div></td>
        <td class = w6><div class=day1>{0[52]}</div><br><div class=content1>{0[53]}</div></td>
        <td class = w7><div class=day1>{0[54]}</div><br><div class=content1>{0[55]}</div></td>
      </tr>
      <tr class="days1">
        <td class = w1><div class=day1>{0[56]}</div><br><div class=content1>{0[57]}</div></td>
        <td class = w2><div class=day1>{0[58]}</div><br><div class=content1>{0[59]}</div></td>
        <td class = w3><div class=day1>{0[60]}</div><br><div class=content1>{0[61]}</div></td>
        <td class = w4><div class=day1>{0[62]}</div><br><div class=content1>{0[63]}</div></td>
        <td class = w5><div class=day1>{0[64]}</div><br><div class=content1>{0[65]}</div></td>
        <td class = w6><div class=day1>{0[66]}</div><br><div class=content1>{0[67]}</div></td>
        <td class = w7><div class=day1>{0[68]}</div><br><div class=content1>{0[69]}</div></td>
      </tr>
      <tr class="days1">
        <td class = w1><div class=day1>{0[70]}</div><br><div class=content1>{0[71]}</div></td>
        <td class = w2><div class=day1>{0[72]}</div><br><div class=content1>{0[73]}</div></td>
        <td class = w3><div class=day1>{0[74]}</div><br><div class=content1>{0[75]}</div></td>
        <td class = w4><div class=day1>{0[76]}</div><br><div class=content1>{0[77]}</div></td>
        <td class = w5><div class=day1>{0[78]}</div><br><div class=content1>{0[79]}</div></td>
        <td class = w6><div class=day1>{0[80]}</div><br><div class=content1>{0[81]}</div></td>
        <td class = w7><div class=day1>{0[82]}</div><br><div class=content1>{0[83]}</div></td>
      </tr>
    </table>
  </div>
</div>
'''.format(cal1).strip() 
    return str1 + str2 

def generate_html1(y1, m1, str0): 
    wd1, cal1 = generate_calendar1(y1, m1) 
    cal2 = get_schedule1(y1, m1, cal1, wd1, str0) 
    return generate_html0(y1, m1, cal2) 

# =========================================================
# AI解析＆実行処理
# =========================================================
if st.button("AIで解析してカレンダーを作成", use_container_width=True):
    if uploaded_file is None:
        st.error("画像をアップロードしてください。")
    else:
        with st.spinner("AIが予定表を読み取っています（年間対応）..."):
            try:
                genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
                model = genai.GenerativeModel('gemini-3.5-flash')
                
                img = Image.open(uploaded_file)
                
                # AIへの指示を強化（画像内の情報を最優先させる）
                prompt = f"""
                これは予定表（またはカレンダー）の画像です。
                画像からすべての日付と予定を抽出し、以下のフォーマットで出力してください。
                
                【出力フォーマット】
                YYYY/MM/DD 予定の内容
                
                【年月特定のルール（重要）】
                1. 画像内に「年」や「月」の記載（令和〇年なども含む）がある場合は、必ずその情報を最優先して日付を特定し、西暦に変換してください。
                2. もし画像内に「年」が一切書かれていない場合のみ、基準年である {fallback_year} 年の出来事として推測して補完してください。
                
                【その他のルール】
                ・予定がない日は出力しないでください。
                ・Markdown記号(```など)や挨拶文は一切含めないでください。
                ・必ず「年/月/日 半角スペース 予定」の形式を守ってください。
                ・複数月が含まれる場合はすべての月を抽出してください。
                """
                
                response = model.generate_content([prompt, img])
                extracted_text = response.text.strip()
                st.session_state.schedule_data = extracted_text
                
                # --- AIが抽出したデータから、自動で最初の月を見つけて画面にセットする ---
                first_found_year = fallback_year
                first_found_month = dt1.date.today().month # デフォルトは現在の月
                
                for line in extracted_text.split('\n'):
                    parts = line.strip().split(' ', 1)
                    if len(parts) >= 1:
                        try:
                            # 抽出テキストから最初の YYYY/MM/DD を解析
                            dt = dt1.datetime.strptime(parts[0], "%Y/%m/%d")
                            first_found_year = dt.year
                            first_found_month = dt.month
                            break # 最初の1件が見つかったら終了
                        except ValueError:
                            continue
                
                st.session_state.display_year = first_found_year
                st.session_state.display_month = first_found_month
                
                st.success("解析成功！カレンダーを生成しました。")
                
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

# =========================================================
# カレンダー表示 ＆ 月移動ナビゲーション
# =========================================================
if st.session_state.schedule_data:
    st.markdown("---")
    
    with st.expander("AIが読み取った予定データ（生テキスト）を見る"):
         st.text(st.session_state.schedule_data)
    
    col_prev, col_title, col_next = st.columns([1, 2, 1])
    
    with col_prev:
        if st.button("⬅️ 先月", use_container_width=True):
            st.session_state.display_month -= 1
            if st.session_state.display_month < 1:
                st.session_state.display_month = 12
                st.session_state.display_year -= 1
            st.rerun()
            
    with col_title:
        st.markdown(f"<h3 style='text-align: center;'>{st.session_state.display_year}年 {st.session_state.display_month}月</h3>", unsafe_allow_html=True)
        
    with col_next:
        if st.button("翌月 ➡️", use_container_width=True):
            st.session_state.display_month += 1
            if st.session_state.display_month > 12:
                st.session_state.display_month = 1
                st.session_state.display_year += 1
            st.rerun()

    final_html = generate_html1(
        st.session_state.display_year, 
        st.session_state.display_month, 
        st.session_state.schedule_data
    )
    
    st.components.v1.html(final_html, height=700, scrolling=True)
    
    st.markdown("### 連携オプション")
    ics_data = create_ics_file(st.session_state.schedule_data)
    
    st.download_button(
        label="🗓 読み取った全予定をGoogleカレンダー用ファイルでダウンロード (.ics)",
        data=ics_data,
        file_name=f"schedule_all.ics",
        mime="text/calendar",
        use_container_width=True
    )
    st.caption("※ダウンロードしたファイルを、Googleカレンダーの設定 ＞「インポート/エクスポート」から読み込んでください。")
