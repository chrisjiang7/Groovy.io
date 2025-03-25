import { Outlet, useLocation } from "react-router-dom";
import NavButtons from "./NavButtons";

const Layout = () => {
  const location = useLocation();
  const hideNavButtons = location.pathname === "/" || location.pathname === "/signup";

  return (
    <div className="min-h-screen w-full flex flex-col justify-between bg-gradient-to-b from-black to-gray-900 text-white">
      {/* Main content area */}
      <div className="flex-grow flex items-center justify-center w-full">
        <Outlet />
      </div>

      {/* Show NavButtons only if NOT on login or signup pages */}
      {!hideNavButtons && <NavButtons />}
    </div>
  );
};

export default Layout;
