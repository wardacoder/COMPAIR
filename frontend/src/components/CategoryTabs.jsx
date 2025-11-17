// ✅ NEW CATEGORIES: gadgets, cars, technologies, destinations, shows, other
const categories = ["gadgets", "cars", "technologies", "destinations", "shows", "other"];

export default function CategoryTabs({ selected, onChange }) {
  return (
    <div className="w-full max-w-4xl mb-8">
      {/* Category selector */}
      <div className="flex flex-wrap justify-center gap-3">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => onChange(cat)}
            className={`px-6 py-3 rounded-full capitalize font-semibold
              shadow-md transition-all duration-300
              focus:outline-none focus:ring-2 focus:ring-offset-2
              ${
                selected === cat
                  ? "bg-gradient-to-r from-blue-600 to-sky-500 text-white scale-105 shadow-lg focus:ring-blue-400"
                  : "bg-white dark:bg-slate-800 text-gray-700 dark:text-gray-300 hover:bg-blue-50 dark:hover:bg-slate-700 hover:text-blue-600 dark:hover:text-sky-400 hover:shadow-lg hover:scale-105 focus:ring-gray-300"
              }`}
          >
            {cat}
          </button>
        ))}
      </div>
    </div>
  );
}