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
    <div className="fixed bottom-0 left-0 right-0 z-50 bg-[#1a1a1a] border-t border-cyan-900 shadow-[0_-1px_10px_rgba(0,0,0,0.5)]">
      <div className="flex justify-around items-center py-3 max-w-md mx-auto">
        {buttons.map((btn) => {
          const isActive = 
            btn.path === "/playlists"
              ? location.pathname.startsWith("/playlists")
              : location.pathname === btn.path;

          return (
            <Link
              key={btn.label}
              to={btn.path}
              className={`flex flex-col items-center gap-1 px-3 py-1 rounded-xl text-xs transition-all duration-200
                ${
                  isActive
                    ? "bg-cyan-800 text-white scale-105 shadow-md"
                    : "text-purple-300 hover:text-white hover:scale-105"
                }`}
            >
              {btn.icon}
              <span>{btn.label}</span>
            </Link>
          );
        })}
      </div>
    </div>
  );
};

export default NavButtons;
