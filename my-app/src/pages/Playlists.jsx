import { useState } from "react";
import React, { Component } from 'react';
import Icon from '@mdi/react';
import { mdiPlaylistMusic } from '@mdi/js';
import { useNavigate } from "react-router-dom";
import { usePlaylists } from "./PlaylistContext"



const Playlists = () => {
  const navigate = useNavigate();
  const { playlists } = usePlaylists();

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
