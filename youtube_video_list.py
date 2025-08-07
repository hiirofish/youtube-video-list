import os
import pickle
import csv
import re
from collections import defaultdict
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# --- 設定項目：あなたのチャンネルIDをここに入力してください ---
# --- チャンネルIDをファイルから読み込む ---
CHANNEL_ID_FILE = "channel_id.txt"

try:
    with open(CHANNEL_ID_FILE, 'r', encoding='utf-8') as f:
        # 前後の空白や改行を削除
        CHANNEL_ID = f.read().strip()
    if not CHANNEL_ID:
        print(f"エラー: {CHANNEL_ID_FILE} が空です。チャンネルIDを記述してください。")
        exit()
except FileNotFoundError:
    print(f"エラー: {CHANNEL_ID_FILE} が見つかりません。")
    print("ファイルを作成し、中にご自身のYouTubeチャンネルIDを一行記述してください。")
    exit()
# ----------------------------------------------------


CLIENT_SECRETS_FILE = "client.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
TOKEN_FILE = "token.json"
OUTPUT_CSV_FILE = "youtube_master_list.csv"

def get_authenticated_service():
    """OAuth 2.0認証を行い、YouTube APIサービスオブジェクトを返す"""
    creds = None
    # token.json ファイルが存在すれば、そこから認証情報を読み込む
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    # 認証情報がない、または無効な場合
    if not creds or not creds.valid:
        # 期限切れでリフレッシュトークンがある場合はリフレッシュ
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # 新規に認証フローを開始
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            #creds = flow.run_local_server(port=0, open_browser=False)
            creds = flow.run_local_server()
        # 認証情報をtoken.jsonに保存
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    return build(API_SERVICE_NAME, API_VERSION, credentials=creds)

def parse_duration(duration_str):
    """ISO 8601形式の動画時間を hh:mm:ss 形式の文字列に変換する"""
    if not duration_str:
        return "00:00"
    
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
    if not match:
        return "00:00"
    
    hours, minutes, seconds = match.groups(default='0')
    if int(hours) > 0:
        return f"{int(hours)}:{int(minutes):02d}:{int(seconds):02d}"
    return f"{int(minutes):02d}:{int(seconds):02d}"

def get_channel_playlists(youtube, channel_id):
    """チャンネルのすべての再生リストを取得する"""
    playlists = {}
    request = youtube.playlists().list(
        part="snippet",
        channelId=channel_id,
        maxResults=50
    )
    while request:
        response = request.execute()
        for item in response["items"]:
            playlists[item["id"]] = item["snippet"]["title"]
        request = youtube.playlists().list_next(request, response)
    print(f"{len(playlists)} 件の再生リストを取得しました。")
    return playlists

def get_video_to_playlist_map(youtube, playlists):
    """どの動画がどの再生リストに属しているかの対応表を作成する"""
    video_map = defaultdict(list)
    for playlist_id, playlist_title in playlists.items():
        print(f"再生リスト「{playlist_title}」の動画を取得中...")
        video_ids_in_playlist = set()
        request = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50
        )
        while request:
            response = request.execute()
            for item in response["items"]:
                video_ids_in_playlist.add(item["contentDetails"]["videoId"])
            request = youtube.playlistItems().list_next(request, response)
        
        for video_id in video_ids_in_playlist:
            video_map[video_id].append(playlist_title)
    return video_map

def get_channel_videos(youtube, channel_id):
    """チャンネルのすべての動画の詳細情報を取得する"""
    res = youtube.channels().list(id=channel_id, part='contentDetails').execute()
    uploads_playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    all_video_ids_in_channel = set()
    request = youtube.playlistItems().list(part="contentDetails", playlistId=uploads_playlist_id, maxResults=50)
    while request:
        response = request.execute()
        for item in response["items"]:
            all_video_ids_in_channel.add(item["contentDetails"]["videoId"])
        request = youtube.playlistItems().list_next(request, response)
    
    all_video_ids_list = list(all_video_ids_in_channel)
    all_videos_details = []
    for i in range(0, len(all_video_ids_list), 50):
        chunk_ids = all_video_ids_list[i:i+50]
        video_response = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=",".join(chunk_ids)
        ).execute()
        all_videos_details.extend(video_response["items"])

    print(f"チャンネルの全動画 {len(all_videos_details)} 件の詳細情報を取得しました。")
    return all_videos_details

def save_to_csv(video_data):
    """動画データをCSVファイルに保存する"""
    with open(OUTPUT_CSV_FILE, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        # ヘッダー行に新しい列を追加
        writer.writerow([
            '公開日', 'タイトル', '動画URL', '再生回数', '高評価数', 'コメント数',
            '動画の長さ', '所属再生リスト', 'タグ', 'サムネイルURL', '説明文'
        ])
        for video in video_data:
            writer.writerow([
                video['published_at'],
                video['title'],
                video['url'],
                video['view_count'],
                video['like_count'],
                video['comment_count'],
                video['duration'],
                video['playlists'],
                video['tags'],
                video['thumbnail_url'],
                video['description']
            ])
    print(f"CSVファイル '{OUTPUT_CSV_FILE}' の作成が完了しました。")

if __name__ == "__main__":

    youtube = get_authenticated_service()
    
    playlists = get_channel_playlists(youtube, CHANNEL_ID)
    video_to_playlist = get_video_to_playlist_map(youtube, playlists)
    all_videos = get_channel_videos(youtube, CHANNEL_ID)

    final_data = []
    for video in all_videos:
        video_id = video['id']
        snippet = video.get('snippet', {})
        statistics = video.get('statistics', {})
        content_details = video.get('contentDetails', {})
        playlist_names = ", ".join(video_to_playlist.get(video_id, []))
        
        final_data.append({
            'published_at': snippet.get('publishedAt', '')[:10],
            'title': snippet.get('title', ''),
            'description': snippet.get('description', ''),
            'url': f'https://www.youtube.com/watch?v={video_id}',
            'playlists': playlist_names,
            'view_count': statistics.get('viewCount', 0),
            'like_count': statistics.get('likeCount', 0),
            'comment_count': statistics.get('commentCount', 0),
            'duration': parse_duration(content_details.get('duration', '')),
            'tags': ", ".join(snippet.get('tags', [])),
            'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url', '')
        })
    
    final_data.sort(key=lambda x: x['published_at'])
    save_to_csv(final_data)