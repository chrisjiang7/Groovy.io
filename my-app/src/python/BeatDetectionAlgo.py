import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt

# # Example usage:
song1_path = 'test_songs/ShapeOfYou.mp3'
song2_path = 'test_songs/CantStopTheFeeling.mp3'
# mashup_songs(song1_path, song2_path)
# Load audio file
y, sr = librosa.load(song1_path)

# Compute the STFT
n_fft = 1028  # Number of FFT components
hop_length = 256  # Number of samples between successive frames
stft = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)

# Convert the complex STFT to magnitude
magnitude = np.abs(stft)

# Convert to decibels for better visualization
db_magnitude = librosa.amplitude_to_db(magnitude, ref=np.max)

# Plot the spectrogram
plt.figure(figsize=(12, 6))
librosa.display.specshow(db_magnitude, sr=sr, hop_length=hop_length, x_axis='time', y_axis='log')
plt.colorbar(format='%+2.0f dB')
plt.title('Spectrogram (STFT)')
plt.xlabel('Time (s)')
plt.ylabel('Frequency (Hz)')
plt.show()


