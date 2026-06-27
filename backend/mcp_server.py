"""
MCP (Model Context Protocol) Server for COMPAIR

This server exposes COMPAIR Dashboard data as programmatic tools that Grok/ChatGPT/Claude 
can use to interpret data, identify patterns, and provide intelligent recommendations.

The tools are aligned with the Dashboard metrics so AI assistants can provide
insights based on the same data users see visually.

Usage:
    python mcp_server.py
    
Then configure Grok/ChatGPT/Claude to connect to this MCP server.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os

# Import database utilities
from database.connection import get_db_session
from database.repository import (
    get_dashboard_summary,
    get_feedback_stats,
    get_last_comparison,
    get_recent_comparisons,
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="COMPAIR MCP Server",
    description="Model Context Protocol server exposing Dashboard data as tools for AI assistants",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# MCP TOOL SCHEMAS
# ============================================================================

class ToolRequest(BaseModel):
    """Base request model for tool invocation."""
    tool_name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class ToolResponse(BaseModel):
    """Base response model for tool results."""
    tool_name: str
    success: bool
    data: Any
    error: Optional[str] = None


# ============================================================================
# MCP TOOLS - Based on Dashboard Metrics
# ============================================================================

def tool_get_dashboard_overview() -> Dict:
    """
    Get complete dashboard overview - all metrics in one call.
    
    This is the primary tool for AI assistants to understand the current state
    of COMPAIR usage and user satisfaction.
    
    Returns:
        Complete dashboard data including:
        - Total comparisons
        - Comparison quality (comprehensiveness score)
        - Decision confidence metrics
        - Preference usage breakdown
        - Category distribution
        - Recent trends
        - User feedback insights
    """
    try:
        with get_db_session() as db:
            summary = get_dashboard_summary(db)
            return {
                "overview": "Complete COMPAIR Dashboard Data",
                "data": summary,
                "generated_at": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Error in tool_get_dashboard_overview: {e}")
        raise


def tool_get_comparison_quality() -> Dict:
    """
    Get comparison quality metrics from user feedback.
    
    Analyzes the comprehensiveness ratings users give after comparisons.
    Useful for understanding if comparison results are meeting user expectations.
    
    Returns:
        - comprehensiveness_score: Average rating (1-5)
        - rating_breakdown: Count per star rating (5★, 4★, 3★, 2★, 1★)
        - total_responses: Number of feedback responses
        - quality_assessment: AI-friendly interpretation
    """
    try:
        with get_db_session() as db:
            stats = get_feedback_stats(db)
            
            score = stats.get("comprehensiveness_score", 0)
            breakdown = stats.get("rating_breakdown", {})
            total = sum(breakdown.values())
            
            # Generate quality assessment
            if score >= 4.5:
                assessment = "Excellent - Users find comparisons very comprehensive"
            elif score >= 4.0:
                assessment = "Good - Users are generally satisfied with comparison quality"
            elif score >= 3.5:
                assessment = "Average - There's room for improvement in comparison depth"
            elif score >= 3.0:
                assessment = "Below average - Users want more detailed comparisons"
            else:
                assessment = "Needs attention - Comparison quality is not meeting expectations"
            
            return {
                "comprehensiveness_score": round(score, 2),
                "rating_breakdown": breakdown,
                "total_responses": total,
                "quality_assessment": assessment,
                "percentages": {
                    f"{star}★": round((count / total * 100), 1) if total > 0 else 0
                    for star, count in breakdown.items()
                }
            }
    except Exception as e:
        logger.error(f"Error in tool_get_comparison_quality: {e}")
        raise


def tool_get_decision_confidence() -> Dict:
    """
    Get decision confidence metrics - how well comparisons help users decide.
    
    Two types of metrics:
    1. Decision Help (without preferences): Did the comparison help users decide?
    2. Winner Match (with preferences): How well did the AI-picked winner match user needs?
    
    Returns:
        - decision_helpfulness: Breakdown of yes/somewhat/no responses
        - winner_match_score: Average rating for personalized winner accuracy
        - winner_match_count: Number of responses for winner match
        - insights: AI-friendly interpretation
    """
    try:
        with get_db_session() as db:
            stats = get_feedback_stats(db)
            
            decision = stats.get("decision_helpfulness", {})
            winner_score = stats.get("winner_match_score", 0)
            winner_count = stats.get("winner_match_count", 0)
            
            # Calculate decision help percentages
            total_decisions = sum(decision.values())
            decision_percentages = {}
            if total_decisions > 0:
                decision_percentages = {
                    "yes_decided": round(decision.get("yes_decided", 0) / total_decisions * 100, 1),
                    "somewhat": round(decision.get("somewhat", 0) / total_decisions * 100, 1),
                    "still_confused": round(decision.get("still_confused", 0) / total_decisions * 100, 1)
                }
            
            # Generate insights
            insights = []
            if decision_percentages.get("yes_decided", 0) >= 70:
                insights.append("Strong: Most users can make decisions after comparisons")
            elif decision_percentages.get("still_confused", 0) >= 30:
                insights.append("Concern: Many users still confused after comparisons")
            
            if winner_score >= 4.0:
                insights.append("Personalization working well - winners match user needs")
            elif winner_score > 0 and winner_score < 3.5:
                insights.append("Personalization needs improvement - winners don't match well")
            
            return {
                "decision_helpfulness": {
                    "counts": decision,
                    "percentages": decision_percentages,
                    "total_responses": total_decisions
                },
                "winner_match": {
                    "score": round(winner_score, 2),
                    "count": winner_count,
                    "assessment": "Good match" if winner_score >= 4 else "Needs improvement" if winner_score > 0 else "No data"
                },
                "insights": insights
            }
    except Exception as e:
        logger.error(f"Error in tool_get_decision_confidence: {e}")
        raise


def tool_get_preference_usage() -> Dict:
    """
    Get preference usage breakdown - how users choose to compare.
    
    Shows the split between:
    - With Preferences: Users who specify what matters to them (personalized)
    - Without Preferences: Users who want general comparisons
    
    Returns:
        - personalized_count: Comparisons with user preferences
        - general_count: Comparisons without preferences
        - total_comparisons: Total number of comparisons
        - percentages: Percentage breakdown
        - trend_insight: AI-friendly interpretation
    """
    try:
        with get_db_session() as db:
            summary = get_dashboard_summary(db)
            
            personalized = summary.get("personalized_count", 0)
            general = summary.get("general_count", 0)
            total = summary.get("total_comparisons", 0)
            
            personalized_pct = round((personalized / total * 100), 1) if total > 0 else 0
            general_pct = round((general / total * 100), 1) if total > 0 else 0
            
            # Generate insight
            if personalized_pct >= 60:
                insight = "Users prefer personalized comparisons - they value tailored recommendations"
            elif general_pct >= 60:
                insight = "Users prefer quick general comparisons - consider prompting for preferences"
            else:
                insight = "Balanced usage - users use both personalized and general comparisons"
            
            return {
                "personalized_count": personalized,
                "general_count": general,
                "total_comparisons": total,
                "percentages": {
                    "with_preferences": personalized_pct,
                    "without_preferences": general_pct
                },
                "trend_insight": insight
            }
    except Exception as e:
        logger.error(f"Error in tool_get_preference_usage: {e}")
        raise


def tool_get_category_insights() -> Dict:
    """
    Get category distribution and insights.
    
    Shows which categories users compare most often.
    
    Returns:
        - categories: List of categories with counts
        - top_category: Most popular category
        - insights: AI-friendly interpretation
    """
    try:
        with get_db_session() as db:
            summary = get_dashboard_summary(db)
            
            categories = summary.get("category_stats", [])
            total = sum(cat.get("count", 0) for cat in categories)
            
            # Add percentages
            for cat in categories:
                cat["percentage"] = round((cat.get("count", 0) / total * 100), 1) if total > 0 else 0
            
            # Sort by count
            categories_sorted = sorted(categories, key=lambda x: x.get("count", 0), reverse=True)
            
            top_category = categories_sorted[0] if categories_sorted else None
            
            return {
                "categories": categories_sorted,
                "total_comparisons": total,
                "top_category": top_category.get("category") if top_category else None,
                "top_category_percentage": top_category.get("percentage") if top_category else 0,
                "diversity": len(categories),
                "insight": f"'{top_category.get('category')}' is the most compared category" if top_category else "No category data yet"
            }
    except Exception as e:
        logger.error(f"Error in tool_get_category_insights: {e}")
        raise


def tool_get_popular_comparisons() -> Dict:
    """
    Get most popular item comparisons.
    
    Shows which item pairs users compare most frequently.
    
    Returns:
        - comparison_pairs: List of item pairs with counts
        - insights: AI-friendly interpretation
    """
    try:
        with get_db_session() as db:
            summary = get_dashboard_summary(db)
            
            pairs = summary.get("comparison_pairs", [])
            
            return {
                "comparison_pairs": pairs[:10],  # Top 10
                "total_unique_pairs": len(pairs),
                "insight": f"Top comparison: {pairs[0].get('items', 'N/A')}" if pairs else "No comparison data yet"
            }
    except Exception as e:
        logger.error(f"Error in tool_get_popular_comparisons: {e}")
        raise


def tool_get_user_feedback_summary() -> Dict:
    """
    Get user feedback summary - what users like and want improved.
    
    Aggregates the text feedback from users:
    - What they liked about comparisons
    - What they think could be improved
    
    Returns:
        - liked_comments: Recent positive feedback
        - improvement_comments: Recent improvement suggestions
        - feedback_themes: Common themes identified
    """
    try:
        with get_db_session() as db:
            stats = get_feedback_stats(db)
            
            liked = stats.get("liked_comments", [])
            improvements = stats.get("improvement_comments", [])
            
            # Simple theme extraction (could be enhanced with NLP)
            themes = {
                "positive": [],
                "improvements": []
            }
            
            if liked:
                themes["positive"].append(f"{len(liked)} users shared what they liked")
            if improvements:
                themes["improvements"].append(f"{len(improvements)} users suggested improvements")
            
            return {
                "liked_comments": liked[:10],  # Most recent 10
                "improvement_comments": improvements[:10],
                "total_liked": len(liked),
                "total_improvements": len(improvements),
                "themes": themes,
                "insight": "Users are providing feedback" if (liked or improvements) else "No feedback yet - encourage users to share their thoughts"
            }
    except Exception as e:
        logger.error(f"Error in tool_get_user_feedback_summary: {e}")
        raise


def tool_get_activity_trends() -> Dict:
    """
    Get comparison activity trends over time.
    
    Shows how comparison usage has changed over the last 14 days.
    
    Returns:
        - daily_counts: List of daily comparison counts
        - trend_direction: Increasing, decreasing, or stable
        - insights: AI-friendly interpretation
    """
    try:
        with get_db_session() as db:
            summary = get_dashboard_summary(db)
            
            trends = summary.get("trends", [])
            
            # Analyze trend direction
            if len(trends) >= 2:
                recent = sum(t.get("count", 0) for t in trends[-7:])
                older = sum(t.get("count", 0) for t in trends[:-7]) if len(trends) > 7 else 0
                
                if recent > older * 1.2:
                    direction = "increasing"
                    insight = "Usage is growing - more comparisons in recent days"
                elif recent < older * 0.8:
                    direction = "decreasing"
                    insight = "Usage is declining - fewer comparisons recently"
                else:
                    direction = "stable"
                    insight = "Usage is stable"
            else:
                direction = "insufficient_data"
                insight = "Not enough data to determine trend"
            
            return {
                "daily_counts": trends,
                "trend_direction": direction,
                "total_period_comparisons": sum(t.get("count", 0) for t in trends),
                "insight": insight
            }
    except Exception as e:
        logger.error(f"Error in tool_get_activity_trends: {e}")
        raise


def tool_get_last_comparison() -> Dict:
    """
    Get details about the most recent comparison.
    
    Returns information about the last comparison made, including:
    - Items compared
    - Category
    - Full comparison result (introduction, table, pros, cons, recommendation, winner)
    - When it was created
    - Comparison ID
    
    This tool is useful when users ask questions like:
    - "What was the last comparison about?"
    - "Tell me about the last comparison"
    - "What items were compared last?"
    """
    try:
        with get_db_session() as db:
            last_comp = get_last_comparison(db)
            
            if not last_comp:
                return {
                    "found": False,
                    "message": "No comparisons found in the database yet."
                }
            
            # Extract comparison data
            comparison_data = last_comp.original_comparison if isinstance(last_comp.original_comparison, dict) else {}
            
            return {
                "found": True,
                "comparison_id": last_comp.comparison_id,
                "items": last_comp.items if isinstance(last_comp.items, list) else [],
                "category": last_comp.category,
                "created_at": last_comp.created_at.isoformat() if last_comp.created_at else None,
                "comparison_data": {
                    "introduction": comparison_data.get("introduction", ""),
                    "table": comparison_data.get("table", {}),
                    "pros": comparison_data.get("pros", {}),
                    "cons": comparison_data.get("cons", {}),
                    "recommendation": comparison_data.get("recommendation", ""),
                    "personalized_winner": comparison_data.get("personalized_winner", ""),
                    "winner_reason": comparison_data.get("winner_reason", "")
                },
                "summary": f"Last comparison: {', '.join(last_comp.items) if isinstance(last_comp.items, list) else 'N/A'} in category '{last_comp.category}'"
            }
    except Exception as e:
        logger.error(f"Error in tool_get_last_comparison: {e}")
        raise


def tool_get_recent_comparisons(limit: int = 5) -> Dict:
    """
    Get recent comparisons (last N comparisons).
    
    Parameters:
        - limit: Number of recent comparisons to retrieve (default: 5)
    
    Returns:
        - List of recent comparisons with basic info (items, category, created_at)
        - Useful for questions like "What are the latest comparisons?"
    """
    try:
        with get_db_session() as db:
            recent = get_recent_comparisons(db, limit=limit)
            
            if not recent:
                return {
                    "found": False,
                    "message": "No comparisons found in the database yet.",
                    "comparisons": []
                }
            
            comparisons_list = []
            for comp in recent:
                comparison_data = comp.original_comparison if isinstance(comp.original_comparison, dict) else {}
                comparisons_list.append({
                    "comparison_id": comp.comparison_id,
                    "items": comp.items if isinstance(comp.items, list) else [],
                    "category": comp.category,
                    "created_at": comp.created_at.isoformat() if comp.created_at else None,
                    "has_winner": bool(comparison_data.get("personalized_winner")),
                    "winner": comparison_data.get("personalized_winner", ""),
                    "summary": f"{', '.join(comp.items) if isinstance(comp.items, list) else 'N/A'} ({comp.category})"
                })
            
            return {
                "found": True,
                "count": len(comparisons_list),
                "comparisons": comparisons_list,
                "message": f"Found {len(comparisons_list)} recent comparison(s)"
            }
    except Exception as e:
        logger.error(f"Error in tool_get_recent_comparisons: {e}")
        raise


def tool_generate_insights_report() -> Dict:
    """
    Generate a comprehensive insights report combining all dashboard metrics.
    
    This is the most powerful tool - it analyzes all data and provides
    actionable insights and recommendations.
    
    Returns:
        - executive_summary: High-level overview
        - key_metrics: Important numbers at a glance
        - strengths: What's working well
        - improvements: Areas needing attention
        - recommendations: Actionable suggestions
    """
    try:
        with get_db_session() as db:
            summary = get_dashboard_summary(db)
            feedback = get_feedback_stats(db)
            
            # Extract key metrics
            total_comparisons = summary.get("total_comparisons", 0)
            quality_score = feedback.get("comprehensiveness_score", 0)
            personalized_count = summary.get("personalized_count", 0)
            general_count = summary.get("general_count", 0)
            winner_match = feedback.get("winner_match_score", 0)
            decision_help = feedback.get("decision_helpfulness", {})
            
            # Analyze strengths
            strengths = []
            if quality_score >= 4.0:
                strengths.append("High comparison quality - users find results comprehensive")
            if winner_match >= 4.0:
                strengths.append("Strong personalization - AI winners match user needs well")
            if decision_help.get("yes_decided", 0) > decision_help.get("still_confused", 0):
                strengths.append("Comparisons are helping users make decisions")
            
            # Identify improvements
            improvements = []
            if quality_score < 3.5 and quality_score > 0:
                improvements.append("Comparison quality could be improved")
            if winner_match < 3.5 and winner_match > 0:
                improvements.append("Personalized winners not matching user expectations")
            if decision_help.get("still_confused", 0) > decision_help.get("yes_decided", 0):
                improvements.append("Many users still confused after comparisons")
            if personalized_count < general_count:
                improvements.append("Low personalization adoption - users not specifying preferences")
            
            # Generate recommendations
            recommendations = []
            if quality_score < 4.0:
                recommendations.append("Enhance comparison detail and depth")
            if personalized_count < general_count:
                recommendations.append("Encourage users to specify their preferences for better results")
            if not strengths:
                recommendations.append("Gather more user feedback to understand needs")
            
            personalized_pct = round((personalized_count / total_comparisons * 100), 1) if total_comparisons > 0 else 0
            
            return {
                "executive_summary": f"COMPAIR has processed {total_comparisons} comparisons with an average quality score of {quality_score:.1f}/5. {personalized_pct}% of users used personalized comparisons.",
                "key_metrics": {
                    "total_comparisons": total_comparisons,
                    "quality_score": round(quality_score, 2),
                    "personalization_rate": f"{personalized_pct}%",
                    "winner_match_score": round(winner_match, 2) if winner_match > 0 else "N/A"
                },
                "strengths": strengths if strengths else ["Keep gathering data to identify strengths"],
                "improvements": improvements if improvements else ["No critical issues identified"],
                "recommendations": recommendations if recommendations else ["Continue monitoring metrics"],
                "generated_at": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Error in tool_generate_insights_report: {e}")
        raise


# ============================================================================
# TOOL REGISTRY
# ============================================================================

TOOLS = {
    "get_dashboard_overview": {
        "function": tool_get_dashboard_overview,
        "description": "Get complete dashboard overview with all metrics in one call",
        "parameters": {}
    },
    "get_comparison_quality": {
        "function": tool_get_comparison_quality,
        "description": "Get comparison quality metrics (comprehensiveness score, rating breakdown)",
        "parameters": {}
    },
    "get_decision_confidence": {
        "function": tool_get_decision_confidence,
        "description": "Get decision confidence metrics (decision helpfulness, winner match score)",
        "parameters": {}
    },
    "get_preference_usage": {
        "function": tool_get_preference_usage,
        "description": "Get preference usage breakdown (personalized vs general comparisons)",
        "parameters": {}
    },
    "get_category_insights": {
        "function": tool_get_category_insights,
        "description": "Get category distribution and insights",
        "parameters": {}
    },
    "get_popular_comparisons": {
        "function": tool_get_popular_comparisons,
        "description": "Get most popular item comparison pairs",
        "parameters": {}
    },
    "get_user_feedback_summary": {
        "function": tool_get_user_feedback_summary,
        "description": "Get user feedback summary (what users like and want improved)",
        "parameters": {}
    },
    "get_activity_trends": {
        "function": tool_get_activity_trends,
        "description": "Get comparison activity trends over time",
        "parameters": {}
    },
    "generate_insights_report": {
        "function": tool_generate_insights_report,
        "description": "Generate comprehensive insights report with recommendations",
        "parameters": {}
    },
    "get_last_comparison": {
        "function": tool_get_last_comparison,
        "description": "Get details about the most recent comparison (items, category, full comparison result, winner, etc.)",
        "parameters": {}
    },
    "get_recent_comparisons": {
        "function": tool_get_recent_comparisons,
        "description": "Get recent comparisons (last N comparisons) with basic info",
        "parameters": {
            "limit": {
                "type": "integer",
                "description": "Number of recent comparisons to retrieve",
                "default": 5
            }
        }
    }
}


# ============================================================================
# MCP API ENDPOINTS
# ============================================================================

@app.get("/")
def root():
    """Root endpoint - MCP server info."""
    return {
        "name": "COMPAIR MCP Server",
        "version": "2.0.0",
        "description": "Dashboard-aligned MCP tools for AI assistants (ChatGPT/Claude)",
        "tools_available": len(TOOLS),
        "tools": list(TOOLS.keys())
    }


@app.get("/tools")
def list_tools():
    """
    List all available MCP tools.
    
    Returns tool names, descriptions, and parameter schemas.
    This endpoint helps AI assistants discover what tools are available.
    """
    tools_info = []
    for tool_name, tool_data in TOOLS.items():
        tools_info.append({
            "name": tool_name,
            "description": tool_data["description"],
            "parameters": tool_data["parameters"]
        })
    
    return {
        "tools": tools_info,
        "count": len(tools_info)
    }


@app.post("/tools/invoke")
async def invoke_tool(request: ToolRequest):
    """
    Invoke an MCP tool.
    
    This is the main endpoint that AI assistants call to execute tools.
    
    Request Body:
        - tool_name: Name of the tool to invoke
        - parameters: Dictionary of parameters for the tool
    
    Returns:
        - ToolResponse with results or error
    """
    tool_name = request.tool_name
    
    try:
        # Check if tool exists
        if tool_name not in TOOLS:
            raise HTTPException(
                status_code=404,
                detail=f"Tool '{tool_name}' not found. Available tools: {list(TOOLS.keys())}"
            )
        
        # Get tool function
        tool_function = TOOLS[tool_name]["function"]
        
        # Invoke tool with parameters
        logger.info(f"🔧 Invoking MCP tool: {tool_name}")
        result = tool_function(**request.parameters)
        
        return ToolResponse(
            tool_name=tool_name,
            success=True,
            data=result,
            error=None
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error invoking tool {tool_name}: {str(e)}")
        return ToolResponse(
            tool_name=tool_name,
            success=False,
            data=None,
            error=str(e)
        )


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "server": "COMPAIR MCP Server v2.0",
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# SERVER STARTUP
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # MCP server runs on a different port (8001) than main backend (8000)
    MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
    MCP_PORT = int(os.getenv("MCP_PORT", "8001"))
    
    logger.info(f"🚀 Starting COMPAIR MCP Server v2.0 on {MCP_HOST}:{MCP_PORT}")
    logger.info(f"📊 Dashboard-aligned tools: {len(TOOLS)}")
    for tool_name in TOOLS.keys():
        logger.info(f"   • {tool_name}")
    
    uvicorn.run(app, host=MCP_HOST, port=MCP_PORT)




