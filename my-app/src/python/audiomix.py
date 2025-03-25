from pydub import AudioSegment
import librosa
import numpy as np

# 1. Analyze Audio Features
def analyze_audio(file_path):
    y, sr = librosa.load(file_path, sr=None, mono=True)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beats = librosa.frames_to_time(beat_frames, sr=sr)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    key = np.argmax(np.mean(chroma, axis=1))  # Simplistic key detection
    energy = librosa.feature.rms(y=y)[0]
    energy_times = librosa.frames_to_time(range(len(energy)), sr=sr)
    return tempo, beats, y, sr, key, energy, energy_times

# 2. Dynamic Beat Matching
def find_transition_points_dynamic(beats1, beats2, energy1, energy_times1, threshold_factor=0.1, min_transition_time=10.0):
    """
    Find transition points between two songs, ensuring they are not too early.
    """
    transition_points = []
    avg_interval1 = np.mean(np.diff(beats1)) if len(beats1) > 1 else 0.5
    avg_interval2 = np.mean(np.diff(beats2)) if len(beats2) > 1 else 0.5
    threshold = min(avg_interval1, avg_interval2) * threshold_factor

    # Only consider beats after min_transition_time
    beats1_filtered = [beat for beat in beats1 if beat >= min_transition_time]
    beats2_filtered = [beat for beat in beats2 if beat >= min_transition_time]

    for beat1 in beats1_filtered:
        for beat2 in beats2_filtered:
            if abs(beat1 - beat2) < threshold:
                transition_points.append((beat1, beat2))

    return transition_points

# 3. Custom fade curve generation
def custom_fade_curve(length, curve_type='linear'):
    if curve_type == 'logarithmic':
        return np.logspace(0, -1, length)
    elif curve_type == 'linear':
        return np.linspace(1, 0, length)
    else:
        raise ValueError("Unsupported curve type")

# 4. Apply fade curve to audio samples
def apply_fade(samples, fade_curve):
    faded_samples = samples * fade_curve
    return faded_samples

# 5. Dynamic Crossfade
def dynamic_crossfade(song1, song2, transition_point, fade_duration=3000, song1_name="Song 1", song2_name="Song 2"):
    """
    Apply dynamic crossfade between song1 and song2 at the given transition point.
    :param song1: AudioSegment for song 1
    :param song2: AudioSegment for song 2
    :param transition_point: Time (in seconds) where the transition happens
    :param fade_duration: Duration of the fade in milliseconds
    :param song1_name: Name of song 1 (for print statement)
    :param song2_name: Name of song 2 (for print statement)
    :return: Mixed AudioSegment
    """
    # Convert transition point to milliseconds
    transition_point_ms = transition_point * 1000

    # Ensure both songs are long enough for the crossfade
    if transition_point_ms + fade_duration > len(song1):
        raise ValueError(f"{song1_name} does not have enough data for crossfade at the transition point.")
    if transition_point_ms + fade_duration > len(song2):
        raise ValueError(f"{song2_name} does not have enough data for crossfade at the transition point.")
    
    # Slice the last part of song1 that will fade out
    fade_out_start = transition_point_ms - fade_duration
    fade_out_end = transition_point_ms
    fade_out_segment = song1[fade_out_start:fade_out_end]
    fade_out_segment = fade_out_segment.fade_out(fade_duration)
    fade_out_segment.export(f"temp/fade_out_{song1_name}.mp3", format="mp3")  # Export fade-out part
    
    # Set `fade_in_start` to the desired starting point (e.g., 50 seconds in song2)
    fade_in_start = 56 * 1000  # 50 seconds converted to milliseconds
    fade_in_end = min(fade_in_start + fade_duration, len(song2))
    fade_in_segment = song2[fade_in_start:fade_in_end]
    fade_in_segment = fade_in_segment.fade_in(fade_duration)
    fade_in_segment.export(f"temp/fade_in_{song2_name}.mp3", format="mp3")  # Export fade-in part
    
    # Ensure the first part doesn't include the fade-out segment
    first_part = song1[:fade_out_start]  # This part ends right before the fade-out
    first_part.export(f"temp/first_part_{song1_name}.mp3", format="mp3")  # Export first part
    
    # The second part is from song2 after the fade-in
    second_part = song2[fade_in_end:]  # After the fade-in
    second_part.export(f"temp/second_part_{song2_name}.mp3", format="mp3")  # Export second part

    # Function to convert seconds to minutes and seconds
    def seconds_to_min_sec(seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{int(minutes)}m {int(seconds)}s"

    # Print the start times of each segment with source information
    print(f"Transition Point: {transition_point:.2f} seconds")
    print(f"First Part of {song1_name} starts at: {seconds_to_min_sec(first_part.duration_seconds)}")
    print(f"Fade Out Segment (from {song1_name}) starts at: {seconds_to_min_sec(fade_out_start / 1000)}")
    print(f"Fade In Segment (from {song2_name}) starts at: {seconds_to_min_sec(fade_in_start / 1000)}")
    print(f"Second Part of {song2_name} starts at: {seconds_to_min_sec(second_part.duration_seconds)}")

    # Combine all parts together with the fade-out and fade-in segments
    mixed_song = first_part + fade_out_segment + fade_in_segment + second_part
    
    # Save the mixed song to file
    mixed_song.export("temp/mixed_output.mp3", format="mp3")
    print("Mixed audio saved as mixed_output.mp3")
    
    return mixed_song