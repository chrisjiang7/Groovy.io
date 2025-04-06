import React, { useState, useRef } from "react";
import { mdiUpload, mdiPlay, mdiStop, mdiDownload, mdiVolumeHigh } from "@mdi/js";
import Icon from "@mdi/react";

const Mix = () => {
  const [song1, setSong1] = useState(null);
  const [song2, setSong2] = useState(null);
  const [mixing, setMixing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [mixComplete, setMixComplete] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);
  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [data, setData] = useState(null);
  const [volume, setVolume] = useState(1.0); // New volume state


  const audioRef = useRef(null);

  const handleSongUpload = (e, songNumber) => {
    const file = e.target.files[0];
    if (file) {
      songNumber === 1 ? setSong1(file) : setSong2(file);
    }
  };


  const handleVolumeChange = (e) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    audioRef.current.volume = newVolume;
  };


  const handleMix = () => {
    if (song1 && song2) {
      setMixing(true);
      setProgress(0);
      setMixComplete(false);
      setAudioUrl(null);
      uploadFiles();
    }
  };

  const togglePlayback = () => {
    if (playing) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setPlaying(!playing);
  };

  const handleTimeUpdate = () => {
    setCurrentTime(audioRef.current.currentTime);
  };

  const handleLoadedMetadata = () => {
    setDuration(audioRef.current.duration);
  };

  const handleSeek = (e) => {
    const rect = e.target.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const width = rect.width;
    const percentage = clickX / width;
    const newTime = percentage * duration;
    audioRef.current.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const formatTime = (time) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
  };

  const uploadFiles = () => {
    const formData = new FormData();
    formData.append("file1", song1);
    formData.append("file2", song2);
    fetch("http://127.0.0.1:5000/api/upload", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        setData(data.message);
        mix_songs();
      })
      .catch((error) => console.error("Upload error:", error));
  };

  const mix_songs = () => {
    let interval;
    setProgress(0);
  
    interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) return prev; // Don't let it reach 100% yet
        return prev + 10;
      });
    }, 500);
  
    fetch("http://127.0.0.1:5000/api/mix_songs")
      .then((response) => response.blob())
      .then((blob) => {
        clearInterval(interval); // Stop progress updates
        const url = URL.createObjectURL(blob);
        setAudioUrl(url);
        setProgress(100); // Only now set to 100%
        setMixing(false);
        setMixComplete(true);
      })
      .catch((error) => {
        clearInterval(interval);
        console.error("Received file error:", error);
      });
  };
  
  const upload_to_db = () => {
    const formData = new FormData();
    formData.append("file1", song1);
    formData.append("file2", song2);
    fetch("http://127.0.0.1:5000/api/save_to_db", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => setData1(data.message))
      .catch((error) => console.error("Upload error:", error));
  };

  const random_song = () => {
    fetch("http://127.0.0.1:5000/api/random_song")
    .then(response => response.json())
    .then(data => {
      fetchAndUploadSong(`http://localhost:5000${data.song_1}`, 1);
      fetchAndUploadSong(`http://localhost:5000${data.song_2}`, 2);
    })
    .catch((error) => console.error("Random song select error:", error));
  };

  const fetchAndUploadSong = async (url, songNumber) => {
    const response = await fetch(url);
    const blob = await response.blob();
    const filename = url.split("/").pop(); // get filename from URL
  
    const file = new File([blob], filename, { type: blob.type });
    handleSongUpload({ target: { files: [file] } }, songNumber);
  };

  return (
    <div className="flex flex-col items-center p-8 pb-24 w-full">
      <h1 className="text-4xl font-bold text-purple-400 mb-8">Mix Your Songs</h1>

      <div className="relative bg-gray-800 p-6 rounded-2xl shadow-lg w-full max-w-3xl flex flex-col items-center gap-6">
        {/* Song Upload Section */}
        <div className="flex space-x-8">
          {[1, 2].map((num) => (
            <div key={num} className="flex flex-col items-center">
              <h2 className="text-xl font-semibold mb-2">Song {num}</h2>
              <label className="bg-gray-700 p-6 rounded-2xl flex flex-col items-center justify-center cursor-pointer hover:bg-gray-600">
                <Icon path={mdiUpload} size={1.8} color="#b266ff" />
                <span className="mt-2">Upload</span>
                <input
                  type="file"
                  accept="audio/*"
                  className="hidden"
                  onChange={(e) => handleSongUpload(e, num)}
                />
              </label>
              <p className="mt-2 text-sm text-center w-32 truncate">
                {num === 1 && song1 ? song1.name : num === 2 && song2 ? song2.name : ""}
              </p>
            </div>
          ))}
        </div>

        {/* Mix Button */}
        <div className="flex w-max gap-4">
          <button
            onClick={handleMix}
            className={`bg-cyan-500 text-white font-semibold py-3 px-6 rounded-2xl transition-all duration-300 hover:bg-cyan-600 ${
              !(song1 && song2) ? "opacity-50 cursor-not-allowed" : ""
            }`}
            disabled={!(song1 && song2)}
          >
            Mix Songs
          </button>

          <button
            className="bg-cyan-500 text-white font-semibold py-3 px-6 rounded-2xl transition-all duration-300 hover:bg-cyan-600"
            onClick={random_song}
          >
            I'm feeling lucky
          </button>
        </div>


        {/* Mix Progress Bar */}
        {mixing && (
          <div className="w-80 mt-3">
            <div className="w-full bg-gray-700 h-3 rounded-full">
              <div
                className="bg-purple-500 h-3 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <p className="text-center mt-2 text-purple-400 font-medium">Mixing... {progress}%</p>
          </div>
        )}

        {/* Playback Controls */}
        {mixComplete && audioUrl && !mixing && (
          <div className="flex flex-col items-center mt-3 w-full">
            <div className="flex items-center space-x-4 w-full max-w-md">
              <button
                onClick={togglePlayback}
                className="bg-purple-500 text-white p-4 rounded-full hover:bg-purple-600"
              >
                <Icon path={playing ? mdiStop : mdiPlay} size={1} />
              </button>
              <div
                className="flex-1 bg-gray-700 h-3 rounded-full relative cursor-pointer"
                onClick={handleSeek}
              >
                <div
                  className="bg-purple-500 h-3 rounded-full"
                  style={{ width: duration ? `${(currentTime / duration) * 100}%` : "0%" }}
                ></div>
              </div>
              <p className="text-sm w-18 text-right">
                {formatTime(currentTime)} / {formatTime(duration)}
              </p>

               {/*volume control */}
              <input type="range" min="0" max="1" step="0.01" value={volume} onChange={handleVolumeChange} className="w-16 h-2 accent-purple-500" />
              <Icon path={mdiVolumeHigh} size={1} color="#b266ff" />

              <audio
                ref={audioRef}
                src={audioUrl}
                onTimeUpdate={handleTimeUpdate}
                onLoadedMetadata={handleLoadedMetadata}
                onEnded={() => setPlaying(false)}
              />
            </div>

            {/* Download Button */}
            <a
              href={audioUrl}
              download="RemixedSong.mp3"
              target="_blank"
              rel="noopener noreferrer"
              className="mt-4 bg-purple-500 text-white font-semibold py-2 px-4 rounded-2xl hover:bg-purple-600 transition-all duration-300"
            >
              <Icon path={mdiDownload} size={0.9} className="inline mr-2" />
              Download Remix
            </a>

            <button className="mt-4 bg-cyan-500 text-white font-semibold py-2 px-4 rounded-2xl hover:bg-cyan-600 transition-all duration-300"
              onClick={upload_to_db}>
              Add to playlist
            </button>

          </div>
        )}
      </div>
    </div>
  );
};

export default Mix;
