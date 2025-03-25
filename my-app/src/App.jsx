import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Playlists from "./pages/Playlists";
import Playlist_page from "./pages/Playlist_page";
import Mix from "./pages/Mix";
import Profile from "./pages/Profile";
import SignUp from "./pages/SignUp";

const App = () => {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Login />} />
        <Route path="home" element={<Home />} />
        <Route path="login" element={<Login />} />
        <Route path="playlists" element={<Playlists />} />
        <Route path="playlists/:id" element={<Playlist_page />} />
        <Route path="mix" element={<Mix />} />
        <Route path="profile" element={<Profile />} />
        <Route path="signup" element={<SignUp />} />
      </Route>
    </Routes>
  );
};

export default App;
