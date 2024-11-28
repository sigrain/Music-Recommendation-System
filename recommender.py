import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

df = pd.read_csv('scaled_spotify_features.csv')
df_original = pd.read_csv('spotify_Lofi_features_with_info.csv')

features = df[['acousticness', 'tempo', 'loudness', 'mode', 'key', 'energy', 'valence', 'instrumentalness', 'time_signature']]

cosine_sim = cosine_similarity(features)

df['title'] = df_original['track_name']
df['artist'] = df_original['artist_name']
df['track_url'] = df_original['id'].apply(lambda x: f"https://open.spotify.com/track/{x}")
indices = pd.Series(df.index, index=df['title']).drop_duplicates()

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

title='Sonder'
results = recommend_songs(title)
print(results)