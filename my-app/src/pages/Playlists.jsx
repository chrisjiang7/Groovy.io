import { useState } from "react";
import React, { Component } from 'react';
import Icon from '@mdi/react';
import { mdiPlaylistMusic } from '@mdi/js';
import { useNavigate } from "react-router-dom";

const Playlists = () => {
  const navigate = useNavigate();
  
  const [playlists, setPlaylists] = useState([
    { id: 1, name: "Remixes" },
    { id: 2, name: "Workout" },
    { id: 3, name: "pop" },
    { id: 4, name: "rap" },
    { id: 5, name: "Top Hits 2025" },
    { id: 6, name: "hiphop" },
    { id: 7, name: "2024 hits" },
    { id: 8, name: "beats" },
    { id: 9, name: "birthday" },
    { id: 10, name: "wedding" },
    { id: 11, name: "graduation" },
    { id: 12, name: "2023 hits" },
    { id: 5, name: "random songs" },
    { id: 6, name: "2022 hits" },
    { id: 7, name: "throwbacks" },
    { id: 8, name: "2021 hits" },
    { id: 9, name: "2020 favorites" },
    { id: 10, name: "covid era" },
    { id: 11, name: "2019 throwbacks" },
    { id: 12, name: "2019 hits" }
    //add more to test scrollbar functionality
  ]);

  return (
    <div className="flex flex-col items-center p-8 pb-20">
      <h1 className="text-4xl font-bold mb-8 text-purple-400">Your Playlists</h1>
      {/* scrollable grid container */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 overflow-y-auto p-4 w-full max-h-[65vh]">
        {playlists.map((playlist) => (
          <div
            key={playlist.id}
            className="bg-gray-800 p-4 rounded-xl shadow-lg hover:shadow-purple-500/50 hover:scale-105 transition-all duration-300 flex flex-col items-center"
            onClick={() => navigate(`/playlists/${playlist.id}`, { state: { name: playlist.name } })}
          >
            <Icon
              path={mdiPlaylistMusic}
              title="Playlist Icon"
              size={3}
              color="#a855f7"
              horizontal
            />
            <h2 className="text-lg font-semibold">{playlist.name}</h2>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Playlists;
