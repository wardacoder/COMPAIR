import { useState } from "react";
import { Star, MessageCircle, CheckCircle, Send, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import API_BASE from "../config/api";

export default function FeedbackSection({ comparisonId, userId = "guest", hasPersonalization = false }) {
  const [isOpen, setIsOpen] = useState(false);
  const [hasBeenClicked, setHasBeenClicked] = useState(false);
  
  // Question 1: Accuracy rating (both scenarios)
  const [accuracyRating, setAccuracyRating] = useState(0);
  const [hoveredAccuracy, setHoveredAccuracy] = useState(0);
  
  // Question 2 for WITH preferences: Winner match rating
  const [winnerMatchRating, setWinnerMatchRating] = useState(0);
  const [hoveredWinnerMatch, setHoveredWinnerMatch] = useState(0);
  
  // Question 2 for WITHOUT preferences: Decision help
  const [decisionHelp, setDecisionHelp] = useState(null);
  
  // Question 3: What did you like? (both scenarios)
  const [whatLiked, setWhatLiked] = useState("");
  
  // Question 4: What could be improved? (both scenarios)
  const [improvement, setImprovement] = useState("");
  
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const decisionOptions = [
    { value: "yes", label: "Yes, I know what to choose now", emoji: "✅" },
    { value: "somewhat", label: "Somewhat, but I need more info", emoji: "🤔" },
    { value: "no", label: "No, still confused", emoji: "😕" }
  ];

  const getComprehensiveLabel = (rating) => {
    const labels = {
      1: "Very incomplete",
      2: "Missing key info",
      3: "Average",
      4: "Good coverage",
      5: "Very comprehensive"
    };
    return labels[rating] || "";
  };

  const getWinnerMatchLabel = (rating) => {
    const labels = {
      1: "Completely wrong for me",
      2: "Not a good match",
      3: "Okay match",
      4: "Good match",
      5: "Perfect match for my needs"
    };
    return labels[rating] || "";
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (accuracyRating === 0) {
      setError("Please rate how comprehensive the information was");
      return;
    }
    
    if (hasPersonalization && winnerMatchRating === 0) {
      setError("Please rate how well the winner matches your needs");
      return;
    }
    
    if (!hasPersonalization && !decisionHelp) {
      setError("Please select if this comparison helped you decide");
      return;
    }

    setLoading(true);
    setError(null);

    // Build comment from responses
    let commentParts = [];
    if (hasPersonalization) {
      commentParts.push(`Winner match: ${winnerMatchRating}/5 - ${getWinnerMatchLabel(winnerMatchRating)}`);
    } else {
      const selectedOption = decisionOptions.find(o => o.value === decisionHelp);
      commentParts.push(`Decision help: ${selectedOption?.label}`);
    }
    // Only add if there's actual content (not empty, not just whitespace, not just quotes)
    const likedText = whatLiked.trim();
    if (likedText && likedText.length > 0 && likedText !== '""' && likedText !== "''") {
      commentParts.push(`Liked: ${likedText}`);
    }
    const improvementText = improvement.trim();
    if (improvementText && improvementText.length > 0 && improvementText !== '""' && improvementText !== "''") {
      commentParts.push(`Improvement: ${improvementText}`);
    }

    try {
      const response = await fetch(`${API_BASE}/feedback`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          comparison_id: comparisonId,
          rating: accuracyRating,
          comment: commentParts.join(" | "),
          user_id: userId
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to submit feedback");
      }

      setSubmitted(true);
      
      // Close modal and reset after 2 seconds
      setTimeout(() => {
        setIsOpen(false);
        setTimeout(() => {
          setSubmitted(false);
          setAccuracyRating(0);
          setWinnerMatchRating(0);
          setDecisionHelp(null);
          setWhatLiked("");
          setImprovement("");
        }, 300);
      }, 2000);
      
    } catch (err) {
      console.error("Error submitting feedback:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const closeModal = () => {
    setIsOpen(false);
    setError(null);
  };

  // Check if form is valid for submission
  const isFormValid = () => {
    if (accuracyRating === 0) return false;
    if (hasPersonalization && winnerMatchRating === 0) return false;
    if (!hasPersonalization && !decisionHelp) return false;
    return true;
  };

  return (
    <>
      {/* Floating Feedback Button */}
      <motion.button
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8, duration: 0.4, ease: "easeOut" }}
        onClick={() => {
          setIsOpen(true);
          setHasBeenClicked(true);
        }}
        className="fixed bottom-6 right-6 z-40 flex items-center gap-2 px-5 py-3 
          bg-gradient-to-r from-indigo-600 to-purple-600 
          hover:from-indigo-700 hover:to-purple-700
          text-white font-semibold rounded-full shadow-lg hover:shadow-xl
          transition-all duration-300 transform hover:scale-105"
      >
        <MessageCircle className="w-5 h-5" />
        <span>Feedback</span>
        {/* Yellow blinker - disappears permanently once clicked */}
        {!hasBeenClicked && (
          <span className="flex h-3 w-3 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-yellow-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-yellow-400"></span>
          </span>
        )}
      </motion.button>

      {/* Modal Overlay */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={closeModal}
              className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
            />

            {/* Modal */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              transition={{ type: "spring", damping: 25, stiffness: 300 }}
              className="fixed inset-0 z-50 flex items-center justify-center p-4"
            >
              <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl w-full max-w-md max-h-[90vh] overflow-hidden flex flex-col">
                {/* Modal Header */}
                <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-4 flex items-center justify-between flex-shrink-0">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-white/20 rounded-lg">
                      <MessageCircle className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h2 className="text-xl font-bold text-white">Feedback</h2>
                      <p className="text-indigo-200 text-sm">Help us improve!</p>
                    </div>
                  </div>
                  <button
                    onClick={closeModal}
                    className="p-2 hover:bg-white/20 rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5 text-white" />
                  </button>
                </div>

                {/* Modal Body - Scrollable */}
                <div className="p-6 overflow-y-auto flex-1">
                  {submitted ? (
                    <motion.div
                      initial={{ scale: 0.8, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      className="text-center py-8"
                    >
                      <div className="w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
                        <CheckCircle className="w-10 h-10 text-green-600 dark:text-green-400" />
                      </div>
                      <h3 className="text-xl font-bold text-gray-800 dark:text-white mb-2">
                        Thank You! 🎉
                      </h3>
                      <p className="text-gray-600 dark:text-gray-400">
                        Your feedback helps us improve COMPAIR
                      </p>
                    </motion.div>
                  ) : (
                    <form onSubmit={handleSubmit} className="space-y-6">
                      {/* Question 1: Comprehensive Rating (Both scenarios) */}
                      <div>
                        <label className="block text-gray-800 dark:text-gray-200 font-medium mb-3">
                          1. How comprehensive was the information provided?
                        </label>
                        <div className="flex justify-center gap-2">
                          {[1, 2, 3, 4, 5].map((star) => (
                            <button
                              key={star}
                              type="button"
                              onClick={() => setAccuracyRating(star)}
                              onMouseEnter={() => setHoveredAccuracy(star)}
                              onMouseLeave={() => setHoveredAccuracy(0)}
                              className="transition-transform hover:scale-125 focus:outline-none"
                            >
                              <Star
                                className={`w-9 h-9 transition-colors ${
                                  star <= (hoveredAccuracy || accuracyRating)
                                    ? "fill-yellow-400 text-yellow-400"
                                    : "text-gray-300 dark:text-gray-600"
                                }`}
                              />
                            </button>
                          ))}
                        </div>
                        {accuracyRating > 0 && (
                          <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-2">
                            {getComprehensiveLabel(accuracyRating)}
                          </p>
                        )}
                      </div>

                      {/* Question 2: Conditional based on hasPersonalization */}
                      {hasPersonalization ? (
                        /* WITH PREFERENCES: Winner Match Rating */
                        <div>
                          <label className="block text-gray-800 dark:text-gray-200 font-medium mb-3">
                            2. How well does the winner match your needs?
                          </label>
                          <div className="flex justify-center gap-2">
                            {[1, 2, 3, 4, 5].map((star) => (
                              <button
                                key={star}
                                type="button"
                                onClick={() => setWinnerMatchRating(star)}
                                onMouseEnter={() => setHoveredWinnerMatch(star)}
                                onMouseLeave={() => setHoveredWinnerMatch(0)}
                                className="transition-transform hover:scale-125 focus:outline-none"
                              >
                                <Star
                                  className={`w-9 h-9 transition-colors ${
                                    star <= (hoveredWinnerMatch || winnerMatchRating)
                                      ? "fill-yellow-400 text-yellow-400"
                                      : "text-gray-300 dark:text-gray-600"
                                  }`}
                                />
                              </button>
                            ))}
                          </div>
                          {winnerMatchRating > 0 && (
                            <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-2">
                              {getWinnerMatchLabel(winnerMatchRating)}
                            </p>
                          )}
                        </div>
                      ) : (
                        /* WITHOUT PREFERENCES: Decision Help */
                        <div>
                          <label className="block text-gray-800 dark:text-gray-200 font-medium mb-3">
                            2. Did this comparison help you make a decision?
                          </label>
                          <div className="space-y-2">
                            {decisionOptions.map((option) => (
                              <button
                                key={option.value}
                                type="button"
                                onClick={() => setDecisionHelp(option.value)}
                                className={`w-full px-4 py-3 rounded-xl font-medium transition-all duration-200 flex items-center gap-3 text-left
                                  ${decisionHelp === option.value
                                    ? "bg-indigo-600 text-white shadow-lg"
                                    : "bg-gray-100 dark:bg-slate-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-slate-600"
                                  }`}
                              >
                                <span className="text-lg">{option.emoji}</span>
                                <span className="text-sm">{option.label}</span>
                              </button>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Question 3: What did you like? (Both scenarios) */}
                      <div>
                        <label className="block text-gray-800 dark:text-gray-200 font-medium mb-2">
                          3. What did you like? <span className="text-gray-400 font-normal">(Optional)</span>
                        </label>
                        <textarea
                          value={whatLiked}
                          onChange={(e) => setWhatLiked(e.target.value)}
                          placeholder="Tell us what you found helpful..."
                          className="w-full px-4 py-3 bg-gray-50 dark:bg-slate-700 border border-gray-200 dark:border-slate-600 rounded-xl text-gray-800 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none transition-all"
                          rows={2}
                        />
                      </div>

                      {/* Question 4: What could be improved? (Both scenarios) */}
                      <div>
                        <label className="block text-gray-800 dark:text-gray-200 font-medium mb-2">
                          4. What could be improved? <span className="text-gray-400 font-normal">(Optional)</span>
                        </label>
                        <textarea
                          value={improvement}
                          onChange={(e) => setImprovement(e.target.value)}
                          placeholder="Any suggestions for improvement..."
                          className="w-full px-4 py-3 bg-gray-50 dark:bg-slate-700 border border-gray-200 dark:border-slate-600 rounded-xl text-gray-800 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none transition-all"
                          rows={2}
                        />
                      </div>

                      {/* Error Message */}
                      {error && (
                        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
                          <p className="text-red-600 dark:text-red-400 text-sm text-center">{error}</p>
                        </div>
                      )}

                      {/* Submit Button */}
                      <button
                        type="submit"
                        disabled={loading || !isFormValid()}
                        className="w-full py-3 bg-gradient-to-r from-indigo-600 to-purple-600 
                          hover:from-indigo-700 hover:to-purple-700 
                          disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed 
                          text-white font-semibold rounded-xl 
                          transition-all duration-300 
                          flex items-center justify-center gap-2
                          shadow-lg hover:shadow-xl"
                      >
                        {loading ? (
                          <>
                            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                            Submitting...
                          </>
                        ) : (
                          <>
                            <Send className="w-5 h-5" />
                            Submit Feedback
                          </>
                        )}
                      </button>
                    </form>
                  )}
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
