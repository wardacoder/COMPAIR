import { Sun, Moon } from "lucide-react";
import { useTheme } from "../App";

export default function ThemeToggle() {
  const { darkMode, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="p-2 rounded-lg
        bg-gray-100 dark:bg-slate-700 
        border border-gray-200 dark:border-slate-600
        hover:bg-gray-200 dark:hover:bg-slate-600
        transition-all duration-300 ease-in-out
        hover:scale-105 active:scale-95
        group"
      aria-label="Toggle theme"
    >
      {darkMode ? (
        <Sun className="w-4 h-4 text-yellow-500 transition-transform group-hover:rotate-180 duration-500" />
      ) : (
        <Moon className="w-4 h-4 text-slate-700 transition-transform group-hover:-rotate-12 duration-300" />
      )}
    </button>
  );
}