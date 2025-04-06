from pydub import AudioSegment
from pydub.effects import low_pass_filter, high_pass_filter
import librosa
import numpy as np
import whisper
import pickle
import os
import soundfile as sf
from pydub.utils import get_array_type
from array import array

MIN_INTRO_DURATION = 30

#convert to wav
def convert_to_wav(input_path, output_path):
    audio = AudioSegment.from_file(input_path)
    audio.export(output_path, format="wav")

def to_camelot(key_index):
    camelot_wheel = ["8B", "3B", "10B", "5B", "12B", "7B", "2B", "9B", "4B", "11B", "6B", "1B"]
    return camelot_wheel[key_index % 12]

# Analyze Audio Features
def analyze_audio(file_path):
    y, sr = librosa.load(file_path, sr=None, mono=True)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beats = librosa.frames_to_time(beat_frames, sr=sr)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    key = np.argmax(np.mean(chroma, axis=1))
    energy = librosa.feature.rms(y=y)[0]
    energy_times = librosa.frames_to_time(range(len(energy)), sr=sr)
    return tempo, beats, y, sr, key, energy, energy_times

# Tempo Adjustment
def create_tempo_adjusted_version(input_file, output_file, original_tempo, target_tempo):
    try:
        import pyrubberband as rubberband
        using_rubberband = True
    except ImportError:
        using_rubberband = False

    y, sr = librosa.load(input_file, sr=None)
    rate = original_tempo / target_tempo
    rate = np.clip(rate, 0.85, 1.15)  #clamp for quality

    print(f"\n=== Time Stretching ===")
    print(f"Original Tempo: {original_tempo:.2f} BPM")
    print(f"Target Tempo:   {target_tempo:.2f} BPM")
    print(f"Stretch Rate:   {rate:.3f}")
    
    if using_rubberband:
        print("Using Rubber Band for high-quality stretching")
        y_stretched = rubberband.time_stretch(y, sr, rate,)
    else:
        print("Rubber Band not found. Falling back to Librosa (lower quality)")
        y_stretched = librosa.effects.time_stretch(y, rate)

    sf.write(output_file, y_stretched, sr)
    print(f"Tempo-adjusted audio saved to: {output_file}")

def custom_fade_curve(length, direction='out', curve_type='ease_in_out'):
    t = np.linspace(0, 1, length)

    if curve_type == 'ease_in_out':
        # Smoothstep fade (ease in, ease out)
        curve = 3 * t**2 - 2 * t**3
    elif curve_type == 'linear':
        curve = t
    elif curve_type == 'log':
        curve = np.logspace(-2, 0, length, base=10)
        curve = (curve - curve.min()) / (curve.max() - curve.min())
    else:
        raise ValueError("Unsupported curve type")

    return 1 - curve if direction == 'out' else curve
# crossfade
def dynamic_crossfade(song1, song2, transition_point, fade_duration, song1_name="Song 1", song2_name="Song 2", song2_beat=0.0):
    fade_duration = int(round(fade_duration))
    transition_ms = int(round(transition_point * 1000))

    fade_out_start = max(0, transition_ms - fade_duration)
    fade_out_end = transition_ms

    fade_in_start = int(song2_beat * 1000)
    fade_in_end = fade_in_start + fade_duration

    if fade_out_start >= len(song1):
        raise ValueError(f"Transition point {transition_point:.1f}s is too late in {song1_name} (duration: {len(song1)/1000:.1f}s)")
    if fade_in_end > len(song2):
        raise ValueError(f"Fade duration {fade_duration}ms is too long at {song2_beat:.2f}s in {song2_name} (duration: {len(song2)/1000:.1f}s)")

    try:
        fading_out = song1[fade_out_start:fade_out_end]
        fading_in = song2[fade_in_start:fade_in_end]

        # Convert to numpy arrays
        samples_out = np.array(fading_out.get_array_of_samples()).astype(np.float32)
        samples_in = np.array(fading_in.get_array_of_samples()).astype(np.float32)

        # Generate fade curves
        curve_out = custom_fade_curve(len(samples_out), direction='out', curve_type='ease_in_out')
        curve_in = custom_fade_curve(len(samples_in), direction='in', curve_type='ease_in_out')

        # Apply fade curves
        faded_out = samples_out * curve_out
        faded_in = samples_in * curve_in

        # Convert back to AudioSegments
        sample_width = fading_out.sample_width
        array_type = get_array_type(sample_width * 8)

        final_out = fading_out._spawn(array(array_type, faded_out.astype(np.int16)))
        final_in = fading_in._spawn(array(array_type, faded_in.astype(np.int16)))

        # Overlay crossfade segment
        crossfade_segment = final_out.overlay(final_in)

        return (
            song1[:fade_out_start] +        # Beginning of song 1
            crossfade_segment +             # Crossfade segment
            song2[fade_in_end:]             # Remainder of song 2 after the transition
        )

    except Exception as e:
        raise RuntimeError(
            f"Failed to create crossfade between {song1_name} and {song2_name} "
            f"at {transition_point:.1f}s with {fade_duration}ms fade: {str(e)}"
        )

# Whisper Lyrics
def extract_lyrics_with_timings(audio_path: str, model_size: str = "tiny"):
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path, word_timestamps=True)
    lyrics = []
    for segment in result["segments"]:
        for word in segment["words"]:
            lyrics.append({
                "word": word["word"],
                "start": word["start"],
                "end": word["end"],
                "confidence": word.get("probability", 0)
            })
    return lyrics

def group_lyrics_into_lines(word_timings, max_pause=0.5):
    lines = []
    current_line = []
    for word in word_timings:
        if not current_line or word["start"] - current_line[-1]["end"] <= max_pause:
            current_line.append(word)
        else:
            lines.append({
                "text": " ".join(w["word"] for w in current_line),
                "start": current_line[0]["start"],
                "end": current_line[-1]["end"],
                "words": current_line
            })
            current_line = [word]
    if current_line:
        lines.append({
            "text": " ".join(w["word"] for w in current_line),
            "start": current_line[0]["start"],
            "end": current_line[-1]["end"],
            "words": current_line
        })
    return lines

def find_non_lyric_intervals(lyric_lines, total_duration, min_gap=0.5):
    non_lyric_intervals = []
    prev_end = 0.0
    for line in lyric_lines:
        if line["start"] > prev_end:
            if non_lyric_intervals and (line["start"] - prev_end) < min_gap:
                prev_start, _ = non_lyric_intervals.pop()
                non_lyric_intervals.append((prev_start, line["start"]))
            else:
                non_lyric_intervals.append((prev_end, line["start"]))
        prev_end = line["end"]
    if prev_end < total_duration:
        non_lyric_intervals.append((prev_end, total_duration))
    return non_lyric_intervals

def get_lyrics_with_cache(file_path, model_size="tiny"):
    base_name = os.path.basename(file_path)
    cache_dir = ".cache"
    os.makedirs(cache_dir, exist_ok=True)

    cache_file = os.path.join(
        cache_dir,
        f"{base_name}.{model_size}.v1.lyrics_cache"
    )

    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            return pickle.load(f)

    # Run transcription
    lyrics = extract_lyrics_with_timings(file_path, model_size)
    
    with open(cache_file, 'wb') as f:
        pickle.dump(lyrics, f)
        
    return lyrics

# Transition Tools
def filter_non_intro_beats(beats):
    return [beat for beat in beats if beat >= MIN_INTRO_DURATION]

def find_closest_beat(beats, target_time):
    return min(beats, key=lambda x: abs(x - target_time))

def calculate_optimal_fade(tempo, energy, current_time, energy_times, beats):
    base_fade_beats = 10
    current_energy = np.interp(current_time, energy_times, energy)
    energy_factor = 1.5 - (current_energy / np.max(energy))
    fade_beats = base_fade_beats * energy_factor
    beat_duration = 60 / tempo
    fade_duration = max(8, min(12, fade_beats * beat_duration))
    return fade_duration * 1000

def find_best_fade_window(beats, non_lyric_intervals, tempo, energy, energy_times):
    candidate_points = []
    for interval_start, interval_end in non_lyric_intervals:
        if interval_end - interval_start < 2:
            continue
        interval_beats = [b for b in beats if interval_start <= b <= interval_end]
        for beat in interval_beats:
            potential_fade = calculate_optimal_fade(
                tempo, energy, beat, energy_times, beats
            ) / 1000
            fade_start = beat - (potential_fade/2)
            fade_end = beat + (potential_fade/2)
            if fade_start >= interval_start and fade_end <= interval_end:
                energy_score = 1 - abs(0.5 - (np.interp(beat, energy_times, energy)/np.max(energy)))
                duration_score = min(1, potential_fade/8)
                score = energy_score * duration_score
                candidate_points.append((score, beat, potential_fade))
    if not candidate_points:
        return None, None
    best_candidate = max(candidate_points, key=lambda x: x[0])
    return best_candidate[2] * 1000, best_candidate[1]

def get_safe_transition_points(beats, non_lyric_intervals, fade_duration):
    safe_beats = []
    margin = 0.25
    for beat in beats:
        window_start = beat - fade_duration / 2
        window_end = beat + fade_duration / 2
        if window_start < 0:
            continue
        for interval_start, interval_end in non_lyric_intervals:
            if (interval_start - margin) <= window_start and (window_end <= interval_end + margin):
                safe_beats.append(beat)
                break
    return safe_beats

def extend_with_loop(audio_segment, interval_start, interval_end, target_duration):
    loop_duration = interval_end - interval_start
    loop_segment = audio_segment[interval_start*1000 : interval_end*1000]
    needed_loops = int(np.ceil((target_duration - loop_duration) / loop_duration))
    extended = loop_segment * needed_loops
    transition_point = interval_end
    before = audio_segment[:interval_start*1000]
    after = audio_segment[interval_end*1000:]
    return before + extended + after, transition_point
