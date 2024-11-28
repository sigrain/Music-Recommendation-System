import pandas as pd
from sklearn.preprocessing import StandardScaler

#df = pd.read_csv('spotify_Lofi_features_with_info.csv')
df = pd.read_csv('ref_spotify_Lofi_features_with_info.csv')

print("元のデータの最初の5行:")
print(df.head())

print("\n欠損値の確認:")
print(df.isnull().sum())

#features = df[['acousticness', 'danceability', 'energy', 'valence', 'instrumentalness', 'speechiness']]
features = df[['acousticness', 'tempo', 'loudness', 'mode', 'key', 'energy', 'valence', 'instrumentalness', 'time_signature']]

print("\n選定した特徴量の最初の5行:")
print(features.head())

scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)

df_scaled = pd.DataFrame(features_scaled, columns=['acousticness', 'tempo', 'loudness', 'mode', 'key', 'energy', 'valence', 'instrumentalness', 'time_signature'])
#df_scaled.to_csv('scaled_spotify_features.csv', index=False)
df_scaled.to_csv('ref_scaled_spotify_features.csv', index=False)

print("\nスケーリング後のデータの最初の5行:")
print(df_scaled.head())