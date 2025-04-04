import React, { useState, useEffect, useRef, useContext  } from "react";
import { useParams, useLocation, useNavigate } from "react-router-dom"; 
import { MdPlayArrow, MdDelete, MdPause, MdVolumeUp, MdVolumeOff } from "react-icons/md";
import { mdiArrowLeftTopBold } from "@mdi/js"; 
import Icon from "@mdi/react"; 
import { usePlaylists } from "./PlaylistContext"

const Playlist_page = () => {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate(); 
  const [data, setData] = useState([]);
  const [currentSong, setCurrentSong] = useState({ url: null, name: "" });
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const audioRef = useRef(null);
  const playlistName = location.state?.name || "Unknown Playlist";
  const { playlists  } = usePlaylists();
  const [selectedPlaylists, setSelectedPlaylists] = useState({});

  useEffect(() => {
    list_songs(playlistName);
  }, []);

  const list_songs = (playlist_name) => {
    fetch(`http://127.0.0.1:5000/api/list_songs/${playlist_name}`)
      .then((response) => response.json())
      .then((data) => setData(data))
      .catch((error) => console.error("Error fetching songs:", error));
  };

  const get_song_db = (filename) => {
    const audioUrl = `http://127.0.0.1:5000/api/get_song_db/${filename}`;
    setCurrentSong({ url: audioUrl, name: filename });
    setIsPlaying(true);
  };

  useEffect(() => {
    if (audioRef.current && isPlaying) {
      audioRef.current.play().catch((error) => console.log("Autoplay blocked:", error));
    }
  }, [currentSong.url]);

  const delete_song_db = (filename) => {
    fetch(`http://127.0.0.1:5000/api/delete_song_db/${filename}`)
      .then((response) => response.json())
      .then(() => list_songs(playlistName))
      .catch((error) => console.error("Delete error:", error));
  };

  const move_song = (filename,playlist_name) => {
    fetch(`http://127.0.0.1:5000/api/move_song/${filename}/${playlist_name}`)
      .then((response) => response.json())
      .then(() => list_songs(playlistName))
      .catch((error) => console.error("Move error:", error));
  };

  const closePlayer = () => {
    setCurrentSong({ url: null, name: "" });
    setIsPlaying(false);
  };

  const togglePlay = () => {
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const updateProgress = () => {
    setCurrentTime(audioRef.current.currentTime);
    setDuration(audioRef.current.duration || 0);
  };

  const changeProgress = (e) => {
    const newTime = (e.target.value / 100) * duration;
    audioRef.current.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const changeVolume = (e) => {
    const newVolume = e.target.value;
    audioRef.current.volume = newVolume;
    setVolume(newVolume);
  };

  const handleSelectChange = (e, filename) => {
    const selectedId = e.target.value;
    const selectedPlaylist = playlists.find((pl) => pl.id === parseInt(selectedId));
    if (selectedPlaylist) {
      setSelectedPlaylists((prevState) => ({
        ...prevState,
        [filename]: selectedId, 
      }));
      move_song(filename, selectedPlaylist.name);
    }
  };

  return (
    <div className="max-w-3x1 mx-auto p-6 bg-gray-900 text-white rounded-lg shadow-lg">
      {/* Return to Playlists Button */}
      <button
        onClick={() => navigate("/playlists")} 
        className="mb-4 px-4 py-2 flex items-center gap-2 bg-purple-600 hover:bg-purple-500 rounded-lg text-white font-medium transition-all"
      >
        <Icon path={mdiArrowLeftTopBold} size={1} /> {/*Icon added here */}
        Return to Playlists
      </button>

      <h1 className="text-2xl font-bold text-purple-400 mb-2">{playlistName}</h1>
      <p className="text-gray-400 mb-6">Playlist ID: {id}</p>

      {!currentSong.url ? (
        <div className="h-64 overflow-y-auto p-3 bg-gray-800 rounded-lg">
          {data.length > 0 ? (
            <ul className="space-y-3">
              {data.map((item, index) => (
                <li key={index} className="flex justify-between items-center bg-gray-700 p-3 rounded-md">
                  <span className="text-white">{item.filename}</span>
                  {/* <span className="text-gray-400 text-sm">Added on: {item.stored_date}</span> */}
                  <div className="flex gap-3">
                    <MdPlayArrow
                      className="text-green-400 cursor-pointer hover:text-green-300 text-2xl"
                      onClick={() => get_song_db(item.filename)}
                    />
                    <MdDelete
                      className="text-red-400 cursor-pointer hover:text-red-300 text-2xl"
                      onClick={() => delete_song_db(item.filename)}
                    />
                    <select className="ml-2 p-1 border rounded bg-gray-900" defaultValue=""
                      value={selectedPlaylists[item.filename] || ""}
                      onChange={(e) => handleSelectChange(e, item.filename)}
                    > 
                      <option className="text-white" value="" disabled>Move to...</option>
                      {playlists.map((pl) => (
                        <option key={pl.id} value={pl.id}>{pl.name}</option>
                      ))}
                    </select>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-400 text-center">No songs found...</p>
          )}
        </div>
      ) : (
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-bold text-purple-400">Now Playing...</h2>
          <p className="text-white text-lg mt-2 truncate">{currentSong.name}</p>

          {/* Custom Audio Player */}
          <div className="w-full min-w-[300px] bg-gray-700 rounded-lg p-4 mb-6 flex flex-col items-center">
            <audio
              ref={audioRef}
              src={currentSong.url}
              onTimeUpdate={updateProgress}
              onLoadedMetadata={updateProgress}
            />

            {/* Play/Pause Button */}
            <button onClick={togglePlay} className="mb-3">
              {isPlaying ? (
                <MdPause className="text-white text-4xl cursor-pointer" />
              ) : (
                <MdPlayArrow className="text-white text-4xl cursor-pointer" />
              )}
            </button>

            {/* Progress Bar */}
            <input
              type="range"
              value={duration ? (currentTime / duration) * 100 : 0}
              onChange={changeProgress}
              className="w-full appearance-none h-2 bg-gray-500 rounded-lg cursor-pointer"
            />

            {/* Time Display */}
            <div className="flex justify-between w-full text-gray-300 text-sm mt-2">
              <span>{formatTime(currentTime)}</span>
              <span>{formatTime(duration)}</span>
            </div>

            {/* Volume Control */}
            <div className="flex items-center w-full mt-4">
              {volume > 0 ? (
                <MdVolumeUp className="text-white text-xl mr-2" />
              ) : (
                <MdVolumeOff className="text-white text-xl mr-2" />
              )}
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={volume}
                onChange={changeVolume}
                className="w-full appearance-none h-2 bg-gray-500 rounded-lg cursor-pointer"
              />
            </div>
          </div>

          <button
            onClick={closePlayer}
            className="mb-4 px-4 py-2 flex items-center gap-2 bg-cyan-600 hover:bg-cyan-500 rounded-lg text-white font-medium transition-all"
      >
        	<Icon path={mdiArrowLeftTopBold} size={1} /> {/* ✅ MDI Icon added here */}
        	Return to {playlistName}
          </button>
        </div>
      )}
    </div>
  );
};

// Format Time Function
const formatTime = (seconds) => {
  if (!seconds) return "0:00";
  const minutes = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${minutes}:${secs < 10 ? "0" : ""}${secs}`;
};

export default Playlist_page;
