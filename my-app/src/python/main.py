from audiomix import *
from Ai_DJ_DB import *
from random_song import *
from pydub import AudioSegment
import numpy as np
from flask import Flask,jsonify,request,send_file,send_from_directory
from flask_cors import CORS
import os
import logging
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
    # Analyze songs
    logging.info("Analyzing songs...")
    tempo["file1"], beats1, y1, sr1, key["file1"], energy1, energy_times1 = analyze_audio(file_path1)
    tempo["file2"], beats2, y2, sr2, key["file2"], energy2, energy_times2 = analyze_audio(file_path2)

    logging.info(f"Song 1: Tempo={tempo['file1']} BPM, Key={key['file1']}, Duration={len(y1) / sr1} seconds")
    logging.info(f"Song 2: Tempo={tempo['file2']} BPM, Key={key['file2']}, Duration={len(y2) / sr2} seconds")

    logging.info("Finding transition points...")
    transitions = find_transition_points_dynamic(beats1, beats2, energy1, energy_times1, min_transition_time=15.0)

    if transitions:
        transition_point = transitions[0][0]  # Use the first detected transition point
        logging.info(f"Transition point at: {transition_point} seconds")
    else:
        logging.info("No transition points found.")
        return

    # Load the songs
    logging.info("Loading songs...")
    try:
        song1 = AudioSegment.from_file(file_path1)
        song2 = AudioSegment.from_file(file_path2)
        logging.info("Successfully loaded both songs")
    except Exception as e:
        logging.info(f"Error loading songs: {str(e)}")
        return

    # Mixing audio
    logging.info("Mixing audio...")
    try:
        mixed_song = dynamic_crossfade(song1, song2, transition_point)  # Use the tempo-adjusted version
        output_file = "temp/mixed_song.mp3"
        mixed_song.export(output_file, format="mp3")
        logging.info(f"Mixed audio saved as {output_file}")
        return output_file
        
    except ValueError as e:
        logging.info(e)

if __name__ == "__main__":
    app.run(debug=True)