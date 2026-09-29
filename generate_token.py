from google_auth_oauthlib.flow import InstalledAppFlow
import os
import urllib.parse

SCOPES = ['https://www.googleapis.com/auth/calendar']

if not os.path.exists('credentials.json'):
    print("❌ エラー: credentials.json が見つかりません。")
else:
    # redirect_uri を http://localhost に固定
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json',
        scopes=SCOPES,
        redirect_uri='http://localhost'
    )

    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')

    print("\n" + "="*60)
    print("1. 以下のURLをコピーしてブラウザで開き、Googleログイン・許可をしてください：\n")
    print(auth_url)
    print("\n2. 許可後、ブラウザで「このサイトにアクセスできません」と表示されたら、")
    print("   その画面のアドレスバー（URL）全体をコピーして、下に貼り付けてEnterを押してください。")
    print("="*60 + "\n")

    url_input = input("貼り付け用URL (または code): ").strip()

    # URL全体から code の値を自動抽出
    code = url_input
    if "code=" in url_input:
        parsed_url = urllib.parse.urlparse(url_input)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        if 'code' in query_params:
            code = query_params['code'][0]

    try:
        flow.fetch_token(code=code)
        creds = flow.credentials

        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        print("\n🎉 成功！ token.json が生成されました！")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")