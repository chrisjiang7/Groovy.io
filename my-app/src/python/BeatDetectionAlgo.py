import librosa
import numpy as np
from sklearn.cluster import KMeans
from scipy.signal import find_peaks

def detect_section_transitions(audio_file, n_sections=3):
    """
    Enhanced verse/chorus transition detection focusing on:
    - Spectral contrast (important for verse-chorus transitions)
    - Harmonic changes
    - Energy level changes
    - Rhythmic pattern changes
    """
    # Load audio with optimal parameters
    y, sr = librosa.load(audio_file, duration=180)  # Analyze first 3 minutes
    hop_length = 1024  # Smaller window for better temporal resolution
    
    # Extract more targeted features
    # Spectral contrast (helps identify changes in musical texture)
    contrast = librosa.feature.spectral_contrast(y=y, sr=sr, hop_length=hop_length)
    
    # Harmonic content with better temporal resolution
    chroma = librosa.feature.chroma_cens(y=y, sr=sr, hop_length=hop_length)
    
    # Energy features
    rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
    # Mel-scaled spectrogram for better frequency resolution
    mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, hop_length=hop_length, n_mels=128)
    mel_db = librosa.power_to_db(mel_spec, ref=np.max)
    
    # Rhythm features
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop_length)
    beat_strength = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
    
    # Normalize and combine features
    features = np.vstack([
        contrast,  # Spectral contrast features
        chroma,    # Harmonic content
        rms[np.newaxis, :contrast.shape[1]],  # Energy
        np.mean(mel_db, axis=0)[np.newaxis, :contrast.shape[1]],  # Average mel energy
        beat_strength[np.newaxis, :contrast.shape[1]]  # Rhythmic information
    ]).T
    
    # Normalize features
    features = (features - np.mean(features, axis=0)) / np.std(features, axis=0)
    
    # Cluster sections with more clusters for finer granularity
    kmeans = KMeans(n_clusters=n_sections + 2, random_state=42)
    labels = kmeans.fit_predict(features)
    
    # Calculate transition scores with adjusted weights
    window_time = hop_length / sr
    
    # Fix the shape mismatch in the transition scores calculation
    label_changes = np.abs(np.diff(labels, prepend=labels[0]))
    contrast_changes = np.mean(np.abs(np.diff(contrast, axis=1)), axis=0)
    rms_changes = np.abs(np.diff(rms, prepend=rms[0]))
    chroma_changes = np.mean(np.abs(np.diff(chroma, axis=1)), axis=0)
    
    # Ensure all arrays have the same length
    min_length = min(len(label_changes), len(contrast_changes), 
                    len(rms_changes), len(chroma_changes), 
                    len(beat_strength))
    
    # Enhanced scoring system with proper array lengths:
    transition_scores = (
        0.35 * label_changes[:min_length] +      # Structure changes
        0.25 * contrast_changes[:min_length] +   # Texture changes
        0.20 * rms_changes[:min_length] +        # Energy changes
        0.10 * chroma_changes[:min_length] +     # Harmonic changes
        0.10 * beat_strength[:min_length]        # Rhythmic intensity
    )
    
    # Smooth the transition scores
    window_size = int(0.2 * sr / hop_length)  # 200ms window
    transition_scores = np.convolve(transition_scores, 
                                  np.hanning(window_size)/window_size, 
                                  mode='same')
    
    # Find peaks with adaptive threshold
    threshold = np.percentile(transition_scores, 85) 

    # Minimum 15 seconds between transitions
    min_distance = int(15/window_time)  
    
    peaks, _ = find_peaks(
        transition_scores,
        height=threshold,
        distance=min_distance,
        prominence=np.std(transition_scores) 
    )
    
    # Convert to timestamps
    transitions = sorted([p * window_time for p in peaks])
    
    # Filter out transitions before 50 seconds
    transitions = [t for t in transitions if t >= 50]
    
    # Post-processing for most significant transitions
    if len(transitions) > 0:
        # Get peak scores for filtered transitions
        peak_scores = [transition_scores[int(t/window_time)] for t in transitions]
        
        # Select top transitions based on score
        if len(transitions) > 3:
            top_indices = np.argsort(peak_scores)[-3:]
            transitions = sorted([transitions[i] for i in top_indices])
    
    return transitions

def print_transitions(audio_file):
    """Print detected transitions with timestamps"""
    transitions = detect_section_transitions(audio_file)
    
    print(f"\nAnalysis of: {audio_file}")
    if not transitions:
        print("No clear transitions detected")
    else:
        print("Most likely verse-chorus transitions:")
        for i, time in enumerate(transitions, 1):
            mins = int(time // 60)
            secs = int(time % 60)
            print(f"  {i}. {mins}:{secs:02d}")

if __name__ == "__main__":
    audio_file = 'test_songs/CantStopTheFeeling.mp3'
    print_transitions(audio_file)
    