# 必要なライブラリのインポート
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import time
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Spotify APIの認証情報
CLIENT_ID = 'e66dda04498a46038fe510b9dca85185'
CLIENT_SECRET = '8cedcd94028d42798d5197d6b8565bd9'

# Spotify APIへの認証
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id='e66dda04498a46038fe510b9dca85185', client_secret='8cedcd94028d42798d5197d6b8565bd9'))

# リクエスト制限に対応するための待機時間（秒）
REQUEST_DELAY = 1  # 通常は1-2秒が適切です
MAX_RETRIES = 3  # 最大リトライ回数

# プレイリストごとにトラックIDを取得
def get_track_ids_from_playlists(playlist_ids, tracks_per_playlist=100):
    track_ids = set()  # 重複を避けるためセットを使用
    for playlist_id in playlist_ids:
        playlist_tracks = sp.playlist_tracks(playlist_id, limit=tracks_per_playlist)
        for item in playlist_tracks['items']:
            track_ids.add(item['track']['id'])
        logger.info(f'Playlist ID: {playlist_id}, Tracks fetched: {len(track_ids)}')
        time.sleep(REQUEST_DELAY)  # リクエスト制限に対応するための待機時間
    return list(track_ids)

def get_track_ids_from_albums(album_ids, tracks_per_album=50):
    track_ids = set()
    for album_id in album_ids:
        album_tracks = sp.album_tracks(album_id, limit=tracks_per_album)
        for item in album_tracks['items']:
            track_ids.add(item['id'])
        logger.info(f'Album ID: {album_id}, Tracks fetched: {len(track_ids)}')
        time.sleep(REQUEST_DELAY)
    return list(track_ids)

# トラックの特徴量を取得してデータフレームに保存
def get_track_features(track_ids):
    features_list = []
    track_info_list = []
    total_tracks = len(track_ids)
    for i in range(0, total_tracks, 50):  # 50件ずつ取得
        batch = track_ids[i:i + 50]
        for attempt in range(MAX_RETRIES):
            try:
                features = sp.audio_features(batch)
                for feature in features:
                    if feature:  # 有効な特徴量データがある場合
                        features_list.append(feature)
                        track_info = sp.track(feature['id'])
                        track_name = track_info['name']
                        artist_name = track_info['artists'][0]['name']
                        track_info_list.append({'id': feature['id'], 'track_name': track_name, 'artist_name': artist_name})
                logger.info(f'Processed {i + len(batch)} / {total_tracks} tracks')
                time.sleep(REQUEST_DELAY)  # リクエスト制限に対応するための待機時間
                break  # 正常に処理された場合はループを抜ける
            except Exception as e:
                logger.error(f'Error processing batch {i // 50 + 1}: {e}')
                time.sleep(REQUEST_DELAY * (attempt + 1))  # 待機時間を増やして再試行
                if attempt == MAX_RETRIES - 1:
                    logger.error(f'Failed to process batch {i // 50 + 1} after {MAX_RETRIES} attempts')
    return pd.DataFrame(features_list), pd.DataFrame(track_info_list)

# プレイリストIDのリスト（PurrpleCatの楽曲アルバムのID）
album_ids = [
    '2K5GZ1Psz2XHF4SpEJkhgX', #Dino Land
    '55L8lKQl6gbxfh5bcWrCLQ', #Eye of the Storm
    '3hD3hLhE4W5Lvx5XSuTd5w', #Happy Place
    '59m7LCjUEDGPQuWoYHadCZ', #Distant Worlds 4
    '04aVAYOaZJ9vXYTa4y3lBj', #Sands of Time
    '6ss3oRZIxr0jk9kB66HpHb', #City Nights 2
    '7A5vVrxjCelpOMceajwqJ2', #Sea of Stars 2
    '3WdJxDOuJnqyDQmW91goLC', #Tranquil Trails
    '0BpgwfJCTVqWevgNhA4n1J', #Night Train
    '6NKkzD1sK7kCVoDE0zx1hx', #Please Hold Me
    '2QHF5f0m72y7s69fxCsFIG', #Distant Worlds 3
    '7BueHUEkuGGJL07tvBaiyt', #Multiverse
    '13CYfS3FXVKVR6CcxniyJF', #Signs of Life
    '7jl0owgDzhTW0EW1IYZwbO', #Sea of Stars
    '24UhqWzgdqPkNVqTGse44S', #Distant Worlds 2
    '6EVQT7Xc0p59lQMDFY6fGH', #House in the Woods
    '1V1AErAHIPzUS9hadeD4d9', #Sky Lake
    '7GVLnMDEXBGYaedR9O9WJ2', #Oasis
    '712XhXdmixid8lPfLg8Sp0', #Adventure Island
    '1HMUgCoAmBAPcvvyy5Ol8n', #Sleeping Cat
    '3LrTtPoOMTzawKeOXirGBh', #City Nights
    '7wvearmMh28I7gpcW3U5Zo', #Floating Castle
    '6fCxHAh209OFUJ1WSzvhRh', #Distant Worlds
    '1wKEos4Xsx9LCyxNBX508l', #Sleepy Eyes
    '4NrDKpBMcem4V4jqm2KgYv', #Above the Clouds
    '1bGLisfgtSYUzHbCmWcWxL', #Far from Home
    '2tfTGm3G3RWTGZCfBq0yiR', #Mellow Skies
    '0Jxt4HUjGrMKZhRugGmTR3', #Melting Snow
    '0b9VM6B5aFfkt5Re9NwYNQ', #Sweet Dreams
    '1iEBsMAjSPTZkmJ3mE1fd7', #Bloom
    '7jWERk1GForch2aujc6job', #Mono no aware
    '6joo22r88KqXxvOgEORO9R', #Snowbound
    '2lfNRWiTrto7WhHH5EyggB', #Reading During a Thunder Storm
    '4nT8Ze9lBK46JgZfdIs5zW', #Feelin' Fresh
    '6mG7ipIWFLDJ7otgqXRVGN', #Cat Nap
    '3oEexKDd87suM4rxvFh4KG', #Pelagic Journey
    '1xvf3EqqV6Z4QyfzmDJnDA', #Whispers in the Dark
    '4laHLSbi5yvlh0au02OAU1', #Floating to my bedroom
    '0k3F0C9gHgn7P4xXMvhDfE', #A Good Book
    '03wu3desDKeyIKIREXVEaB', #Just Relax
    '7sCy4WxBx3docv52rrTHnx', #Nostalgia and Moving On
    '0yvwPdLH0siy6jlf84Dqze', #Brain Fog
    '6F2rfo9UxDyF2zfxWk8V1Y', #Indigo Dreams
    '2x7smIiF9UjVFZomo9NKUj', #Now or Never
    '4G8pLLXrTbS62CvKDJxzGl', #Up All Night
]

ref_album_ids = [
    '5sdidXAFrlLlR7pxIkvH2a', #happy day
    '6OOfmtVLBHjDPORNmcpstw', #Dreamland
    '6NkBw1KlvZjaRK1An85T1q', #CozyCafe
    '5JZwvefxlkxf1UuRuVV88d', #moonlight melanchory
    '34ghYFISn9VEpGNwR4o5X8', #imaginary
    '3U5IXAObtsdk809C6GXzUv', #soothing breeze
    '4J04asMI7ZClXLFy5EaC2l', #daydream
    '5McRM5rXSMID4SAaO7Z3X7', #calmy
    '3jXMV80tootPuCv3ZeTH8T', #feelin warm
    '4AL6wGK6sAimDgMIzGuLfz', #quiet city
    '42HBZlENumc3uVbUhHkb1r', #a better place
    '4m6bLncIYJTrXPP1VElbMD', #golden hour
    '1h6oXNtiHZeYfYgoTIXxQf', #secret garden
    '6KmFVc02ydkX74X0mgytOM', #alone time
    '75wHLesrFkyesQlDOtBha8', #homeland
    '6CKdLa08BOvAH7yoTOxu9X', #daydream
    '33UUMdyDFYuUD1rqXbQxlA', #Cozy Vacation
]

# トラックIDを取得
logger.info('Fetching track IDs...')
#track_ids = get_track_ids_from_albums(album_ids)
track_ids = get_track_ids_from_albums(ref_album_ids)

# 特徴量とトラック情報を取得
logger.info('Fetching track features and info...')
df_features, df_track_info = get_track_features(track_ids)

# 特徴量データフレームにトラック情報を結合
df = pd.merge(df_features, df_track_info, on='id')

# 必要な列のみを選択(ここでは全て選択しています)
df = df[['id', 'track_name', 'artist_name', 'acousticness', 'danceability', 'energy', 'valence', 'instrumentalness', 'speechiness', 'tempo', 'loudness', 'mode', 'key', 'duration_ms', 'time_signature']]

# データを保存
#df.to_csv('spotify_Lofi_features_with_info.csv', index=False)
df.to_csv('ref_spotify_Lofi_features_with_info.csv', index=False)

logger.info("Spotify楽曲特徴量データがref_spotify_Lofi_features_with_info.csvに保存されました。")
