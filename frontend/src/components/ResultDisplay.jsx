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
import API_BASE from "../config/api";

export default function ResultDisplay({ result, onSave, onExport, onReset }) {
  const [shareUrl, setShareUrl] = useState(null);
  const [shareLoading, setShareLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleShare = async () => {
    setShareLoading(true);
    try {
      const response = await fetch(`${API_BASE}/share-comparison`, {
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

  // ✅ FIXED: Handle short messages with centered, consistent styling
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

      {/* Pros & Cons Per Item */}
      {(hasPros || hasCons) && (
        <div className="mb-10 pb-8 border-b-2 border-gray-200 dark:border-slate-700">
          <div className="flex items-center gap-2 mb-6">
            <div className="p-2 bg-gradient-to-r from-emerald-100 to-red-100 dark:from-emerald-900/30 dark:to-red-900/30 rounded-lg">
              <ClipboardList className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            </div>
            <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
              Pros & Cons
            </h2>
          </div>
          
          {/* Group pros/cons by item */}
          {(() => {
            // Parse pros and cons to group by item name
            const itemData = {};
            
            // Get unique item names from the result
            const itemNames = result.items || [];
            itemNames.forEach(name => {
              itemData[name] = { pros: [], cons: [] };
            });
            
            // Helper function to find best matching item name
            const findMatchingItem = (proConText) => {
              // Try exact match first
              const exactMatch = itemNames.find(name => 
                name.toLowerCase() === proConText.toLowerCase()
              );
              if (exactMatch) return exactMatch;
              
              // Try partial match (item name contains text or text contains item name)
              const partialMatch = itemNames.find(name => {
                const nameLower = name.toLowerCase();
                const textLower = proConText.toLowerCase();
                return nameLower.includes(textLower) || textLower.includes(nameLower);
              });
              if (partialMatch) return partialMatch;
              
              // Try word-by-word matching (e.g., "Toyota Camry" matches "Camry")
              const words = proConText.toLowerCase().split(/\s+/);
              const wordMatch = itemNames.find(name => {
                const nameWords = name.toLowerCase().split(/\s+/);
                return words.some(word => nameWords.includes(word)) ||
                       nameWords.some(word => words.includes(word));
              });
              if (wordMatch) return wordMatch;
              
              return null;
            };
            
            // Parse pros - format: "Item Name: description"
            if (result.pros) {
              result.pros.forEach(pro => {
                const colonIndex = pro.indexOf(':');
                if (colonIndex > 0) {
                  const itemName = pro.substring(0, colonIndex).trim();
                  const description = pro.substring(colonIndex + 1).trim();
                  
                  // Skip if description is empty or indicates missing info
                  if (!description || 
                      description.toLowerCase().includes('not found') ||
                      description.toLowerCase().includes('n/a') ||
                      description.toLowerCase().includes('no pros')) {
                    return;
                  }
                  
                  // Find matching item using improved matching
                  const matchedItem = findMatchingItem(itemName);
                  if (matchedItem && itemData[matchedItem]) {
                    itemData[matchedItem].pros.push(description);
                  } else {
                    // If no match found, try to distribute evenly or add to items missing pros
                    const itemsWithoutPros = itemNames.filter(name => itemData[name].pros.length === 0);
                    if (itemsWithoutPros.length > 0) {
                      itemData[itemsWithoutPros[0]].pros.push(description);
                    } else {
                      // All items have pros, add to the one with fewest
                      const itemWithFewestPros = itemNames.reduce((min, name) => 
                        itemData[name].pros.length < itemData[min].pros.length ? name : min
                      );
                      itemData[itemWithFewestPros].pros.push(description);
                    }
                  }
                } else {
                  // No colon format - try to find item name in the text itself
                  const matchedItem = findMatchingItem(pro);
                  if (matchedItem && itemData[matchedItem]) {
                    itemData[matchedItem].pros.push(pro);
                  } else {
                    // Distribute to item missing pros
                    const itemsWithoutPros = itemNames.filter(name => itemData[name].pros.length === 0);
                    if (itemsWithoutPros.length > 0) {
                      itemData[itemsWithoutPros[0]].pros.push(pro);
                    }
                  }
                }
              });
            }
            
            // Parse cons - format: "Item Name: description"
            if (result.cons) {
              result.cons.forEach(con => {
                const colonIndex = con.indexOf(':');
                if (colonIndex > 0) {
                  const itemName = con.substring(0, colonIndex).trim();
                  const description = con.substring(colonIndex + 1).trim();
                  
                  // Skip if description is empty or indicates missing info
                  if (!description || 
                      description.toLowerCase().includes('not found') ||
                      description.toLowerCase().includes('n/a') ||
                      description.toLowerCase().includes('no cons')) {
                    return;
                  }
                  
                  // Find matching item using improved matching
                  const matchedItem = findMatchingItem(itemName);
                  if (matchedItem && itemData[matchedItem]) {
                    itemData[matchedItem].cons.push(description);
                  } else {
                    // If no match found, try to distribute evenly or add to items missing cons
                    const itemsWithoutCons = itemNames.filter(name => itemData[name].cons.length === 0);
                    if (itemsWithoutCons.length > 0) {
                      itemData[itemsWithoutCons[0]].cons.push(description);
                    } else {
                      // All items have cons, add to the one with fewest
                      const itemWithFewestCons = itemNames.reduce((min, name) => 
                        itemData[name].cons.length < itemData[min].cons.length ? name : min
                      );
                      itemData[itemWithFewestCons].cons.push(description);
                    }
                  }
                } else {
                  // No colon format - try to find item name in the text itself
                  const matchedItem = findMatchingItem(con);
                  if (matchedItem && itemData[matchedItem]) {
                    itemData[matchedItem].cons.push(con);
                  } else {
                    // Distribute to item missing cons
                    const itemsWithoutCons = itemNames.filter(name => itemData[name].cons.length === 0);
                    if (itemsWithoutCons.length > 0) {
                      itemData[itemsWithoutCons[0]].cons.push(con);
                    }
                  }
                }
              });
            }
            
            // Fallback: If any item has no pros/cons, try to extract from unparsed pros/cons
            const unparsedPros = result.pros || [];
            const unparsedCons = result.cons || [];
            
            // Check for items missing pros/cons and try to fill them
            Object.entries(itemData).forEach(([itemName, data]) => {
              if (data.pros.length === 0 && unparsedPros.length > 0) {
                // Try to find any pro that mentions this item
                const matchingPros = unparsedPros.filter(pro => {
                  const proLower = pro.toLowerCase();
                  const itemLower = itemName.toLowerCase();
                  return proLower.includes(itemLower) || itemLower.includes(proLower.split(':')[0]?.toLowerCase() || '');
                });
                if (matchingPros.length > 0) {
                  matchingPros.forEach(pro => {
                    const colonIndex = pro.indexOf(':');
                    if (colonIndex > 0) {
                      data.pros.push(pro.substring(colonIndex + 1).trim());
                    } else {
                      data.pros.push(pro);
                    }
                  });
                }
              }
              
              if (data.cons.length === 0 && unparsedCons.length > 0) {
                // Try to find any con that mentions this item
                const matchingCons = unparsedCons.filter(con => {
                  const conLower = con.toLowerCase();
                  const itemLower = itemName.toLowerCase();
                  return conLower.includes(itemLower) || itemLower.includes(conLower.split(':')[0]?.toLowerCase() || '');
                });
                if (matchingCons.length > 0) {
                  matchingCons.forEach(con => {
                    const colonIndex = con.indexOf(':');
                    if (colonIndex > 0) {
                      data.cons.push(con.substring(colonIndex + 1).trim());
                    } else {
                      data.cons.push(con);
                    }
                  });
                }
              }
            });
            
            return (
              <div className="space-y-6">
                {Object.entries(itemData).map(([itemName, data], idx) => (
                  <div 
                    key={idx} 
                    className={`rounded-2xl overflow-hidden border-2 shadow-lg
                      ${hasWinner && itemName === result.personalized_winner 
                        ? 'border-yellow-400 dark:border-yellow-500 ring-2 ring-yellow-400/30' 
                        : 'border-gray-200 dark:border-slate-600'}`}
                  >
                    {/* Item Header */}
                    <div className={`px-5 py-4 flex items-center gap-3
                      ${hasWinner && itemName === result.personalized_winner 
                        ? 'bg-gradient-to-r from-yellow-100 via-amber-50 to-yellow-100 dark:from-yellow-900/40 dark:via-amber-900/30 dark:to-yellow-900/40' 
                        : 'bg-gradient-to-r from-blue-50 via-slate-50 to-blue-50 dark:from-slate-700 dark:via-slate-750 dark:to-slate-700'}`}
                    >
                      {hasWinner && itemName === result.personalized_winner && (
                        <Trophy className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
                      )}
                      <h3 className="text-xl font-bold text-gray-800 dark:text-gray-100">
                        {itemName}
                      </h3>
                      {hasWinner && itemName === result.personalized_winner && (
                        <span className="ml-auto px-3 py-1 bg-yellow-400 dark:bg-yellow-500 text-yellow-900 text-sm font-bold rounded-full">
                          WINNER
                        </span>
                      )}
                    </div>
                    
                    {/* Pros & Cons Table */}
                    <div className="grid grid-cols-2 divide-x-2 divide-gray-200 dark:divide-slate-600">
                      {/* Pros Column */}
                      <div className="bg-emerald-50/50 dark:bg-emerald-900/10">
                        <div className="px-4 py-3 bg-emerald-100 dark:bg-emerald-900/30 border-b-2 border-emerald-200 dark:border-emerald-800/50">
                          <div className="flex items-center gap-2">
                            <ThumbsUp className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                            <span className="font-bold text-emerald-700 dark:text-emerald-300">Pros</span>
                          </div>
                        </div>
                        <ul className="p-4 space-y-3">
                          {data.pros.length > 0 ? (
                            data.pros.map((pro, proIdx) => (
                              <li key={proIdx} className="flex items-start gap-2">
                                <span className="text-emerald-500 dark:text-emerald-400 mt-0.5 flex-shrink-0">✓</span>
                                <span className="text-gray-700 dark:text-gray-300 text-sm leading-relaxed">{pro}</span>
              </li>
                            ))
                          ) : (
                            <li className="text-gray-400 dark:text-gray-500 text-sm italic">No pros listed</li>
                          )}
          </ul>
        </div>
                      
                      {/* Cons Column */}
                      <div className="bg-red-50/50 dark:bg-red-900/10">
                        <div className="px-4 py-3 bg-red-100 dark:bg-red-900/30 border-b-2 border-red-200 dark:border-red-800/50">
                          <div className="flex items-center gap-2">
              <ThumbsDown className="w-5 h-5 text-red-600 dark:text-red-400" />
                            <span className="font-bold text-red-700 dark:text-red-300">Cons</span>
            </div>
          </div>
                        <ul className="p-4 space-y-3">
                          {data.cons.length > 0 ? (
                            data.cons.map((con, conIdx) => (
                              <li key={conIdx} className="flex items-start gap-2">
                                <span className="text-red-500 dark:text-red-400 mt-0.5 flex-shrink-0">✗</span>
                                <span className="text-gray-700 dark:text-gray-300 text-sm leading-relaxed">{con}</span>
              </li>
                            ))
                          ) : (
                            <li className="text-gray-400 dark:text-gray-500 text-sm italic">No cons listed</li>
                          )}
          </ul>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            );
          })()}
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