import { useState, useEffect, useCallback } from "react";
import { 
  BarChart3, Target, TrendingUp,
  ThumbsUp, ThumbsDown, Clock, Activity
} from "lucide-react";
import Navbar from "../Navbar";
import Loader from "../components/Loader";
import AnalyticsChat from "../components/AnalyticsChat";
import API_BASE from "../config/api";

export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  const [timeRange, setTimeRange] = useState(30);

  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${API_BASE}/analytics/dashboard?days=${timeRange}`);
      if (!response.ok) throw new Error('Failed to fetch dashboard data');
      const data = await response.json();
      console.log('Dashboard data received:', data);
      console.log('Feedback stats:', data.feedback_stats);
      console.log('Liked comments:', data.feedback_stats?.liked_comments);
      console.log('Improvement comments:', data.feedback_stats?.improvement_comments);
      setDashboardData(data);
    } catch (err) {
      console.error('Dashboard error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [timeRange]);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
        <Navbar />
        <div className="flex items-center justify-center min-h-[80vh]">
          <Loader />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
        <Navbar />
        <div className="container mx-auto px-4 py-8">
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 text-center">
            <p className="text-red-600 dark:text-red-400">{error}</p>
            <button onClick={fetchDashboardData} className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  const {
    total_comparisons = 0,
    personalized_count = 0,
    general_count = 0,
    category_stats = [],
    comparison_pairs = [],
    feedback_stats = {},
    trends = []
  } = dashboardData || {};

  const {
    comprehensiveness_score = 0,
    rating_breakdown = {},
    decision_helpfulness = {},
    winner_match_score = 0,
    winner_match_count = 0,
    liked_comments = [],
    improvement_comments = []
  } = feedback_stats || {};
  
  // Debug logging
  console.log('Extracted liked_comments:', liked_comments);
  console.log('Extracted improvement_comments:', improvement_comments);
  console.log('liked_comments length:', liked_comments?.length);
  console.log('improvement_comments length:', improvement_comments?.length);
  console.log('First liked comment:', liked_comments?.[0]);
  console.log('First improvement comment:', improvement_comments?.[0]);
  console.log('liked_comments after filter:', liked_comments?.filter(c => c && c.text && typeof c.text === 'string' && c.text.trim().length > 0));
  console.log('improvement_comments after filter:', improvement_comments?.filter(c => c && c.text && typeof c.text === 'string' && c.text.trim().length > 0));

  // Calculate percentages
  const totalRatings = Object.values(rating_breakdown).reduce((a, b) => a + b, 0);
  const getRatingPercent = (rating) => totalRatings > 0 ? Math.round((rating_breakdown[rating] || 0) / totalRatings * 100) : 0;
  
  const totalDecisions = (decision_helpfulness.yes_decided || 0) + (decision_helpfulness.somewhat || 0) + (decision_helpfulness.still_confused || 0);
  const getDecisionPercent = (key) => totalDecisions > 0 ? Math.round((decision_helpfulness[key] || 0) / totalDecisions * 100) : 0;

  const totalPrefs = personalized_count + general_count;
  const personalizedPercent = totalPrefs > 0 ? Math.round((personalized_count / totalPrefs) * 100) : 0;

  // Get color for quality score
  const getQualityColor = (score) => {
    if (score >= 4.5) return "text-emerald-500";
    if (score >= 3.5) return "text-yellow-500";
    return "text-rose-500";
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <Navbar />
      
      <div className="container mx-auto px-4 py-6 max-w-7xl">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
              <BarChart3 className="w-7 h-7 text-indigo-600" />
              COMPAIR Analytics Dashboard
            </h1>
            <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">Performance insights and user feedback</p>
          </div>
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(Number(e.target.value))}
            className="mt-3 md:mt-0 px-3 py-1.5 text-sm bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-700 dark:text-gray-300"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
        </div>

        {/* ============ TOP SECTION: METRICS SUMMARY ============ */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
          
          {/* Card 1: Comparison Quality */}
          <div className="bg-white dark:bg-gray-900 rounded-xl p-5 border border-gray-200 dark:border-gray-800 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide">Comparison Quality</h3>
              <span className="text-xs text-gray-400">{totalRatings} responses</span>
            </div>
            
            <div className="flex items-center justify-between gap-4">
              {/* Score - Left side */}
              <div className="text-center">
                <div className="flex items-baseline gap-1">
                  <span className={`text-5xl font-bold ${getQualityColor(comprehensiveness_score)}`}>
                    {comprehensiveness_score.toFixed(1)}
                  </span>
                  <span className="text-gray-400 text-lg">/5</span>
                </div>
                <p className="text-xs text-gray-400 mt-1">avg score</p>
              </div>

              {/* Star Rating Pie Chart - Right side */}
              {totalRatings > 0 && (
                <div className="flex items-center gap-4">
                  <div className="relative w-24 h-24 flex-shrink-0">
                    <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                      {(() => {
                        const ratings = [
                          { key: "5", color: "#10B981", percent: getRatingPercent("5") },
                          { key: "4", color: "#4ADE80", percent: getRatingPercent("4") },
                          { key: "3", color: "#FACC15", percent: getRatingPercent("3") },
                          { key: "2", color: "#FB923C", percent: getRatingPercent("2") },
                          { key: "1", color: "#F43F5E", percent: getRatingPercent("1") }
                        ];
                        let offset = 0;
                        return ratings.map((r, i) => {
                          const strokeDasharray = `${r.percent * 0.88} ${88 - r.percent * 0.88}`;
                          const strokeDashoffset = -offset * 0.88;
                          offset += r.percent;
                          return r.percent > 0 ? (
                            <circle
                              key={r.key}
                              cx="18" cy="18" r="14"
                              fill="none"
                              stroke={r.color}
                              strokeWidth="5"
                              strokeDasharray={strokeDasharray}
                              strokeDashoffset={strokeDashoffset}
                            />
                          ) : null;
                        });
                      })()}
                    </svg>
                  </div>

                  {/* Legend */}
                  <div className="grid grid-cols-1 gap-1.5">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-emerald-500" />
                      <span className="text-xs text-gray-600 dark:text-gray-300 font-medium">5★</span>
                      <span className="text-xs text-gray-400">{getRatingPercent("5")}%</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-green-400" />
                      <span className="text-xs text-gray-600 dark:text-gray-300 font-medium">4★</span>
                      <span className="text-xs text-gray-400">{getRatingPercent("4")}%</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-yellow-400" />
                      <span className="text-xs text-gray-600 dark:text-gray-300 font-medium">3★</span>
                      <span className="text-xs text-gray-400">{getRatingPercent("3")}%</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-orange-400" />
                      <span className="text-xs text-gray-600 dark:text-gray-300 font-medium">2★</span>
                      <span className="text-xs text-gray-400">{getRatingPercent("2")}%</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-rose-500" />
                      <span className="text-xs text-gray-600 dark:text-gray-300 font-medium">1★</span>
                      <span className="text-xs text-gray-400">{getRatingPercent("1")}%</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Card 2: Decision Confidence Metrics */}
          <div className="bg-white dark:bg-gray-900 rounded-xl p-5 border border-gray-200 dark:border-gray-800 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide">Decision Confidence</h3>
              <Target className="w-4 h-4 text-gray-400" />
            </div>

            <div className="grid grid-cols-2 gap-3">
              {/* Non-personalized: Decision Help */}
              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs font-medium text-gray-700 dark:text-gray-300">Decision Help</span>
                    <span className="text-[10px] px-1.5 py-0.5 bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400 rounded">
                      No Prefs
                    </span>
                  </div>
                </div>
                <p className="text-[10px] text-gray-400 mb-2">{totalDecisions} responses</p>
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1">
                      <div className="w-2 h-2 rounded-full bg-emerald-500" />
                      <span className="text-xs text-gray-600 dark:text-gray-300">Yes</span>
                    </div>
                    <span className="text-xs font-semibold text-emerald-600">{getDecisionPercent("yes_decided")}%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1">
                      <div className="w-2 h-2 rounded-full bg-yellow-500" />
                      <span className="text-xs text-gray-600 dark:text-gray-300">Somewhat</span>
                    </div>
                    <span className="text-xs font-semibold text-yellow-600">{getDecisionPercent("somewhat")}%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1">
                      <div className="w-2 h-2 rounded-full bg-rose-500" />
                      <span className="text-xs text-gray-600 dark:text-gray-300">No</span>
                    </div>
                    <span className="text-xs font-semibold text-rose-600">{getDecisionPercent("still_confused")}%</span>
                  </div>
                </div>
              </div>

              {/* Personalized: Winner Match */}
              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
                <div className="flex items-center gap-1.5 mb-2">
                  <span className="text-xs font-medium text-gray-700 dark:text-gray-300">Winner Match</span>
                  <span className="text-[10px] px-1.5 py-0.5 bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 rounded">
                    With Prefs
                  </span>
                </div>
                <p className="text-[10px] text-gray-400 mb-2">{winner_match_count} responses</p>
                <div className="text-center">
                  <span className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
                    {winner_match_score > 0 ? winner_match_score.toFixed(1) : "—"}
                  </span>
                  <span className="text-gray-400 text-sm">/5</span>
                </div>
              </div>
            </div>
          </div>

          {/* Card 3: Preference Usage Breakdown (Donut) */}
          <div className="bg-white dark:bg-gray-900 rounded-xl p-5 border border-gray-200 dark:border-gray-800 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide">Preference Usage</h3>
              <span className="text-xs text-gray-400">{total_comparisons} total</span>
            </div>
            <p className="text-xs text-gray-400 mb-3">How users compare items</p>

            <div className="flex items-center gap-4">
              {/* Donut Chart */}
              <div className="relative w-20 h-20 flex-shrink-0">
                <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                  {/* Background circle (without prefs) */}
                  <circle cx="18" cy="18" r="14" fill="none" stroke="#E5E7EB" strokeWidth="4" className="dark:stroke-gray-700" />
                  {/* Foreground circle (with prefs) */}
                  <circle 
                    cx="18" cy="18" r="14" fill="none" 
                    stroke="#6366F1" strokeWidth="4"
                    strokeDasharray={`${personalizedPercent * 0.88} ${88 - personalizedPercent * 0.88}`}
                    strokeLinecap="round"
                  />
                </svg>
              </div>

              {/* Legend with counts */}
              <div className="flex-1 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-indigo-500" />
                    <span className="text-xs text-gray-700 dark:text-gray-300">With Prefs</span>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-bold text-indigo-600">{personalized_count}</span>
                    <span className="text-xs text-gray-400 ml-1">({personalizedPercent}%)</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-gray-300 dark:bg-gray-600" />
                    <span className="text-xs text-gray-700 dark:text-gray-300">Without Prefs</span>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-bold text-gray-600 dark:text-gray-400">{general_count}</span>
                    <span className="text-xs text-gray-400 ml-1">({100 - personalizedPercent}%)</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* ============ MIDDLE SECTION: USER BEHAVIOR ============ */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
          
          {/* Most Compared Categories */}
          <div className="bg-white dark:bg-gray-900 rounded-xl p-5 border border-gray-200 dark:border-gray-800 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide">Category Usage</h3>
                <p className="text-xs text-gray-400 mt-0.5">Based on {total_comparisons} total comparisons</p>
              </div>
              <BarChart3 className="w-4 h-4 text-gray-400" />
            </div>

            <div className="mt-4">
              {/* Vertical Bar Chart - Show all categories */}
              {(() => {
                // Define all available categories
                const allCategories = ["gadgets", "cars", "technologies", "destinations", "shows", "other"];
                
                // Create a map of category -> count from backend data
                const categoryMap = {};
                category_stats.forEach(cat => {
                  categoryMap[cat.category] = cat.count;
                });
                
                // Merge: all categories with their counts (0 if not in stats)
                const mergedCategories = allCategories.map(cat => ({
                  category: cat,
                  count: categoryMap[cat] || 0
                }));
                
                // Calculate max count for scaling (use 1 if all are 0)
                const maxCount = Math.max(...mergedCategories.map(c => c.count), 1);
                
                const colors = [
                  'bg-indigo-500 dark:bg-indigo-600',
                  'bg-emerald-500 dark:bg-emerald-600',
                  'bg-amber-500 dark:bg-amber-600',
                  'bg-rose-500 dark:bg-rose-600',
                  'bg-purple-500 dark:bg-purple-600',
                  'bg-cyan-500 dark:bg-cyan-600'
                ];
                
                return (
                  <div className="flex items-end justify-center gap-1.5" style={{ height: '140px', minHeight: '140px', maxHeight: '140px' }}>
                    {mergedCategories.map((cat, index) => {
                      // Calculate height: 0 count = 2% (minimal visible), others scale proportionally
                      const heightPercent = cat.count === 0 
                        ? 2  // Minimal height for 0 count
                        : Math.max((cat.count / maxCount) * 96, 2); // Scale from 2% to 96% (leave space for labels)
                      
                      const color = colors[index % colors.length];
                      
                      return (
                        <div key={cat.category} className="flex flex-col items-center group h-full flex-1 max-w-[50px]" style={{ minWidth: '35px' }}>
                          {/* Bar Container - takes full height, aligns to bottom */}
                          <div className="w-full h-full flex flex-col justify-end relative" style={{ height: '100px' }}>
                            {/* Bar - thin width */}
                            <div 
                              className={`w-full ${color} rounded-t hover:opacity-80 transition-all duration-300 cursor-pointer relative`}
                              style={{ height: `${heightPercent}%`, minHeight: cat.count === 0 ? '2px' : '4px' }}
                              title={`${cat.category}: ${cat.count} comparison${cat.count !== 1 ? 's' : ''}`}
                            >
                              {/* Count label on bar (only show if count > 0) */}
                              {cat.count > 0 && (
                                <div className="absolute -top-5 left-1/2 -translate-x-1/2 bg-gray-900 text-white text-[10px] px-1.5 py-0.5 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
                                  {cat.count}
                                </div>
                              )}
                            </div>
                          </div>
                          {/* Category label */}
                          <div className="mt-2 text-center w-full" style={{ height: '40px' }}>
                            <span className="text-[10px] font-medium text-gray-600 dark:text-gray-400 capitalize block truncate">
                              {cat.category}
                            </span>
                            <span className={`text-[9px] mt-0.5 block ${cat.count === 0 ? 'text-gray-300 dark:text-gray-600' : 'text-gray-400 dark:text-gray-500'}`}>
                              {cat.count}
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                );
              })()}
            </div>
          </div>

          {/* Most Compared Items */}
          <div className="bg-white dark:bg-gray-900 rounded-xl p-5 border border-gray-200 dark:border-gray-800 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide">Most Compared Items</h3>
              <TrendingUp className="w-4 h-4 text-gray-400" />
            </div>

            {comparison_pairs.length > 0 ? (
              <div className="space-y-2 max-h-64 overflow-y-auto pr-2">
                {comparison_pairs.map((item, index) => (
                  <div key={index} className="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-800 last:border-0">
                    <div className="flex items-center gap-2">
                      <span className="w-5 h-5 rounded-full bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 text-xs font-bold flex items-center justify-center flex-shrink-0">
                        {index + 1}
                      </span>
                      <span className="text-sm text-gray-700 dark:text-gray-300 truncate">{item.pair}</span>
                    </div>
                    <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded flex-shrink-0">
                      {item.count}x
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-400 text-sm text-center py-6">No comparison data yet</p>
            )}
          </div>
        </div>

        {/* ============ LOWER SECTION: SYSTEM & GROWTH ============ */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-6">
          
          {/* Average Response Time */}
          <div className="bg-white dark:bg-gray-900 rounded-xl p-5 border border-gray-200 dark:border-gray-800 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">Avg Response Time</h3>
              <Clock className="w-4 h-4 text-gray-400" />
            </div>
            <div className="flex items-baseline gap-1">
              <span className="text-3xl font-bold text-gray-400 dark:text-gray-500">—</span>
            </div>
            <p className="text-xs text-gray-400 mt-1">Coming soon</p>
          </div>

          {/* Comparison Activity Chart */}
          <div className="lg:col-span-3 bg-white dark:bg-gray-900 rounded-xl p-5 border border-gray-200 dark:border-gray-800 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide">Comparison Activity</h3>
                <p className="text-xs text-gray-400">Last 14 days</p>
              </div>
              <Activity className="w-4 h-4 text-gray-400" />
            </div>

            <div className="mt-2">
              {(() => {
                // Generate last 14 days
                const last14Days = [];
                const today = new Date();
                for (let i = 13; i >= 0; i--) {
                  const date = new Date(today);
                  date.setDate(date.getDate() - i);
                  const dateStr = date.toISOString().split('T')[0];
                  last14Days.push(dateStr);
                }
                
                // Create a map of date -> count from trends
                const trendsMap = {};
                trends.forEach(trend => {
                  trendsMap[trend.date] = trend.count;
                });
                
                // Merge: all 14 days with their counts (0 if no data)
                const allDays = last14Days.map(date => ({
                  date: date,
                  count: trendsMap[date] || 0
                }));
                
                // Calculate max count for scaling
                const maxCount = Math.max(...allDays.map(d => d.count), 1);
                
                return (
                  <div className="w-full">
                    {/* Chart bars */}
                    <div className="flex items-end justify-between gap-0.5" style={{ height: '120px', minHeight: '120px', maxHeight: '120px' }}>
                      {allDays.map((day, index) => {
                        // Calculate height: 0 count = 2% (minimal), others scale proportionally
                        const heightPercent = day.count === 0 
                          ? 2 
                          : Math.max((day.count / maxCount) * 96, 2); // Scale from 2% to 96% (leave space for labels)
                        
                        // Format date for display (MM/DD)
                        const dateObj = new Date(day.date);
                        const month = dateObj.getMonth() + 1;
                        const dayNum = dateObj.getDate();
                        const dateLabel = `${month}/${dayNum}`;
                        
                        return (
                          <div key={day.date} className="flex flex-col items-center group h-full flex-1" style={{ minWidth: '20px', maxWidth: '30px' }}>
                            {/* Bar Container */}
                            <div className="w-full h-full flex flex-col justify-end relative" style={{ height: '100px' }}>
                              {/* Bar */}
                              <div 
                                className={`w-full bg-indigo-400 dark:bg-indigo-500 rounded-t hover:bg-indigo-500 dark:hover:bg-indigo-400 transition-all duration-300 cursor-pointer relative`}
                                style={{ height: `${heightPercent}%`, minHeight: day.count === 0 ? '2px' : '4px' }}
                                title={`${day.date}: ${day.count} comparison${day.count !== 1 ? 's' : ''}`}
                              >
                                {/* Count label on bar (only show if count > 0) */}
                                {day.count > 0 && (
                                  <div className="absolute -top-5 left-1/2 -translate-x-1/2 bg-gray-900 text-white text-[10px] px-1.5 py-0.5 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
                                    {day.count}
                                  </div>
                                )}
                              </div>
                            </div>
                            {/* Date label */}
                            <div className="mt-1.5 text-center" style={{ height: '20px' }}>
                              <span className="text-[9px] text-gray-500 dark:text-gray-400 block truncate">
                                {dateLabel}
                              </span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              })()}
            </div>
          </div>
        </div>

        {/* ============ BOTTOM SECTION: FEEDBACK INSIGHTS ============ */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          
          {/* Positive Feedback */}
          <div className="bg-white dark:bg-gray-900 rounded-xl p-5 border border-gray-200 dark:border-gray-800 shadow-sm">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 rounded-lg bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center">
                <ThumbsUp className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">What Users Liked</h3>
                <p className="text-xs text-gray-400">Positive feedback</p>
              </div>
            </div>

            {(() => {
              // Handle both string and object formats
              const filtered = liked_comments?.filter(c => {
                if (!c) return false;
                // If it's a string, check if it has content
                if (typeof c === 'string') {
                  return c.trim().length > 0 && c.trim() !== '""' && c.trim() !== "''";
                }
                // If it's an object, check the text property
                if (typeof c === 'object' && c.text) {
                  const text = typeof c.text === 'string' ? c.text : String(c.text);
                  return text.trim().length > 0 && text.trim() !== '""' && text.trim() !== "''";
                }
                return false;
              }) || [];
              
              return filtered.length > 0 ? (
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {filtered.slice(0, 5).map((comment, index) => {
                    // Extract text from either string or object format
                    const text = typeof comment === 'string' ? comment : (comment.text || '');
                    return (
                      <div key={index} className="bg-emerald-50 dark:bg-emerald-900/10 rounded-lg p-3 border-l-2 border-emerald-500">
                        <p className="text-sm text-gray-700 dark:text-gray-300">"{text}"</p>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p className="text-gray-400 text-sm text-center py-4">No positive feedback yet</p>
              );
            })()}
          </div>

          {/* Improvement Suggestions */}
          <div className="bg-white dark:bg-gray-900 rounded-xl p-5 border border-gray-200 dark:border-gray-800 shadow-sm">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 rounded-lg bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
                <ThumbsDown className="w-4 h-4 text-amber-600 dark:text-amber-400" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">Areas to Improve</h3>
                <p className="text-xs text-gray-400">Constructive feedback</p>
              </div>
            </div>

            {(() => {
              // Handle both string and object formats
              const filtered = improvement_comments?.filter(c => {
                if (!c) return false;
                // If it's a string, check if it has content
                if (typeof c === 'string') {
                  return c.trim().length > 0 && c.trim() !== '""' && c.trim() !== "''";
                }
                // If it's an object, check the text property
                if (typeof c === 'object' && c.text) {
                  const text = typeof c.text === 'string' ? c.text : String(c.text);
                  return text.trim().length > 0 && text.trim() !== '""' && text.trim() !== "''";
                }
                return false;
              }) || [];
              
              return filtered.length > 0 ? (
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {filtered.slice(0, 5).map((comment, index) => {
                    // Extract text from either string or object format
                    const text = typeof comment === 'string' ? comment : (comment.text || '');
                    return (
                      <div key={index} className="bg-amber-50 dark:bg-amber-900/10 rounded-lg p-3 border-l-2 border-amber-500">
                        <p className="text-sm text-gray-700 dark:text-gray-300">"{text}"</p>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p className="text-gray-400 text-sm text-center py-4">No improvement suggestions yet</p>
              );
            })()}
          </div>
        </div>

        {/* Analytics Chat Assistant */}
        <AnalyticsChat />
      </div>
    </div>
  );
}
