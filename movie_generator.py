import os
os.environ["IMAGEIO_FFMPEG_EXE"] = "/Users/rain/Downloads/ffmpeg"
from moviepy.editor import *
from PIL import Image
import numpy as np
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

"""
指定したサイズにフィットしてリサイズする
"""
def resize_fit(im, resize_w, resize_h):
    w, h = im.size
    resize_aspect = resize_w / resize_h
    origin_aspect = w / h
    
    if resize_aspect > origin_aspect:
        r_h = int(resize_w / w * h)
        im = im.resize((resize_w, r_h))
        return im.crop((0, 0, resize_w, resize_h))
    else:
        r_w = int(resize_h / h * w)
        im = im.resize((r_w, resize_h))
        return im.crop((0, 0, resize_w, resize_h))
    
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

if __name__ == "__main__":
    title="It's Going to Be a Good Day"
    results = recommend_songs(title)
    print(results['title'])

    audioclips = []

    for i in range(5):
        path = "music/" + results.iloc[i]['title'] + ".wav"
        if (os.path.isfile(path) == True):
            bgm_clip = AudioFileClip("music/" + results.iloc[i]['title'] + ".wav")
            audioclips.append(bgm_clip)
    
    audiomix = concatenate_audioclips(audioclips)

    path = "input/1032.png"
    img = Image.open(path)
    img = resize_fit(img, 1280, 720)

    clip = ImageClip(np.array(img)).set_duration('00:01:00')
    clip = clip.set_audio(audiomix)

    clip.write_videofile(
        "output_video.mp4",
        fps=30,
    )
        

    """
    path = "input/1032.png"
    img = Image.open(path)
    img = resize_fit(img, 1280, 720)

    clip = ImageClip(np.array(img)).set_duration('00:03:00')
    bgm_clip = AudioFileClip("music/Visions.wav")
    clip = clip.set_audio(bgm_clip)

    clip.write_videofile(
        "output_video.mp4",
        fps=30,
    )
    """
    