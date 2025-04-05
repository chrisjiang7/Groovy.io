from pydub import AudioSegment
import librosa
import numpy as np
import whisper
import pickle
import os
import soundfile as sf

MIN_INTRO_DURATION = 30

# 1. Analyze Audio Features
def analyze_audio(file_path):
    y, sr = librosa.load(file_path, sr=None, mono=True)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beats = librosa.frames_to_time(beat_frames, sr=sr)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    key = np.argmax(np.mean(chroma, axis=1))
    energy = librosa.feature.rms(y=y)[0]
    energy_times = librosa.frames_to_time(range(len(energy)), sr=sr)
    return tempo, beats, y, sr, key, energy, energy_times

# tempo adjustment with librosa
def create_tempo_adjusted_version(input_file, output_file, original_tempo, target_tempo):
    y, sr = librosa.load(input_file, sr=None)
    speed_factor = target_tempo / original_tempo
    print(f"Original tempo: {original_tempo:.2f}, Target tempo: {target_tempo:.2f}, Speed factor: {speed_factor:.3f}")
    y_stretched = librosa.effects.time_stretch(y, rate=speed_factor)
    sf.write(output_file, y_stretched, sr)
    print(f"Tempo-adjusted audio saved as {output_file}")


# Lyrics

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
    cache_file = f"{file_path}.{model_size}.v1.lyrics_cache"
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    lyrics = extract_lyrics_with_timings(file_path, model_size)
    with open(cache_file, 'wb') as f:
        pickle.dump(lyrics, f)
    return lyrics

def filter_non_intro_beats(beats):
    return [beat for beat in beats if beat >= MIN_INTRO_DURATION]

def find_closest_beat(beats, target_time):
    return min(beats, key=lambda x: abs(x - target_time))

def calculate_optimal_fade(tempo, energy, current_time, energy_times, beats):
    base_fade_beats = 4
    current_energy = np.interp(current_time, energy_times, energy)
    energy_factor = 1.5 - (current_energy / np.max(energy))
    fade_beats = base_fade_beats * energy_factor
    beat_duration = 60 / tempo
    fade_duration = max(2, min(16, fade_beats * beat_duration))
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
    for beat in beats:
        window_start = beat - fade_duration/2
        window_end = beat + fade_duration/2
        if window_start < 0:
            continue
        for interval_start, interval_end in non_lyric_intervals:
            if interval_start <= window_start and window_end <= interval_end:
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

def dynamic_crossfade(song1, song2, transition_point, fade_duration, song1_name="Song 1", song2_name="Song 2"):
    fade_duration = int(round(fade_duration))
    transition_ms = int(round(transition_point * 1000))
    fade_out_start = max(0, transition_ms - fade_duration)
    fade_out_end = transition_ms
    fade_in_end = min(len(song2), fade_duration)

    if fade_out_start >= len(song1):
        raise ValueError(f"Transition point {transition_point:.1f}s is too late in {song1_name} (duration: {len(song1)/1000:.1f}s)")
    if fade_in_end > len(song2):
        raise ValueError(f"Fade duration {fade_duration}ms too long for {song2_name} (duration: {len(song2)/1000:.1f}s)")

    fading_out = song1[fade_out_start:fade_out_end].fade_out(fade_duration)
    fading_in = song2[:fade_in_end].fade_in(fade_duration)
    crossfade_segment = fading_out.overlay(fading_in)

    return song1[:fade_out_start] + crossfade_segment + song2[fade_in_end:]
