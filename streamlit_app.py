import streamlit as st
import google.generativeai as genai
from PIL import Image
import datetime as dt1
import calendar as cl1

# --- Google Calendar API 用のインポート ---
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Googleカレンダーへのフルアクセス権限
SCOPES = ['https://www.googleapis.com/auth/calendar']

# --- StreamlitのUI初期設定 ---
st.set_page_config(page_title="Googleカレンダー連携 ＆ AI読み取り", layout="wide")

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("📅 Googleカレンダー連携 ＆ AI読み取り")

# ステート管理（表示年月・直前追加イベント履歴）
if "display_year" not in st.session_state:
    st.session_state.display_year = dt1.date.today().year
if "display_month" not in st.session_state:
    st.session_state.display_month = dt1.date.today().month
if "last_added_events" not in st.session_state:
    st.session_state.last_added_events = []  # 直前に写真から追加されたイベント情報の保持用


# =========================================================
# 順序1：API取得（Streamlit Secretsを使用したクラウド認証）
# =========================================================
def get_calendar_service():
    """Streamlit Secrets から Google Calendar API 認証情報を読み込む"""
    if "google_oauth" not in st.secrets:
        st.error("Streamlit の Secrets に [google_oauth] が設定されていません。")
        st.stop()
        
    oauth_info = dict(st.secrets["google_oauth"])
    creds = Credentials.from_authorized_user_info(oauth_info, SCOPES)
    
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        
    return build('calendar', 'v3', credentials=creds)

try:
    cal_service = get_calendar_service()
except Exception as e:
    st.error(f"Googleカレンダーの認証に失敗しました: {e}")
    st.stop()


# --- Googleカレンダー操作用ユーティリティ関数 ---
def fetch_events(service, year, month):
    """Googleカレンダーから指定年月の予定を取得"""
    start_time = dt1.datetime(year, month, 1).isoformat() + 'Z'
    end_day = cl1.monthrange(year, month)[1]
    end_time = dt1.datetime(year, month, end_day, 23, 59, 59).isoformat() + 'Z'
    
    events_result = service.events().list(
        calendarId='primary', timeMin=start_time, timeMax=end_time,
        singleEvents=True, orderBy='startTime').execute()
    
    events = events_result.get('items', [])
    parsed_events = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        date_str = start[:10].replace("-", "/") 
        parsed_events.append({
            'id': event['id'],
            'date': date_str,
            'summary': event.get('summary', '(タイトルなし)')
        })
    return parsed_events

def add_calendar_event(service, date_str, summary):
    """Googleカレンダーに予定を追加し、追加されたイベントIDを返す"""
    dt = dt1.datetime.strptime(date_str, "%Y/%m/%d")
    event = {
        'summary': summary,
        'start': {'date': dt.strftime("%Y-%m-%d")},
        'end': {'date': (dt + dt1.timedelta(days=1)).strftime("%Y-%m-%d")},
    }
    created_event = service.events().insert(calendarId='primary', body=event).execute()
    return created_event.get('id')

def update_calendar_event(service, event_id, date_str, summary):
    """Googleカレンダーの予定を変更"""
    dt = dt1.datetime.strptime(date_str, "%Y/%m/%d")
    event = service.events().get(calendarId='primary', eventId=event_id).execute()
    event['summary'] = summary
    event['start'] = {'date': dt.strftime("%Y-%m-%d")}
    event['end'] = {'date': (dt + dt1.timedelta(days=1)).strftime("%Y-%m-%d")}
    service.events().update(calendarId='primary', eventId=event_id, body=event).execute()

def delete_calendar_event(service, event_id):
    """Googleカレンダーの予定を削除"""
    service.events().delete(calendarId='primary', eventId=event_id).execute()


# --- カレンダーHTML表示関数 ---
def generate_calendar1(y1, m1): 
    cal1 = [""]*42 
    date1 = dt1.date(y1, m1, 1) 
    wd1 = date1.weekday() 
    if wd1 > 5: wd1 = wd1 - 7 
    wd1 = wd1 + 1 
    cal_max1 = cl1.monthrange(y1, m1)[1] 
    for i1 in range(cal_max1): 
        cal1[i1 + wd1] = str(i1+1) 
    return wd1, cal1 

def get_schedule_from_events(y1, m1, cal1, wd1, events_list): 
    cal2 = [""]*len(cal1) 
    for ev in events_list:
        date_parts = ev['date'].split('/')
        if len(date_parts) == 3:
            ey, em, ed = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
            if ey == y1 and em == m1:
                cal2[ed-1 + wd1] += ev['summary'] + "<br>"
                
    cal3 = [] 
    for i1 in range(len(cal1)): 
       cal3.append(cal1[i1]) 
       cal3.append(cal2[i1]) 
    return cal3 

def generate_html0(y1, m1, cal1): 
    m0 = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"] 
    str1 = f'''
<style media="screen"> 
.header0 {{ height: 30px; line-height: 30px; text-align: left; font-size: 40px; padding: 10px; margin: 0; display: inline-block; font-weight: bold; }}
table {{ table-layout: fixed; width: 100%; }} 
th {{ text-align: center; padding: 0px; }} 
td {{ text-align: left; vertical-align: top; padding: 5px; height: 75px; }}
.calendar0 {{ background: #EEEEE8; }} 
.header1 {{ font-size: 13px; padding: 5px; }}
.calendar_table1 {{ height: 60%; padding: 5px; }}
.days1 {{ background: #FFFFFF; }}
.day1 {{ font-weight: bold; font-size: 14px; }} 
.content1 {{ border-radius: 3px; background: #f0e68c; font-size: 12px; font-family: 'Meiryo UI'; color: #000000; padding: 2px; }} 
.w1 {{ color: #FF0000; background: #FFF0F0; }} 
.w7 {{ color: #0000A0; background: #F6F0FF; }}
</style> 
<div class="calendar0">
  <div class="calendar1">
    <table><tr><td><div class="header0">{m1} </div>{y1} {m0[m1-1]}</td></tr></table> 
'''
    str2 = '''
    <table class="header1">
      <tr><th>Sun</th><th>Mon</th><th>Tue</th><th>Wed</th><th>Thu</th><th>Fri</th><th>Sat</th></tr>
    </table> 
    <table class="calendar_table1">
    '''
    for week in range(6):
        str2 += '<tr class="days1">'
        for day in range(7):
            idx = (week * 7 + day) * 2
            css_class = "w1" if day == 0 else "w7" if day == 6 else ""
            str2 += f'<td class="{css_class}"><div class="day1">{cal1[idx]}</div><br><div class="content1">{cal1[idx+1]}</div></td>'
        str2 += '</tr>'
    str2 += '</table></div></div>'
    return str1 + str2 


# =========================================================
# 順序2：Google Calendarから予定取得
# =========================================================
events_data = fetch_events(cal_service, st.session_state.display_year, st.session_state.display_month)


# =========================================================
# 順序3：表示（Googleカレンダーの同期表示）
# =========================================================
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

# カレンダーHTML描画
wd1, cal1_template = generate_calendar1(st.session_state.display_year, st.session_state.display_month) 
cal_data = get_schedule_from_events(st.session_state.display_year, st.session_state.display_month, cal1_template, wd1, events_data) 
final_html = generate_html0(st.session_state.display_year, st.session_state.display_month, cal_data)

st.components.v1.html(final_html, height=650, scrolling=True)


# =========================================================
# 順序4：写真から読み込む ＆ 取り消し（Undo）機能
# =========================================================
st.markdown("---")
st.markdown("### 📷 写真から予定を読み込んで追加")

# --- 直前に写真から取り込んだ予定を取り消すボタン（データがある場合のみ表示） ---
if st.session_state.last_added_events:
    event_count = len(st.session_state.last_added_events)
    st.info(f"💡 直前に写真から {event_count} 件の予定を追加しました。")
    if st.button(f"↩️ 直前に写真から追加した {event_count} 件の予定を取り消す", type="primary", use_container_width=True):
        with st.spinner("追加した予定を取り消し中..."):
            for ev in st.session_state.last_added_events:
                try:
                    delete_calendar_event(cal_service, ev['id'])
                except Exception as e:
                    pass
            # 履歴のクリア
            st.session_state.last_added_events = []
            st.success("写真から追加した予定を取り消しました。")
            st.rerun()

col1, col2 = st.columns([1, 2])
with col1:
    current_year = dt1.date.today().year
    years = [current_year - 1, current_year, current_year + 1, current_year + 2]
    fallback_year = st.selectbox("基準年（画像に年がない場合の補完用）", years, index=1)

uploaded_file = st.file_uploader("予定表の画像をアップロード (PNG/JPG)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if st.button("📸 写真から予定を読み込んで登録", use_container_width=True):
    if not uploaded_file:
        st.error("画像をアップロードしてください。")
    else:
        with st.spinner("AIが予定表を読み取り、Googleカレンダーに登録中..."):
            try:
                genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
                model = genai.GenerativeModel('gemini-3.5-flash')
                images = [Image.open(f) for f in uploaded_file]
                
                prompt = f"""
                これは予定表（またはカレンダー）の画像です。画像からすべての日付と予定を抽出し、以下のフォーマットで出力してください。
                【出力フォーマット】
                YYYY/MM/DD 予定の内容
                【ルール】
                1. 「年」が一切書かれていない場合は、基準年 {fallback_year} 年として補完してください。
                2. Markdown記号や挨拶文は一切含めず、「年/月/日 半角スペース 予定」の形式のみ出力してください。
                """
                request_data = [prompt] + images
                response = model.generate_content(request_data)
                
                extracted_text = response.text.strip()
                
                # 新しい追加結果の保持リストを初期化
                new_added_events = []
                first_date = None
                
                for line in extracted_text.split('\n'):
                    parts = line.strip().split(' ', 1)
                    if len(parts) == 2:
                        try:
                            dt = dt1.datetime.strptime(parts[0], "%Y/%m/%d")
                            # イベントを追加し、生成されたIDを取得
                            event_id = add_calendar_event(cal_service, parts[0], parts[1])
                            new_added_events.append({
                                'id': event_id,
                                'date': parts[0],
                                'summary': parts[1]
                            })
                            if not first_date:
                                first_date = dt
                        except ValueError:
                            continue
                
                # 直前追加リストを更新
                st.session_state.last_added_events = new_added_events

                if first_date:
                    st.session_state.display_year = first_date.year
                    st.session_state.display_month = first_date.month

                st.success(f"{len(new_added_events)} 件の予定を登録しました！間違えた場合は下の『取り消す』ボタンで元に戻せます。")
                st.rerun()
                
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")


# =========================================================
# 追加要件：予定の個別追加・変更・削除
# =========================================================
st.markdown("---")
st.markdown("### 📝 予定の個別管理 (追加・変更・削除)")

col_add, col_edit = st.columns(2)

# --- 個別追加 ---
with col_add:
    st.markdown("#### 新規追加")
    new_date = st.date_input("日付", dt1.date.today())
    new_summary = st.text_input("予定のタイトル")
    if st.button("追加する"):
        if new_summary:
            add_calendar_event(cal_service, new_date.strftime("%Y/%m/%d"), new_summary)
            st.success("予定を追加しました。")
            st.rerun()
        else:
            st.warning("タイトルを入力してください。")

# --- 変更・削除 ---
with col_edit:
    st.markdown(f"#### 編集・削除 ({st.session_state.display_month}月の予定)")
    if events_data:
        event_options = {f"{ev['date']} - {ev['summary']}": ev for ev in events_data}
        selected_event_label = st.selectbox("操作する予定を選択", list(event_options.keys()))
        selected_event = event_options[selected_event_label]
        
        edit_date = st.text_input("日付を変更 (YYYY/MM/DD)", value=selected_event['date'])
        edit_summary = st.text_input("タイトルを変更", value=selected_event['summary'])
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("更新する"):
                update_calendar_event(cal_service, selected_event['id'], edit_date, edit_summary)
                st.success("予定を更新しました。")
                st.rerun()
        with c2:
            if st.button("削除する", type="primary"):
                delete_calendar_event(cal_service, selected_event['id'])
                st.success("予定を削除しました。")
                st.rerun()
    else:
        st.info("この月に予定はありません。")