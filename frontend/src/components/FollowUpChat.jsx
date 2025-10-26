import { useState } from "react";
import { MessageCircle, Send, Loader2 } from "lucide-react";

export default function FollowUpChat({ comparisonId, items }) {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!question.trim() || loading) return;

    const userQuestion = question.trim();
    setQuestion("");
    
    // Add user message immediately
    setMessages(prev => [...prev, {
      role: "user",
      content: userQuestion
    }]);

    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/ask-followup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          comparison_id: comparisonId,
          question: userQuestion
        })
      });

      const data = await response.json();

      // Add AI response
      setMessages(prev => [...prev, {
        role: "assistant",
        content: data.answer
      }]);

    } catch (error) {
      console.error("Follow-up error:", error);
      setMessages(prev => [...prev, {
        role: "assistant",
        content: "Sorry, I couldn't process that question. Please try again."
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-8 p-6 bg-gradient-to-br from-blue-50 to-indigo-50 
      dark:from-slate-800 dark:to-slate-900 rounded-2xl border-2 border-blue-200 
      dark:border-blue-800 shadow-lg">
      
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <MessageCircle className="w-6 h-6 text-blue-600 dark:text-blue-400" />
        <h3 className="text-xl font-bold text-gray-800 dark:text-gray-100">
          Ask Follow-up Questions
        </h3>
      </div>

      <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
        Have specific questions about this comparison? Ask away!
      </p>

      {/* Chat Messages */}
      <div className="space-y-3 mb-4 max-h-96 overflow-y-auto">
        {messages.length === 0 && (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            <p className="text-sm">No questions yet. Try asking:</p>
            <div className="mt-3 space-y-2 text-xs">
              <p className="italic">"Which has better camera for low light?"</p>
              <p className="italic">"What about battery life for gaming?"</p>
              <p className="italic">"Is the price difference worth it?"</p>
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] p-3 rounded-2xl ${
                msg.role === "user"
                  ? "bg-blue-600 text-white rounded-br-none"
                  : "bg-white dark:bg-slate-700 text-gray-800 dark:text-gray-100 border border-gray-200 dark:border-slate-600 rounded-bl-none"
              }`}
            >
              <p className="text-sm leading-relaxed">{msg.content}</p>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-white dark:bg-slate-700 border border-gray-200 dark:border-slate-600 
              p-3 rounded-2xl rounded-bl-none">
              <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm">Thinking...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input Form */}
      <form onSubmit={handleAsk} className="flex gap-2">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Type your question..."
          disabled={loading}
          className="flex-1 p-3 border border-gray-300 dark:border-slate-600 rounded-full 
            bg-white dark:bg-slate-800 text-gray-800 dark:text-gray-100
            focus:ring-2 focus:ring-blue-400 focus:border-blue-400 
            dark:focus:ring-blue-500 transition-all
            disabled:opacity-50 disabled:cursor-not-allowed"
        />
        <button
          type="submit"
          disabled={!question.trim() || loading}
          className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 
            text-white rounded-full font-medium shadow-md
            hover:from-blue-700 hover:to-indigo-700 
            disabled:opacity-50 disabled:cursor-not-allowed
            transition-all duration-300 flex items-center gap-2"
        >
          {loading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <>
              <Send className="w-5 h-5" />
              <span className="hidden sm:inline">Ask</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
}