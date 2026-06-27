import { Link, useLocation } from "react-router-dom";
import { Home, BarChart3, Sparkles } from "lucide-react";
import ThemeToggle from "./components/ThemeToggle";

export default function Navbar() {
  const location = useLocation();
  const isHomePage = location.pathname === "/";

  const isActive = (path) => {
    return location.pathname === path;
  };

  const navLinks = [
    { path: "/", label: "Home", icon: Home },
    { path: "/compare", label: "Compare", icon: Sparkles },
    { path: "/dashboard", label: "Dashboard", icon: BarChart3 },
  ];

  return (
    <nav className="w-full bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50 shadow-sm">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo - Hidden on homepage but placeholder keeps spacing */}
          <div className="w-40">
            {!isHomePage && (
              <Link to="/" className="flex items-center gap-2 group">
                <div className="p-2 bg-gradient-to-r from-blue-600 to-sky-500 rounded-lg group-hover:scale-110 transition-transform">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold">
                  <span className="bg-gradient-to-r from-blue-600 to-sky-500 bg-clip-text text-transparent">
                    COMP
                  </span>
                  <span className="bg-gradient-to-r from-purple-500 to-pink-400 bg-clip-text text-transparent">
                    AI
                  </span>
                  <span className="bg-gradient-to-r from-sky-500 to-blue-600 bg-clip-text text-transparent">
                    R
                  </span>
                </span>
              </Link>
            )}
          </div>

          {/* Navigation Links - Centered */}
          <div className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const active = isActive(link.path);
              
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
                    active
                      ? "bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300"
                      : "text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span>{link.label}</span>
                </Link>
              );
            })}
          </div>

          {/* Mobile Navigation */}
          <div className="flex md:hidden items-center gap-2">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const active = isActive(link.path);
              
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`p-2 rounded-lg transition-all ${
                    active
                      ? "bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300"
                      : "text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                  }`}
                  title={link.label}
                >
                  <Icon className="w-5 h-5" />
                </Link>
              );
            })}
          </div>

          {/* Theme Toggle - Inline version */}
          <div className="w-40 flex justify-end">
            <ThemeToggle />
          </div>
        </div>
      </div>
    </nav>
  );
}

