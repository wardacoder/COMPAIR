import { Sun, Moon } from "lucide-react";
import { useTheme } from "../App";

export default function ThemeToggle() {
  const { darkMode, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="fixed top-6 right-6 z-50 p-3 rounded-full 
        bg-white dark:bg-slate-800 
        border-2 border-gray-200 dark:border-slate-700
        shadow-lg hover:shadow-xl
        transition-all duration-300 ease-in-out
        hover:scale-110 active:scale-95
        group"
      aria-label="Toggle theme"
    >
      {darkMode ? (
        <Sun className="w-5 h-5 text-yellow-500 transition-transform group-hover:rotate-180 duration-500" />
      ) : (
        <Moon className="w-5 h-5 text-slate-700 transition-transform group-hover:-rotate-12 duration-300" />
      )}
    </button>
  );
}