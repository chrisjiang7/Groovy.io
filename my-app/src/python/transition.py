import librosa
import numpy as np
import matplotlib.pyplot as plt

def analyze_audio(file_path):
    y, sr = librosa.load(file_path, sr=None, mono=True)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beats = librosa.frames_to_time(beat_frames, sr=sr)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    key = np.argmax(np.mean(chroma, axis=1))  # Simplistic key detection
    energy = librosa.feature.rms(y=y)[0]
    energy_times = librosa.frames_to_time(range(len(energy)), sr=sr)
    return tempo, beats, y, sr, key, energy, energy_times

def detect_chorus_transition(energy, energy_times, threshold_factor=2.0):
    """
    Detect the chorus transition based on dynamic energy threshold.
    """
    # Calculate the average energy and set the threshold as a multiple of the average
    avg_energy = np.mean(energy)
    threshold = avg_energy * threshold_factor

    print(f"Average Energy: {avg_energy}, Threshold: {threshold}")

    # Plot the energy profile for debugging
    plt.figure(figsize=(10, 6))
    plt.plot(energy_times, energy, label="Energy Profile")
    plt.axhline(y=threshold, color='r', linestyle='--', label="Energy Threshold")
    plt.xlabel("Time (s)")
    plt.ylabel("Energy")
    plt.title("Energy Profile for Chorus Detection")
    plt.legend()
    plt.show()

    # Find the point where energy exceeds threshold (simple heuristic for chorus)
    for i, e in enumerate(energy):
        if e > threshold:
            return energy_times[i]  # Return the time of the first energy peak above the threshold
    
    return None  # No transition point found

def visualize_energy(energy, energy_times, transition_time):
    """Visualize the energy levels and detected transition point"""
    plt.figure(figsize=(10, 6))
    plt.plot(energy_times, energy, label="RMS Energy")
    plt.axvline(x=transition_time, color='r', linestyle='--', label="Detected Transition Point")
    plt.xlabel("Time (s)")
    plt.ylabel("RMS Energy")
    plt.title("RMS Energy with Detected Transition Point")
    plt.legend()
    plt.show()
