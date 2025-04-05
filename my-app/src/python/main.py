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
ml_model.load_model()

song_paths = {}
tempo = {}
key = {}

#global variables for main()
MIN_INTRO_DURATION = 30
MIN_FADE_DURATION = 5000
MAX_FADE_DURATION = 20000

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
    if(save_audio_to_mongodb("temp/mixed_output.mp3", song_name, song_metadata) != None):
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
        logging.info("Analyzing songs...")
        tempo1, beats1, y1, sr1, key1, energy1, energy_times1 = analyze_audio(file_path1)
        tempo2, beats2, y2, sr2, key2, energy2, energy_times2 = analyze_audio(file_path2)

        tempo1 = float(tempo1[0] if isinstance(tempo1, np.ndarray) else tempo1)
        tempo2 = float(tempo2[0] if isinstance(tempo2, np.ndarray) else tempo2)

        logging.info(f"Song 1: Tempo={tempo1:.1f} BPM | Key={key1} | Duration={len(y1)/sr1:.1f}s")
        logging.info(f"Song 2: Tempo={tempo2:.1f} BPM | Key={key2} | Duration={len(y2)/sr2:.1f}s")

        adjusted_tempo2 = tempo1
        logging.info(f"Adjusting Song 2 tempo from {tempo2:.1f} to {adjusted_tempo2:.1f} BPM")
        tempo_adjusted_path = "temp/temp_adjusted.wav"
        create_tempo_adjusted_version(file_path2, tempo_adjusted_path, tempo2, adjusted_tempo2)
        song2_adjusted = AudioSegment.from_file(tempo_adjusted_path)

        logging.info("Analyzing lyrics...")
        lyrics1 = get_lyrics_with_cache(file_path1)
        lyrics2 = get_lyrics_with_cache(tempo_adjusted_path)

        lines1 = group_lyrics_into_lines(lyrics1)
        lines2 = group_lyrics_into_lines(lyrics2)

        duration1 = len(y1) / sr1
        duration2 = len(song2_adjusted) / 1000

        non_lyric1 = find_non_lyric_intervals(lines1, duration1)
        non_lyric2 = find_non_lyric_intervals(lines2, duration2)

        logging.info("Finding optimal transition point...")
        fade_duration, transition_point = find_best_fade_window(
            filter_non_intro_beats(beats1),
            non_lyric1,
            tempo1,
            energy1,
            energy_times1
        )

        if transition_point is None:
            logging.warning("No valid transition point found.")
            return None

        fade_duration = max(MIN_FADE_DURATION, min(MAX_FADE_DURATION, int(fade_duration)))
        beats_fade = fade_duration / 1000 * tempo1 / 60
        logging.info(f"Auto-selected: {fade_duration/1000:.1f}s fade (~{beats_fade:.1f} beats) at {transition_point:.1f}s")

        song1 = AudioSegment.from_file(file_path1)
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

        if not safe_beats2:
            logging.warning("No safe transition points found in second song")
            return None

        target_beat = transition_point * tempo2 / tempo1
        song2_beat = min(safe_beats2, key=lambda x: abs(x - target_beat))
        logging.info(f"Matching beat in Song 2: {song2_beat:.1f}s (target was {target_beat:.1f}s)")

        logging.info("Mixing audio...")
        mixed_song = dynamic_crossfade(
            song1_extended,
            song2_adjusted,
            transition_point,
            fade_duration,
            os.path.basename(file_path1),
            os.path.basename(file_path2)
        )

        output_path = "temp/mixed_song.mp3"
        mixed_song.export(output_path, format="mp3")
        logging.info(f"Mixed song saved as {output_path}")
        return output_path

    except Exception as e:
        logging.error(f"Error during processing: {str(e)}")
        return None
    finally:
        if 'tempo_adjusted_path' in locals() and os.path.exists(tempo_adjusted_path):
            os.remove(tempo_adjusted_path)

if __name__ == "__main__":
    app.run(debug=True)
