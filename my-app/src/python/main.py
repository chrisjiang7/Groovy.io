from audiomix import *
from Ai_DJ_DB import *
from random_song import *
from pydub import AudioSegment
import numpy as np
from flask import Flask,jsonify,request,send_file,send_from_directory
from flask_cors import CORS
import os
import logging
import warnings

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ml_model = AIDJ()
#ml_model.build_music_graph()
#ml_model.save_model()
ml_model.load_model()

song_paths = {}
tempo = {}
key = {}

#global variables for main()
MIN_INTRO_DURATION = 30
MIN_FADE_DURATION = 5000
MAX_FADE_DURATION = 30000

warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

@app.route('/api/mix_songs', methods=['GET'])
def mix_song():
    if os.listdir("uploads"):
        output = main("uploads/song1.mp3", "uploads/song2.mp3")

        files = os.listdir('uploads')
        for file in files:
            file_path = os.path.join('uploads', file)
            if os.path.isfile(file_path):
                os.remove(file_path)

        return send_file(output, mimetype="audio/mpeg", as_attachment=True)


@app.route("/api/upload", methods=["POST"])
def upload_files():
    file1 = request.files["file1"]
    file2 = request.files["file2"]
    if file1 and file1.filename.endswith(".mp3") and file2 and file2.filename.endswith(".mp3"):
        song1_path = os.path.join(UPLOAD_FOLDER, "song1.mp3")
        song2_path = os.path.join(UPLOAD_FOLDER, "song2.mp3")
        file1.save(song1_path)
        file2.save(song2_path)

        song_paths["file1"] = song1_path
        song_paths["file2"] = song2_path

        result = f"Files '{file1.filename}' and '{file2.filename}' uploaded successfully!"

        return jsonify({"message": result})

    return jsonify({"message": "Invalid file format. Only MP3 allowed."}), 400

@app.route('/api/save_to_db', methods=["POST"])
def save_to_db():
    file1 = request.files["file1"]
    file2 = request.files["file2"]
    logging.info("Saving song to mongoDB ")
    song1_name,_ = os.path.splitext(os.path.basename(file1.filename))
    song2_name,_ = os.path.splitext(os.path.basename(file2.filename))
    song_name = song1_name + "X" + song2_name

    song_metadata = {
            "original_songs": [os.path.basename(file1.filename), os.path.basename(file2.filename)],
            "tempo1": float(tempo["file1"][0]) if isinstance(tempo["file1"], np.ndarray) else float(tempo["file1"]),
            "tempo2": float(tempo["file2"][0]) if isinstance(tempo["file2"], np.ndarray) else float(tempo["file2"]),
            "key1": int(key["file1"]),
            "key2": int(key["file2"]),
            "playlist_name": "Remixes",
            "transition_point": float(transition_point)
        }
    if(save_audio_to_mongodb("temp/mixed_song.mp3", song_name, song_metadata) != None):
        return jsonify({"message": "Song sucessfully saved"})
    else:
        return jsonify({"message": "Unable to save song"}), 400
    
@app.route('/api/list_songs/<playlist>', methods=['GET'])
def list_songs(playlist):
    logging.info("Getting list from mongoDB ")
    songs = list_stored_files()
    playlist = [entry for entry in songs if entry["playlist_name"] == playlist]
    logging.info(playlist)
    return jsonify(playlist)

@app.route('/api/get_song_db/<filename>', methods=['GET'])
def get_song_db(filename):
    logging.info("Getting songs from mongoDB ")
    retrieve_audio_from_mongodb(filename,"temp/retrieved_mixed_output.mp3")
    return send_from_directory("temp", "retrieved_mixed_output.mp3", as_attachment=False)

@app.route('/api/delete_song_db/<filename>', methods=['GET'])
def delete_song_db(filename):
    logging.info("Deleting song from mongoDB ")
    if(delete_song(filename)):
        return jsonify({"message": "Song sucessfully deleted"})
    else:
        return jsonify({"message": "Unable to delete song"}), 400
    

@app.route('/api/move_song/<filename>/<playlist_name>', methods=['GET'])
def move_song(filename,playlist_name):
    logging.info("Moving song to different playlist from mongoDB ")
    if(update_playlist(filename,playlist_name)):
        return jsonify({"message": "Song sucessfully moved"})
    else:
        return jsonify({"message": "Unable to move song"}), 400
    
@app.route('/api/random_song', methods=['GET'])
def random_song():
    logging.info("Randomly selecting song")
    song1,song2 = ml_model.recommend_next_track()
    logging.info(song1)
    logging.info(song2)
    return jsonify({
        "song_1": f"/test_songs/{song1}",
        "song_2": f"/test_songs/{song2}"
    })

@app.route('/test_songs/<path:filename>')
def serve_test_songs(filename):
    try:
        return send_from_directory('test_songs', filename)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404


def main(file_path1, file_path2):
    global transition_point
    try:
        os.makedirs("temp", exist_ok=True)
        os.makedirs("test_songs", exist_ok=True)

        # Convert to WAV to avoid MP3 stretching issues
        song1_wav = os.path.join("temp", "song1.wav")
        song2_wav = os.path.join("temp", "song2.wav")
        convert_to_wav(file_path1, song1_wav)
        convert_to_wav(file_path2, song2_wav)

        #print("\n=== Analyzing Songs ===")
        tempo["file1"], beats1, y1, sr1, key["file1"], energy1, energy_times1 = analyze_audio(song1_wav)
        tempo["file2"], beats2, y2, sr2, key["file2"], energy2, energy_times2 = analyze_audio(song2_wav)

        tempo1 = float(tempo["file1"][0] if isinstance(tempo["file1"], np.ndarray) else tempo["file1"])
        tempo2 = float(tempo["file2"][0] if isinstance(tempo["file2"], np.ndarray) else tempo["file2"])

        #print(f"\nSong 1: {os.path.basename(file_path1)}")
        #print(f"  Tempo: {tempo1:.1f} BPM | Key: {to_camelot(key1)} | Duration: {len(y1)/sr1:.1f}s")
        #print(f"\nSong 2: {os.path.basename(file_path2)}")
        #print(f"  Tempo: {tempo2:.1f} BPM | Key: {to_camelot(key2)} | Duration: {len(y2)/sr2:.1f}s")

        if abs(key["file1"] - key["file2"]) not in [0, 1, 11]:
            logging.info("Warning: Keys may be harmonically incompatible")

        #print("\n=== Adjusting Tempo ===")
        adjusted_tempo2 = tempo1
        tempo_adjusted_path = os.path.join("temp", "tempo_adjusted.wav")
        create_tempo_adjusted_version(song2_wav, tempo_adjusted_path, tempo2, adjusted_tempo2)
        song2_adjusted = AudioSegment.from_file(tempo_adjusted_path)

        #print("\n=== Analyzing Lyrics ===")
        lyrics1 = get_lyrics_with_cache(song1_wav)
        lyrics2 = get_lyrics_with_cache(tempo_adjusted_path)

        lines1 = group_lyrics_into_lines(lyrics1)
        lines2 = group_lyrics_into_lines(lyrics2)

        duration1 = len(y1) / sr1
        duration2 = len(song2_adjusted) / 1000

        non_lyric1 = find_non_lyric_intervals(lines1, duration1)
        non_lyric2 = find_non_lyric_intervals(lines2, duration2)

        #print("\n=== Finding Transition ===")
        fade_duration, transition_point = find_best_fade_window(
            filter_non_intro_beats(beats1),
            non_lyric1,
            tempo1,
            energy1,
            energy_times1
        )

        if transition_point is None:
            logging.info("No valid transition point found in Song 1.")
            return None

        transition_point = find_closest_beat(beats1, transition_point)
        logging.info(f"Quantized transition point to nearest beat: {transition_point:.2f}s")

        fade_duration = max(MIN_FADE_DURATION, min(MAX_FADE_DURATION, int(fade_duration)))
        beats_fade = fade_duration / 1000 * tempo1 / 60
        logging.info(f"Auto-selected: {fade_duration/1000:.1f}s fade (~{beats_fade:.1f} beats)")

        song1 = AudioSegment.from_file(song1_wav)
        required_duration = fade_duration / 1000
        current_duration = next((end - start for start, end in non_lyric1 if start <= transition_point <= end), 0)

        if current_duration < required_duration:
            logging.info(f"Extending section from {current_duration:.1f}s to {required_duration:.1f}s via looping")
            song1_extended, transition_point = extend_with_loop(
                song1,
                max(0, transition_point - current_duration/2),
                min(duration1, transition_point + current_duration/2),
                required_duration
            )
        else:
            song1_extended = song1

        safe_beats2 = get_safe_transition_points(
            filter_non_intro_beats(beats2),
            non_lyric2,
            fade_duration / 1000
        )

        target_beat = transition_point * tempo2 / tempo1

        if not safe_beats2:
            logging.info("No safe transition points found in song 2 — falling back to 4-bar entry")
            if len(beats2) > 16:
                song2_beat = beats2[16]
                logging.info(f"Using beat 16 (~4 bars): {song2_beat:.2f}s")
            else:
                song2_beat = 0
        else:
            song2_beat = min(safe_beats2, key=lambda x: abs(x - target_beat))

        logging.info(f"Matching beat in Song 2: {song2_beat:.1f}s (target was {target_beat:.1f}s)")

        logging.info("\n=== Mixing Songs ===")
        mixed_song = dynamic_crossfade(
            song1_extended,
            song2_adjusted,
            transition_point,
            fade_duration,
            os.path.basename(file_path1),
            os.path.basename(file_path2),
            song2_beat
        )

        output_path = os.path.join("temp", "mixed_song.mp3")
        mixed_song.export(output_path, format="mp3")
        logging.info(f"\nMixed song saved to: {output_path}")
        logging.info(f"Total duration: {len(mixed_song)/1000:.1f} seconds")
        return output_path

    except Exception as e:
        logging.info(f"\nError: {str(e)}")
        return None
    finally:
        # Clean up temporary files
        for temp_file in ["temp/song1.wav", "temp/song2.wav", "temp/tempo_adjusted.wav"]:
            if os.path.exists(temp_file):
                os.remove(temp_file)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
