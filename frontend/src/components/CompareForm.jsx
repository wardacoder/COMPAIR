import { useRef, useEffect } from "react";
import { Settings, ChevronDown, ChevronUp, Lightbulb } from "lucide-react";

export default function CompareForm({ 
  category, 
  items, 
  setItems, 
  criteria, 
  setCriteria,
  userPreferences,
  setUserPreferences,
  showPreferences,
  setShowPreferences,
  onCompare,  
  isComparing  
}) {
  
  const categoryText = {
    gadgets: {
      itemLabel: "Gadget",
      placeholder: "e.g., iPhone 15 Pro Max, Galaxy S24 Ultra",
      hint: "Be specific with model names and specs. Compare similar items (e.g., iPhone 15 vs Samsung S24, not iPhone vs Car)",
      priorityOptions: ["Price", "Performance", "Battery Life", "Camera Quality", "Display", "Build Quality", "Brand", "Features"],
      useCaseLabel: "How will you use it?",  
      useCasePlaceholder: "e.g., gaming, photography, work, daily use"
    },
    cars: {
      itemLabel: "Car",
      placeholder: "e.g., Tesla Model 3, Toyota Camry 2024",
      hint: "Include full model name and year. Compare vehicles of similar types (e.g., Tesla Model 3 vs BMW 3 Series)",
      priorityOptions: ["Price", "Fuel Efficiency", "Safety", "Performance", "Reliability", "Features", "Comfort", "Cargo Space"],
      useCaseLabel: "What's your driving need?",  
      useCasePlaceholder: "e.g., daily commute, family trips, business travel, off-roading"
    },
    technologies: {
      itemLabel: "Technology",
      placeholder: "e.g., React, Python, AWS, ChatGPT",
      hint: "Use full names of languages, frameworks, or platforms. Compare similar tech (e.g., React vs Vue, not React vs Java)",
      priorityOptions: ["Learning Curve", "Performance", "Community Support", "Job Market", "Ecosystem", "Scalability", "Documentation", "Cost"],
      useCaseLabel: "What will you build?",  
      useCasePlaceholder: "e.g., startup project, enterprise app, personal website, mobile app"
    },
    destinations: {
      itemLabel: "Destination",
      placeholder: "e.g., Japan, Maldives, New York City",
      hint: "Use full country or city names. Compare similar destination types (e.g., beach destinations, cities, countries)",
      priorityOptions: ["Cost", "Safety", "Weather", "Attractions", "Culture", "Food", "Visa Requirements", "Activities"],
      useCaseLabel: "What type of trip?",  
      useCasePlaceholder: "e.g., honeymoon, family vacation, solo adventure, business trip"
    },
    shows: {
      itemLabel: "Show",
      placeholder: "e.g., Breaking Bad, Game of Thrones S1",
      hint: "Include show titles and season if comparing seasons.",
      priorityOptions: ["Plot", "Acting", "Production Quality", "Genre", "Length", "Ratings", "Rewatch Value", "Ending"],
      useCaseLabel: "What's your viewing style?",  
      useCasePlaceholder: "e.g., binge watching, casual viewing, background noise, serious watching"
    },
    other: {
      itemLabel: "Item",
      placeholder: "e.g., Udemy Python Course, MrBeast Channel",
      hint: "Be descriptive and specific. This category is flexible—compare courses, services, books, or anything comparable!",
      priorityOptions: ["Quality", "Price", "Value", "Popularity", "Ease of Use", "Features", "Accessibility", "Satisfaction"],
      useCaseLabel: "What's your goal?",  // ✅ General
      useCasePlaceholder: "e.g., learn new skill, entertainment, personal growth, professional development"
    },
  };

  const current = categoryText[category] || categoryText["other"];

  const handleItemChange = (index, value) => {
    const newItems = [...items];
    newItems[index] = value;
    setItems(newItems);
  };

  const addItem = () => {
    if (items.length < 4) setItems([...items, ""]);
  };

  const removeItem = (index) => {
    const newItems = items.filter((_, i) => i !== index);
    setItems(newItems);
  };

  const displayCategory = category === "other" ? "items" : `${category}`;

  const handlePriorityToggle = (priority) => {
    const newPriorities = userPreferences.priorities.includes(priority)
      ? userPreferences.priorities.filter(p => p !== priority)
      : [...userPreferences.priorities, priority];
    
    setUserPreferences({
      ...userPreferences,
      priorities: newPriorities
    });
  };

  // ✅ NEW: Check if at least 2 items are filled
  const hasAtLeastTwoItems = items.filter(item => item.trim().length > 0).length >= 2;

  return (
    <div className="w-full max-w-4xl mt-8">
      {/* Subheading */}
      <div className="text-center mb-6">
        <p className="text-gray-700 dark:text-gray-300 text-lg leading-relaxed mb-4">
          Compare your{" "}
          <span className="text-blue-600 dark:text-sky-400 font-semibold capitalize">
            {displayCategory}
          </span>{" "}
          below — add up to 4 items.
        </p>
        
        {/* ✅ COMPACT: Single merged tip box */}
        <div className="max-w-3xl mx-auto p-3 bg-blue-50 dark:bg-blue-900/20 
          border border-blue-200 dark:border-blue-800 rounded-xl">
          <div className="flex items-start gap-2">
            <Lightbulb className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-blue-800 dark:text-blue-200 text-left leading-relaxed">
              <strong> Pro tip:</strong> {current.hint}
            </p>
          </div>
        </div>
      </div>

      {/* Input fields */}
      <div className="flex flex-wrap justify-center items-center gap-4 mb-6">
        {items.map((item, index) => (
          <div key={index} className="flex items-center gap-2">
            <input
              type="text"
              value={item}
              onChange={(e) => handleItemChange(index, e.target.value)}
              placeholder={current.placeholder}
              className="w-48 sm:w-56 p-3.5 border-2 border-gray-300 dark:border-slate-600 
                rounded-2xl shadow-sm 
                focus:ring-2 focus:ring-blue-500 focus:border-blue-500 
                dark:bg-slate-800 dark:text-white 
                dark:focus:ring-sky-400 dark:focus:border-sky-400
                transition-all text-center font-medium
                placeholder:text-gray-400 dark:placeholder:text-gray-500
                placeholder:text-xs"
            />
            {index >= 2 && (
              <button
                onClick={() => removeItem(index)}
                className="flex items-center justify-center w-9 h-9 rounded-full 
                  border-2 border-gray-300 dark:border-slate-600
                  text-gray-500 hover:text-red-500 hover:border-red-400 
                  dark:text-gray-400 dark:hover:text-red-400 dark:hover:border-red-500
                  transition-all duration-200 hover:scale-110"
                title="Remove this item"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2.5}
                  stroke="currentColor"
                  className="w-4 h-4"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>
        ))}
      </div>

      {/* Add item button */}
      {items.length < 4 && (
        <div className="text-center mb-8">
          <button
            onClick={addItem}
            className="px-6 py-3 rounded-full border-2 border-gray-300 dark:border-slate-600
              text-gray-700 dark:text-gray-300
              bg-white dark:bg-slate-800
              hover:bg-gray-50 dark:hover:bg-slate-700 
              hover:border-blue-400 dark:hover:border-sky-500
              shadow-sm hover:shadow-md
              transition-all duration-200 font-medium"
          >
            + Add Another {current.itemLabel}
          </button>
        </div>
      )}

      {/* User Preferences Section */}
      <div className="mt-8">
        <div className="text-center">
          <button
            onClick={() => setShowPreferences(!showPreferences)}
            className="inline-flex items-center justify-center gap-2 px-8 py-4 
              bg-gradient-to-r from-purple-600 to-pink-600 
              hover:from-purple-700 hover:to-pink-700
              text-white rounded-full 
              font-semibold shadow-lg hover:shadow-xl
              transition-all duration-300
              transform hover:scale-105 active:scale-95"
          >
            <Settings className="w-5 h-5" />
            <span>What matters most to you?</span>
            {showPreferences ? (
              <ChevronUp className="w-5 h-5" />
            ) : (
              <ChevronDown className="w-5 h-5" />
            )}
          </button>
        </div>

        {/* Preferences Form */}
        {showPreferences && (
          <div className="mt-6 p-8 bg-gradient-to-br from-purple-50 via-pink-50 to-purple-50
            dark:from-slate-800 dark:via-slate-850 dark:to-slate-800
            rounded-3xl shadow-xl 
            border-2 border-purple-200 dark:border-slate-700">
            
            <div className="text-center mb-6">
              <h3 className="text-2xl font-bold text-gray-800 dark:text-gray-100 mb-2">
                🎯 Personalize Your Comparison
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Tell us what's important to you, and we'll identify the best choice for your needs!
              </p>
            </div>

            {/* Priority Checkboxes - FIRST */}
            <div className="mb-8">
              <label className="block text-base font-semibold text-gray-800 dark:text-gray-200 mb-4">
                What features matter most? <span className="text-purple-600 dark:text-purple-400">(Select all that apply)</span>
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                {current.priorityOptions.map((priority) => (
                  <label
                    key={priority}
                    className={`flex items-center gap-2 p-3 rounded-xl border-2 
                      cursor-pointer transition-all duration-200
                      ${userPreferences.priorities.includes(priority)
                        ? 'bg-purple-100 dark:bg-purple-900/30 border-purple-500 dark:border-purple-600'
                        : 'bg-white dark:bg-slate-800 border-gray-200 dark:border-slate-600 hover:border-purple-300 dark:hover:border-purple-700'
                      }
                      hover:shadow-md`}
                  >
                    <input
                      type="checkbox"
                      checked={userPreferences.priorities.includes(priority)}
                      onChange={() => handlePriorityToggle(priority)}
                      className="w-4 h-4 text-purple-600 border-gray-300 rounded 
                        focus:ring-2 focus:ring-purple-500 cursor-pointer"
                    />
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      {priority}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            {/* Budget Input - SECOND */}
            <div className="mb-6">
              <label className="block text-base font-semibold text-gray-800 dark:text-gray-200 mb-2">
                Budget <span className="text-sm font-normal text-gray-500">(optional)</span>
              </label>
              <input
                type="text"
                value={userPreferences.budget}
                onChange={(e) => setUserPreferences({
                  ...userPreferences,
                  budget: e.target.value
                })}
                placeholder="e.g., under $1000, around $500, no limit"
                className="w-full p-4 border-2 border-gray-300 dark:border-slate-600 
                  rounded-xl shadow-sm 
                  focus:ring-2 focus:ring-purple-500 focus:border-purple-500 
                  dark:bg-slate-800 dark:text-white 
                  dark:focus:ring-purple-400 dark:focus:border-purple-400
                  transition-all"
              />
            </div>

            {/* ✅ UPDATED: Use Case Input - Category-specific label and placeholder */}
            <div className="mb-6">
              <label className="block text-base font-semibold text-gray-800 dark:text-gray-200 mb-2">
                {current.useCaseLabel} <span className="text-sm font-normal text-gray-500">(optional)</span>
              </label>
              <input
                type="text"
                value={userPreferences.use_case}
                onChange={(e) => setUserPreferences({
                  ...userPreferences,
                  use_case: e.target.value
                })}
                placeholder={current.useCasePlaceholder}
                className="w-full p-4 border-2 border-gray-300 dark:border-slate-600 
                  rounded-xl shadow-sm 
                  focus:ring-2 focus:ring-purple-500 focus:border-purple-500 
                  dark:bg-slate-800 dark:text-white 
                  dark:focus:ring-purple-400 dark:focus:border-purple-400
                  transition-all"
              />
            </div>

            {/* Helper Text */}
            <div className="text-center pt-4 border-t border-purple-200 dark:border-slate-700">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                💡 <strong>The more you share, the better we can personalize your recommendation!</strong>
              </p>
            </div>
          </div>
        )}
      </div>

      {/* ✅ NEW: Compare Now Button with disabled state */}
      <div className="mt-8 text-center">
        <button
          onClick={onCompare}
          disabled={!hasAtLeastTwoItems || isComparing}
          className={`inline-flex items-center justify-center gap-3 px-10 py-4 
            rounded-full text-lg font-bold 
            shadow-xl hover:shadow-2xl
            focus:outline-none focus:ring-4 focus:ring-blue-300 
            dark:focus:ring-sky-500 
            transition-all duration-300
            ${hasAtLeastTwoItems && !isComparing
              ? 'bg-gradient-to-r from-blue-600 via-sky-500 to-blue-600 bg-[length:200%_auto] text-white hover:bg-[position:right_center] cursor-pointer transform hover:scale-105 active:scale-95'
              : 'bg-gray-300 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed opacity-60'
            }`}
        >
          {isComparing ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Comparing...</span>
            </>
          ) : (
            <>
              {!hasAtLeastTwoItems && (
                <span className="text-sm">Enter at least 2 items to compare</span>
              )}
              {hasAtLeastTwoItems && <span>Compare Now</span>}
            </>
          )}
        </button>
      </div>
    </div>
  );

}
