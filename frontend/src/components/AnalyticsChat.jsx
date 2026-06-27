import { useState, useEffect, useRef } from "react";
import { BarChart3, Send, Loader2, Sparkles } from "lucide-react";
import API_BASE from "../config/api";

export default function AnalyticsChat() {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversationHistory, setConversationHistory] = useState([]);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!question.trim() || loading) return;

    const userQuestion = question.trim();
    setQuestion("");
    
    // Add user message immediately with unique ID
    const userMsg = {
      id: Date.now() + Math.random(), // Unique ID
      role: "user",
      content: userQuestion,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMsg]);

    setLoading(true);

    try {
      // Add timeout to prevent hanging
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout
      
      const response = await fetch(`${API_BASE}/analytics/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userQuestion,
          conversation_history: conversationHistory
        }),
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);

      if (!response.ok) {
        // Try to get error detail from response
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.detail || errorData.message || `HTTP ${response.status}`;
        throw new Error(errorMessage);
      }

      const data = await response.json();

      // Add AI response with unique ID
      const assistantMsg = {
        id: Date.now() + Math.random(), // Unique ID
        role: "assistant",
        content: data.answer,
        tool_used: data.tool_used,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, assistantMsg]);

      // Update conversation history
      setConversationHistory(data.conversation_history || []);

    } catch (error) {
      console.error("Analytics chat error:", error);
      
      // Handle timeout specifically
      let errorMessage = "Sorry, I couldn't process that question.";
      if (error.name === 'AbortError') {
        errorMessage = "Request timed out. The AI is taking too long to respond. Please try again with a simpler question.";
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      setMessages(prev => [...prev, {
        id: Date.now() + Math.random(), // Unique ID
        role: "assistant",
        content: errorMessage + "\n\n💡 Common fixes:\n1. Set GROQ_API_KEY: $env:GROQ_API_KEY = 'your-key'\n2. Restart backend after setting key\n3. Make sure MCP server is running (port 8001)\n4. Check backend logs for detailed error messages",
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-8 p-6 bg-gradient-to-br from-purple-50 to-indigo-50 
      dark:from-slate-800 dark:to-slate-900 rounded-2xl border-2 border-purple-200 
      dark:border-purple-800 shadow-lg">
      
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
          <BarChart3 className="w-6 h-6 text-purple-600 dark:text-purple-400" />
        </div>
        <div>
          <h3 className="text-xl font-bold text-gray-800 dark:text-gray-100">
            Analytics Assistant
          </h3>
          <p className="text-xs text-gray-600 dark:text-gray-400">
            Ask questions about COMPAIR analytics and metrics
          </p>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="space-y-3 mb-4 max-h-96 overflow-y-auto">
        {messages.length === 0 && (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            <Sparkles className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p className="text-sm font-medium mb-2">Ask me about dashboard analytics!</p>
            <div className="mt-3 space-y-2 text-xs">
              <p className="italic">"What's the comparison quality score?"</p>
              <p className="italic">"Generate an insights report"</p>
              <p className="italic">"How are users using preferences?"</p>
              <p className="italic">"Show me activity trends"</p>
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] p-3 rounded-2xl ${
                msg.role === "user"
                  ? "bg-purple-600 text-white rounded-br-none"
                  : "bg-white dark:bg-slate-700 text-gray-800 dark:text-gray-100 border border-gray-200 dark:border-slate-600 rounded-bl-none"
              }`}
            >
              <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
              {msg.tool_used && (
                <p className="text-xs mt-2 opacity-70 italic">
                  🔧 Used tool: {msg.tool_used}
                </p>
              )}
            </div>
          </div>
        ))}

        {/* Scroll anchor */}
        <div ref={messagesEndRef} />

        {loading && (
          <div className="flex justify-start">
            <div className="bg-white dark:bg-slate-700 border border-gray-200 dark:border-slate-600 
              p-3 rounded-2xl rounded-bl-none">
              <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm">Analyzing dashboard data...</span>
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
          placeholder="Ask about dashboard analytics..."
          disabled={loading}
          className="flex-1 p-3 border border-gray-300 dark:border-slate-600 rounded-full 
            bg-white dark:bg-slate-800 text-gray-800 dark:text-gray-100
            focus:ring-2 focus:ring-purple-400 focus:border-purple-400 
            dark:focus:ring-purple-500 transition-all
            disabled:opacity-50 disabled:cursor-not-allowed"
        />
        <button
          type="submit"
          disabled={!question.trim() || loading}
          className="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 
            text-white rounded-full font-medium shadow-md
            hover:from-purple-700 hover:to-indigo-700 
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

