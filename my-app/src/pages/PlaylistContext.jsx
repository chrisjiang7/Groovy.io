import React, { createContext, useState, useContext  } from "react";

// Create Context
export const PlaylistContext = createContext();

export const PlaylistProvider = ({ children }) => {
	const [playlists, setPlaylists] = useState([
    { id: 1, name: "Remixes" },
    { id: 2, name: "Workout" },
    { id: 3, name: "pop" },
    { id: 4, name: "rap" },
    { id: 5, name: "Top Hits 2025" },
    { id: 6, name: "hiphop" },
    { id: 7, name: "2024 hits" },
    { id: 8, name: "beats" },
    { id: 9, name: "event" },
    { id: 10, name: "weekend" },
    { id: 11, name: "graduation" },
    { id: 12, name: "2023 hits" },
    { id: 13, name: "random songs" },
    { id: 14, name: "2022 hits" },
    { id: 15, name: "throwbacks" },
    { id: 16, name: "2021 hits" },
    { id: 17, name: "2020 favorites" },
    { id: 18, name: "covid era" },
    { id: 19, name: "2019 throwbacks" },
    { id: 20, name: "2019 hits" }
    //add more to test scrollbar functionality
  ]);

	return (
    <PlaylistContext.Provider value={{ playlists, setPlaylists }}>
      {children}
    </PlaylistContext.Provider>
  );
};

export const usePlaylists = () => {
  return useContext(PlaylistContext);
};