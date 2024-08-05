from flask import Flask, request, render_template, jsonify
import pandas as pd
import numpy as np
from scipy.spatial.distance import cdist
from sklearn.preprocessing import StandardScaler
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from collections import defaultdict

app = Flask(__name__)

# Spotify API credentials
CLIENT_ID = '9eea9297dde44424a86b424e6fb81d6a'
CLIENT_SECRET = '2d0ff0c8165a4249b64f17f985172efc'
REDIRECT_URI = 'http://127.0.0.1:5000'

# Authenticate with user permission
scope = 'user-top-read user-library-read user-read-recently-played'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=scope))

number_cols = ['valence', 'year', 'acousticness', 'danceability', 'duration_ms', 'energy', 'explicit',
               'instrumentalness', 'key', 'liveness', 'loudness', 'mode', 'popularity', 'speechiness', 'tempo']

def get_all_spotify_data():
    results = sp.current_user_saved_tracks(limit=50)
    tracks = results['items']
    spotify_data = []
    for item in tracks:
        track = item['track']
        track_id = track['id']
        audio_features = sp.audio_features(track_id)[0]
        song_data = {
            'name': track['name'],
            'year': int(track['album']['release_date'][:4]),
            'explicit': int(track['explicit']),
            'duration_ms': track['duration_ms'],
            'popularity': track['popularity'],
            'artists': ', '.join(artist['name'] for artist in track['artists'])
        }
        song_data.update(audio_features)
        spotify_data.append(song_data)
    return pd.DataFrame(spotify_data)

# **Mood-Based Recommendation System**
def get_mood_recommendations(mood, n_songs=10):
    mood_features = {
        'happy': {'valence': (0.5, 1.0), 'energy': (0.5, 1.0)},
        'sad': {'valence': (0.0, 0.5), 'energy': (0.0, 0.5)},
        'energetic': {'energy': (0.7, 1.0)}
    }
    spotify_data = get_all_spotify_data()
    mood_data = spotify_data.copy()
    for feature, (low, high) in mood_features[mood].items():
        mood_data = mood_data[(mood_data[feature] >= low) & (mood_data[feature] <= high)]
    return mood_data.sample(n=n_songs)[['name', 'year', 'artists']].to_dict(orient='records')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    mood = request.form.get('mood')
    recommendations = get_mood_recommendations(mood)
    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True)
