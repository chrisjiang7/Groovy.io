import { Link, useLocation } from "react-router-dom";
import { Home, Music, SlidersHorizontal, User } from "lucide-react";

const NavButtons = () => {
  const location = useLocation();
  
  const buttons = [
    { label: "Home", path: "/home", icon: <Home size={18} /> },
    { label: "Playlists", path: "/playlists", icon: <Music size={18} /> },
    { label: "Mix", path: "/mix", icon: <SlidersHorizontal size={18} /> },
    { label: "Profile", path: "/profile", icon: <User size={18} /> },
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 flex justify-center gap-6 p-4 bg-black/30 backdrop-blur-lg rounded-t-2xl shadow-lg">
      {buttons.map((btn) => {
        const isActive = 
          btn.path === "/playlists"
            ? location.pathname.startsWith("/playlists") // Match both `/playlists` and `/playlists/:id`
            : location.pathname === btn.path;

        return (
          <Link
            key={btn.label}
            to={btn.path}
            className={`flex items-center gap-2 px-5 py-2 rounded-2xl shadow-md transition-all duration-200
              ${
                isActive
                  ? "bg-cyan-600 scale-105 shadow-lg" // Active state
                  : "bg-purple-600/90 hover:bg-purple-700 hover:scale-105 hover:shadow-lg" // Default/hover states
              }`}
          >
            {btn.icon}
            <span className="text-sm font-medium">{btn.label}</span>
          </Link>
        );
      })}
    </div>
  );
};

export default NavButtons;
