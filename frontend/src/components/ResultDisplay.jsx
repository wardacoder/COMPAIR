import { useState } from "react";
import {
  ClipboardList,
  Table,
  ThumbsUp,
  ThumbsDown,
  Lightbulb,
  Save,
  FileDown,
  RefreshCcw,
  Trophy,
  Sparkles,
  Share2,
  Check,
} from "lucide-react";
import FollowUpChat from "../components/FollowUpChat";

export default function ResultDisplay({ result, onSave, onExport, onReset }) {
  const [shareUrl, setShareUrl] = useState(null);
  const [shareLoading, setShareLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleShare = async () => {
    setShareLoading(true);
    try {
      const response = await fetch("http://127.0.0.1:8000/share-comparison", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          category: result.category || "other",
          items: result.items || [],
          result: result,
          user_id: "guest123"
        })
      });
      
      const data = await response.json();
      setShareUrl(data.share_url);
      
      navigator.clipboard.writeText(data.share_url);
      setCopied(true);
      setTimeout(() => setCopied(false), 3000);
      
    } catch (error) {
      console.error("Share error:", error);
      alert("Failed to create share link");
    } finally {
      setShareLoading(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(shareUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 3000);
  };

  if (!result) return null;

  if (result.message) {
    return (
      <div className="w-full max-w-4xl mt-10 mx-auto">
        <div className="p-8 text-center 
          bg-white dark:bg-slate-800 
          rounded-3xl shadow-xl 
          border-2 border-blue-100 dark:border-slate-700">
          <p className="text-gray-800 dark:text-gray-200 text-lg leading-relaxed mb-6">
            {result.message}
          </p>
          <button
            onClick={onReset}
            className="inline-flex items-center gap-2 
              bg-gradient-to-r from-blue-600 to-sky-500
              hover:from-blue-700 hover:to-sky-600
              text-white px-6 py-3 rounded-full font-semibold
              shadow-lg hover:shadow-xl
              transition-all duration-300
              transform hover:scale-105 active:scale-95"
          >
            <RefreshCcw className="w-4 h-4" /> Try Again
          </button>
        </div>
      </div>
    );
  }

  const hasTable = Array.isArray(result.table) && result.table.length > 0;
  const hasPros = Array.isArray(result.pros) && result.pros.length > 0;
  const hasCons = Array.isArray(result.cons) && result.cons.length > 0;
  const hasWinner = result.personalized_winner && result.winner_reason;

  return (
    <div className="w-full max-w-4xl mt-10 p-8 
      bg-white dark:bg-slate-800 
      rounded-3xl shadow-2xl 
      border-2 border-blue-100 dark:border-slate-700 
      text-left transition-all duration-300">
      
      {/* Personalized Winner Badge */}
      {hasWinner && (
        <div className="mb-10 p-6 
          bg-gradient-to-r from-yellow-50 via-amber-50 to-orange-50 
          dark:from-yellow-900/20 dark:via-amber-900/20 dark:to-orange-900/20 
          rounded-2xl border-2 border-yellow-400 dark:border-yellow-600 
          shadow-lg">
          
          <div className="flex items-center justify-center gap-3 mb-4">
            <Trophy className="w-8 h-8 text-yellow-600 dark:text-yellow-400 animate-pulse" />
            <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
              Personalized Winner
            </h2>
            <Sparkles className="w-6 h-6 text-yellow-600 dark:text-yellow-400 animate-pulse" />
          </div>
          
          <div className="text-center mb-4">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2 font-medium">
              Based on your preferences, the best choice for you is:
            </p>
            <p className="text-3xl font-extrabold text-transparent bg-clip-text 
              bg-gradient-to-r from-yellow-600 via-orange-600 to-red-600 
              dark:from-yellow-400 dark:via-orange-400 dark:to-red-400
              drop-shadow-sm">
              {result.personalized_winner}
            </p>
          </div>
          
          <div className="bg-white dark:bg-slate-800 rounded-xl p-5 
            border-2 border-yellow-200 dark:border-yellow-700 shadow-sm">
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              <strong className="text-yellow-700 dark:text-yellow-400 text-lg">Why?</strong>{" "}
              {result.winner_reason}
            </p>
          </div>
        </div>
      )}

      {/* Introduction */}
      {result.introduction && (
        <div className="mb-10 pb-8 border-b-2 border-gray-200 dark:border-slate-700">
          <div className="flex items-center gap-2 mb-4">
            <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              <ClipboardList className="w-5 h-5 text-blue-600 dark:text-sky-400" />
            </div>
            <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
              Introduction
            </h2>
          </div>
          <p className="text-gray-700 dark:text-gray-300 leading-relaxed text-lg">
            {result.introduction}
          </p>
        </div>
      )}

      {/* Comparison Table */}
      {hasTable ? (
        <div className="mb-10 pb-8 border-b-2 border-gray-200 dark:border-slate-700">
          <div className="flex items-center gap-2 mb-4">
            <div className="p-2 bg-sky-100 dark:bg-sky-900/30 rounded-lg">
              <Table className="w-5 h-5 text-sky-600 dark:text-sky-400" />
            </div>
            <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
              Comparison Table
            </h2>
          </div>

          <div className="overflow-x-auto rounded-xl shadow-md">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="bg-gradient-to-r from-blue-100 to-sky-100 
                  dark:from-slate-700 dark:to-slate-600">
                  <th className="border-2 border-blue-200 dark:border-slate-600 
                    px-4 py-3 text-left font-bold text-gray-800 dark:text-gray-100">
                    Feature
                  </th>
                  {result.table?.[0] &&
                    Object.keys(result.table[0])
                      .filter((key) => key !== "feature")
                      .map((key) => (
                        <th
                          key={key}
                          className="border-2 border-blue-200 dark:border-slate-600 
                            px-4 py-3 text-left font-bold text-gray-800 dark:text-gray-100 capitalize"
                        >
                          {key}
                          {hasWinner && key === result.personalized_winner && (
                            <span className="ml-2 text-xl">👑</span>
                          )}
                        </th>
                      ))}
                </tr>
              </thead>
              <tbody>
                {result.table.map((row, idx) => (
                  <tr
                    key={idx}
                    className={`transition-colors
                      ${idx % 2 === 0
                        ? "bg-blue-50/50 dark:bg-slate-800/50"
                        : "bg-white dark:bg-slate-900/50"
                      }`}
                  >
                    <td className="border-2 border-blue-100 dark:border-slate-700 
                      px-4 py-3 font-semibold text-gray-800 dark:text-gray-200">
                      {row.feature || "-"}
                    </td>
                    {Object.keys(row)
                      .filter((key) => key !== "feature")
                      .map((key) => (
                        <td
                          key={key}
                          className={`border-2 border-blue-100 dark:border-slate-700 
                            px-4 py-3 text-gray-700 dark:text-gray-300
                            ${hasWinner && key === result.personalized_winner 
                              ? 'bg-yellow-100 dark:bg-yellow-900/20 font-semibold' 
                              : ''}`}
                        >
                          {row[key] || "-"}
                        </td>
                      ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="mb-10 pb-8 border-b-2 border-gray-200 dark:border-slate-700">
          <div className="flex items-center gap-2 mb-4">
            <div className="p-2 bg-sky-100 dark:bg-sky-900/30 rounded-lg">
              <Table className="w-5 h-5 text-sky-600 dark:text-sky-400" />
            </div>
            <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
              Comparison Table
            </h2>
          </div>
          <p className="text-gray-600 dark:text-gray-400">
            No valid comparison table available for the given items.
          </p>
        </div>
      )}

      {/* Pros */}
      {hasPros && (
        <div className="mb-10 pb-8 border-b-2 border-gray-200 dark:border-slate-700">
          <div className="flex items-center gap-2 mb-4">
            <div className="p-2 bg-emerald-100 dark:bg-emerald-900/30 rounded-lg">
              <ThumbsUp className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
            </div>
            <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
              Pros
            </h2>
          </div>
          <ul className="space-y-2 ml-2">
            {result.pros.map((pro, idx) => (
              <li key={idx} className="flex items-start gap-3">
                <span className="text-emerald-600 dark:text-emerald-400 text-xl mt-0.5">✓</span>
                <span className="text-gray-700 dark:text-gray-300 leading-relaxed">{pro}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Cons */}
      {hasCons && (
        <div className="mb-10 pb-8 border-b-2 border-gray-200 dark:border-slate-700">
          <div className="flex items-center gap-2 mb-4">
            <div className="p-2 bg-red-100 dark:bg-red-900/30 rounded-lg">
              <ThumbsDown className="w-5 h-5 text-red-600 dark:text-red-400" />
            </div>
            <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
              Cons
            </h2>
          </div>
          <ul className="space-y-2 ml-2">
            {result.cons.map((con, idx) => (
              <li key={idx} className="flex items-start gap-3">
                <span className="text-red-600 dark:text-red-400 text-xl mt-0.5">✗</span>
                <span className="text-gray-700 dark:text-gray-300 leading-relaxed">{con}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommendation */}
      {result.recommendation && !hasWinner && (
        <div className="mb-8 pb-8 border-b-2 border-gray-200 dark:border-slate-700">
          <div className="flex items-center gap-2 mb-4">
            <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              <Lightbulb className="w-5 h-5 text-blue-600 dark:text-sky-400" />
            </div>
            <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
              Recommendation
            </h2>
          </div>
          <p className="text-gray-800 dark:text-gray-200 leading-relaxed text-lg">
            {result.recommendation}
          </p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex flex-wrap justify-start gap-4 mb-8">
        <button
          onClick={handleShare}
          disabled={shareLoading}
          className="inline-flex items-center gap-2 
            bg-gradient-to-r from-purple-600 to-pink-600 
            hover:from-purple-700 hover:to-pink-700
            text-white px-6 py-3 rounded-full font-semibold
            shadow-lg hover:shadow-xl
            transition-all duration-300
            disabled:opacity-50 disabled:cursor-not-allowed
            transform hover:scale-105 active:scale-95"
        >
          {shareLoading ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              Generating...
            </>
          ) : (
            <>
              <Share2 className="w-4 h-4" /> Share
            </>
          )}
        </button>

        <button
          onClick={onSave}
          className="inline-flex items-center gap-2 
            bg-gradient-to-r from-cyan-600 to-sky-600 
            hover:from-cyan-700 hover:to-sky-700
            text-white px-6 py-3 rounded-full font-semibold
            shadow-lg hover:shadow-xl
            transition-all duration-300
            transform hover:scale-105 active:scale-95"
        >
          <Save className="w-4 h-4" /> Save
        </button>

        <button
          onClick={onExport}
          className="inline-flex items-center gap-2 
            bg-gradient-to-r from-green-600 to-emerald-600 
            hover:from-green-700 hover:to-emerald-700
            text-white px-6 py-3 rounded-full font-semibold
            shadow-lg hover:shadow-xl
            transition-all duration-300
            transform hover:scale-105 active:scale-95"
        >
          <FileDown className="w-4 h-4" /> Export PDF
        </button>

        <button
          onClick={onReset}
          className="inline-flex items-center gap-2 
            bg-gray-200 dark:bg-slate-700 
            text-gray-800 dark:text-gray-200 
            px-6 py-3 rounded-full font-semibold
            hover:bg-gray-300 dark:hover:bg-slate-600 
            shadow-md hover:shadow-lg
            transition-all duration-300
            transform hover:scale-105 active:scale-95"
        >
          <RefreshCcw className="w-4 h-4" /> Compare Again
        </button>
      </div>

      {/* Share URL Display */}
      {shareUrl && (
        <div className="mb-8 p-5 
          bg-gradient-to-r from-purple-50 via-pink-50 to-purple-50
          dark:from-purple-900/20 dark:via-pink-900/20 dark:to-purple-900/20 
          rounded-2xl border-2 border-purple-300 dark:border-purple-700 
          shadow-md">
          <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
            🎉 Share this comparison:
          </p>
          <div className="flex items-center gap-3">
            <input
              type="text"
              value={shareUrl}
              readOnly
              className="flex-1 p-3 bg-white dark:bg-slate-800 
                border-2 border-purple-200 dark:border-purple-700 
                rounded-xl text-sm text-gray-700 dark:text-gray-300 
                font-mono"
            />
            <button
              onClick={copyToClipboard}
              className="inline-flex items-center gap-2 px-5 py-3 
                bg-purple-600 hover:bg-purple-700 
                text-white rounded-xl font-semibold
                shadow-md hover:shadow-lg
                transition-all duration-200
                transform hover:scale-105"
            >
              {copied ? (
                <>
                  <Check className="w-4 h-4" /> Copied!
                </>
              ) : (
                <>
                  <Share2 className="w-4 h-4" /> Copy
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* AI Follow-up Questions */}
      {result.comparison_id && (
        <FollowUpChat 
          comparisonId={result.comparison_id}
          items={result.items || []}
        />
      )}
    </div>
  );

}
