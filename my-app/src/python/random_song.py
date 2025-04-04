from audiomix import *
import librosa
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
import numpy as np
import os, random
import joblib



class AIDJ:
    def __init__(self):
        self.track_features = {}
        self.nn_model =  NearestNeighbors(n_neighbors=3)
        self.scaler = StandardScaler()

    
    def build_music_graph(self):
        for file in os.listdir("test_songs"):
            tempo, beats, y, sr, key, energy, energy_times = analyze_audio("test_songs/"+file)
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr).mean()
            self.track_features[file] = {}
            self.track_features[file]['tempo'] = int(tempo)
            self.track_features[file]['key'] = int(key)
            self.track_features[file]['energy'] = float(spectral_centroid)

        # Create feature matrix for NN
        features = np.array([
            [f['tempo'], f['key'], f['energy']]
            for f in self.track_features.values()
        ])

        scaled_features = self.scaler.fit_transform(features)

        self.nn_model.fit(scaled_features)

    def recommend_next_track(self):
        current_track = random.choice(os.listdir("test_songs"))
        current_features = self.track_features[current_track]
        query = np.array([
            current_features['tempo'],
            current_features['key'],
            current_features['energy']
        ]).reshape(1, -1)

        scaled_query = self.scaler.transform(query)

        distances, indices = self.nn_model.kneighbors(scaled_query)
        similar_indices = indices[0][1:]
        recommended_index = random.choice(similar_indices)
        recommended_track = list(self.track_features.keys())[recommended_index]
        return current_track, recommended_track
    
    def save_model(self):
        # Save the model
        joblib.dump({
            'track_features': self.track_features,
            'nn_model': self.nn_model,
            'scaler': self.scaler
        }, 'dj_model_data.pkl')

    def load_model(self):
        # Save the model
        data = joblib.load('dj_model_data.pkl')
        self.track_features = data['track_features']
        self.nn_model = data['nn_model']
        self.scaler = data['scaler']

    
    


