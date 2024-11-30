import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

#素材用の曲のデータを読み取る
df = pd.read_csv('scaled_spotify_features.csv')
df_original = pd.read_csv('spotify_Lofi_features_with_info.csv')

#参照用の曲のデータを読み取り、ラベリングする
ref_df = pd.read_csv('ref_scaled_spotify_features.csv')
ref_df_original = pd.read_csv('ref_spotify_Lofi_features_with_info.csv')

ref_df['title'] = ref_df_original['track_name']
ref_df['artist'] = ref_df_original['artist_name']
ref_df['track_url'] = ref_df_original['id'].apply(lambda x: f"https://open.spotify.com/track/{x}")

#ターゲットの楽曲の特徴量を抽出
title='carried away'
target_song_row = ref_df[ref_df['title'] == title]
target_song_features = target_song_row[['acousticness', 'tempo', 'loudness', 'mode', 'key', 'energy', 'valence', 'instrumentalness', 'time_signature']]
target_song_df = pd.DataFrame(target_song_features)

#ターゲットの楽曲を追加し、コサイン近似値を算出
features = df[['acousticness', 'tempo', 'loudness', 'mode', 'key', 'energy', 'valence', 'instrumentalness', 'time_signature']]
features = pd.concat([features, target_song_df], ignore_index=True)
cosine_sim = cosine_similarity(features)

#各楽曲をラベリング
target_song_df_original = pd.DataFrame(ref_df_original[ref_df_original['track_name'] == title])
df_original = pd.concat([df_original, target_song_df_original], ignore_index=True)

df = pd.concat([df, target_song_row], ignore_index=True)
df['title'] = df_original['track_name']
df['artist'] = df_original['artist_name']
df['track_url'] = df_original['id'].apply(lambda x: f"https://open.spotify.com/track/{x}")
indices = pd.Series(df.index, index=df['title']).drop_duplicates()

#おすすめの楽曲を推薦する
def recommend_songs(title, cosine_sim=cosine_sim):
    if title not in indices:
        return []
    
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]

    song_indices = [i[0] for i in sim_scores]
    recommendations = df[['title', 'artist', 'track_url']].iloc[song_indices]

    return recommendations

results = recommend_songs(title)
print(results)