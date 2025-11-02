from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
from datetime import datetime
import logging
import uuid

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.chat_message_histories import ChatMessageHistory

# Prompt imports
from prompt.prompt import (
    get_comparison_prompt,
    get_followup_prompt,
    get_winner_instructions_with_preferences,
    get_winner_instructions_without_preferences
)

# Constants imports
from utilities.constants import (
    OPENAI_API_KEY,
    OPENAI_MODEL_NAME,
    OPENAI_TEMPERATURE,
    APP_TITLE,
    CORS_ORIGINS,
    HISTORY_FILE,
    SHARED_FILE,
    SERVER_HOST,
    SERVER_PORT,
    SHARE_URL_BASE,
    SHARE_ID_LENGTH,
    MIN_ITEMS_TO_COMPARE,
    MIN_ITEM_LENGTH
)

# Storage imports
from utilities.storage import (
    load_history,
    save_history,
    load_shared,
    save_shared,
    increment_shared_view_count,
    conversation_memory,
    save_conversation_to_db,
    get_conversation_from_db,
    add_conversation_message,
    get_cached_comparison_result,
    save_cached_comparison,
    delete_history_item,
)

# Brave Search imports
from utilities.brave_search import (
    search_items,
    format_search_results_for_prompt
)

# Database imports
from database.connection import init_db
from database.repository import (
    get_trending_shared,
    get_most_compared_items,
    get_category_stats,
    cleanup_expired_shares,
    cleanup_expired_cache,
)

# Models imports
from models.model import (
    UserPreferences,
    CompareRequest,
    SaveComparisonRequest,
    ShareComparisonRequest,
    FollowUpRequest,
    ComparisonOutput
)

# ---------- LOGGING SETUP ---------- #
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- ENV SETUP ---------- #
logger.info(f"OpenAI key loaded successfully: {bool(OPENAI_API_KEY)}")

# ---------- DATABASE INITIALIZATION ---------- #
init_db()
logger.info("Database initialized")

# ---------- FASTAPI APP ---------- #
app = FastAPI(title=APP_TITLE)

# ---------- CORS ---------- #
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- LANGCHAIN SETUP ---------- #

# Only initialize LLM if API key is available
if OPENAI_API_KEY:
    llm = ChatOpenAI(
        model=OPENAI_MODEL_NAME,
        temperature=OPENAI_TEMPERATURE,
        api_key=OPENAI_API_KEY
    )
else:
    logger.warning("⚠️  OPENAI_API_KEY not set. LLM features will be disabled.")
    llm = None

parser = PydanticOutputParser(pydantic_object=ComparisonOutput)

# ---------- ENDPOINTS ---------- #

@app.get("/")
def root():
    return {"message": "Compair API is running! 🚀"}


@app.get("/health")
def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.get("/health/db")
def health_db():
    """Database health check endpoint."""
    try:
        from database.connection import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            
        # Get connection pool stats
        pool = engine.pool
        return {
            "status": "healthy",
            "database": "connected",
            "pool_size": pool.size(),
            "checked_in_connections": pool.checkedin(),
            "checked_out_connections": pool.checkedout(),
            "overflow": pool.overflow(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={"status": "unhealthy", "database": "disconnected", "error": str(e)}
        )

@app.post("/compare")
async def compare_items(data: CompareRequest):
    """
    ✅ Simple validation with clear rules
    """
    try:
        logger.info(f"Comparison request: {data.category}, items: {data.items}")
        
        # Basic validation
        if not data.items or len(data.items) < MIN_ITEMS_TO_COMPARE:
            return {
                "message": "Please provide at least 2 items to compare."
            }
        
        # Check for very short items (gibberish)
        if any(len(item.strip()) < MIN_ITEM_LENGTH for item in data.items):
            logger.info("Rejected: Items too short")
            return {
                "message": "Please enter clear, distinct, and comparable items."
            }
        
        # Check for identical items
        items_lower = [item.strip().lower() for item in data.items]
        if len(items_lower) != len(set(items_lower)):
            logger.info("Rejected: Identical items")
            return {
                "message": "Please enter different items to compare."
            }
        
        # Check cache first
        user_prefs_dict = data.user_preferences.dict() if data.user_preferences else None
        cached_result = get_cached_comparison_result(data.category, data.items, user_prefs_dict)
        
        if cached_result:
            logger.info("Returning cached comparison result")
            cached_result["comparison_id"] = str(uuid.uuid4())
            cached_result["items"] = data.items
            cached_result["category"] = data.category
            return cached_result
        
        # Check if user provided preferences
        has_preferences = False
        preferences_text = ""
        
        if data.user_preferences:
            prefs = []
            if data.user_preferences.priorities and len(data.user_preferences.priorities) > 0:
                prefs.append(f"Priorities: {', '.join(data.user_preferences.priorities)}")
                has_preferences = True
            if data.user_preferences.budget:
                prefs.append(f"Budget: {data.user_preferences.budget}")
                has_preferences = True
            if data.user_preferences.use_case:
                prefs.append(f"Use case: {data.user_preferences.use_case}")
                has_preferences = True
            
            if prefs:
                preferences_text = "User Preferences:\n" + "\n".join(prefs)
        
        # Dynamic winner instructions
        if has_preferences:
            winner_instructions = get_winner_instructions_with_preferences()
        else:
            winner_instructions = get_winner_instructions_without_preferences()
        
        logger.info(f"Has preferences: {has_preferences}")
        
        # Fetch real-time search results for all items using Brave Search
        logger.info("🔍 Fetching search results from Brave Search API...")
        search_results = search_items(data.items, data.category)
        
        # Format search results for prompt
        search_results_text = format_search_results_for_prompt(search_results)
        
        # Check if LLM is available
        if not llm:
            raise HTTPException(
                status_code=503,
                detail="LLM service is not available. Please set OPENAI_API_KEY environment variable."
            )
        
        # Create comparison prompt function
        create_comparison_messages = get_comparison_prompt(
            winner_instructions=winner_instructions,
            format_instructions=parser.get_format_instructions()
        )
        
        # Create messages with user inputs and search results
        messages = create_comparison_messages({
            "category": data.category,
            "items": ", ".join(data.items),
            "preferences_text": preferences_text,
            "search_results": search_results_text
        })
        
        # Log the full prompt including search results for debugging
        logger.info("=" * 80)
        logger.info("📝 PROMPT BEING SENT TO LLM:")
        logger.info("=" * 80)
        for i, msg in enumerate(messages):
            msg_type = "SYSTEM" if hasattr(msg, 'content') and i == 0 else "USER"
            logger.info(f"\n[{msg_type} MESSAGE {i+1}]:")
            logger.info("-" * 80)
            # Log full content - don't truncate to see complete search results
            logger.info(msg.content)
            logger.info(f"[Message length: {len(msg.content)} chars]")
            logger.info("-" * 80)
        logger.info("=" * 80)
        
        # Invoke LLM with messages and parse result
        llm_response = llm.invoke(messages)
        result = parser.parse(llm_response.content)
        
        # Convert to dict
        result_dict = result.dict()
        
        # If AI returned error message, pass it through
        if result_dict.get("message"):
            logger.info(f"AI returned error: {result_dict['message']}")
            return result_dict
        
        # Ensure no winner if no preferences
        if not has_preferences:
            result_dict["personalized_winner"] = None
            result_dict["winner_reason"] = None
            logger.info("No preferences - removed winner")
        
        # Generate comparison ID
        comparison_id = str(uuid.uuid4())
        
        # Cache the result
        save_cached_comparison(data.category, data.items, result_dict, user_prefs_dict)
        
        # Store in memory for follow-ups (for active sessions)
        # Note: We don't save to DB yet because there's no user_id and no saved comparison yet
        # The conversation will be saved to DB when the user saves the comparison via /save-comparison
        conversation_memory[comparison_id] = {
            "chat_history": ChatMessageHistory(),
            "original_comparison": result_dict,
            "items": data.items,
            "category": data.category
        }
        
        # Add metadata to result
        result_dict["comparison_id"] = comparison_id
        result_dict["items"] = data.items
        result_dict["category"] = data.category
        
        logger.info(f"✅ Comparison successful! ID: {comparison_id}")
        return result_dict
    
    except Exception as e:
        logger.error(f"❌ Comparison error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")

@app.post("/save-comparison")
async def save_comparison(data: SaveComparisonRequest):
    """Save comparison to user history"""
    try:
        entry = save_history(data.user_id, data.category, data.items, data.result)
        logger.info(f"Comparison saved for user: {data.user_id}")
        return {"message": "Comparison saved successfully", "entry": entry}
    
    except Exception as e:
        logger.error(f"Error saving comparison: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save comparison")

@app.post("/share-comparison")
async def share_comparison(data: ShareComparisonRequest):
    """Create shareable link for comparison"""
    try:
        share_id = str(uuid.uuid4())[:SHARE_ID_LENGTH]
        comparison_id = data.result.get("comparison_id") if isinstance(data.result, dict) else None
        
        save_shared(share_id, comparison_id, data.category, data.items, data.result, data.user_id)
        
        logger.info(f"Comparison shared - ID: {share_id}")
        
        return {
            "share_url": f"{SHARE_URL_BASE}{share_id}",
            "share_id": share_id,
            "message": "Comparison shared successfully"
        }
        
    except Exception as e:
        logger.error(f"Share error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to share comparison")

@app.get("/shared/{share_id}")
async def get_shared_comparison(share_id: str):
    """Retrieve shared comparison"""
    try:
        shared = load_shared(share_id)
        
        if not shared:
            raise HTTPException(status_code=404, detail="Shared comparison not found")
        
        # Increment view count
        increment_shared_view_count(share_id)
        shared["views"] += 1
        
        return shared
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving shared comparison: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve comparison")

@app.get("/history/{user_id}")
def get_history(user_id: str, limit: int = 100, offset: int = 0, category: str = None):
    """Retrieve user's comparison history"""
    try:
        history = load_history(user_id, limit, offset, category)
        return {"user_id": user_id, "history": history}
    
    except Exception as e:
        logger.error(f"Error retrieving history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve history")

@app.post("/ask-followup")
async def ask_followup(request: FollowUpRequest):
    """Ask follow-up questions about a comparison"""
    try:
        comparison_id = request.comparison_id
        
        # Try to get from memory first (active session)
        memory_data = conversation_memory.get(comparison_id)
        
        # If not in memory, try database
        if not memory_data:
            db_conversation = get_conversation_from_db(comparison_id)
            if db_conversation:
                memory_data = {
                    "original_comparison": db_conversation["original_comparison"],
                    "items": db_conversation["items"],
                    "category": db_conversation["category"],
                    "messages": db_conversation["messages"]
                }
        
        if not memory_data:
            raise HTTPException(
                status_code=404, 
                detail="Comparison not found. Please create a comparison first."
            )
        
        original_comparison = memory_data["original_comparison"]
        items = memory_data["items"]
        category = memory_data["category"]
        
        # Check if LLM is available
        if not llm:
            raise HTTPException(
                status_code=503,
                detail="LLM service is not available. Please set OPENAI_API_KEY environment variable."
            )
        
        followup_prompt = get_followup_prompt()
        followup_chain = followup_prompt | llm
        
        response = followup_chain.invoke({
            "items": ", ".join(items),
            "category": category,
            "comparison_result": json.dumps(original_comparison, indent=2),
            "question": request.question
        })
        
        answer = response.content
        
        # Save to database
        add_conversation_message(comparison_id, "user", request.question)
        add_conversation_message(comparison_id, "assistant", answer)
        
        # Update memory if exists
        if comparison_id in conversation_memory:
            chat_history = conversation_memory[comparison_id]["chat_history"]
            chat_history.add_user_message(request.question)
            chat_history.add_ai_message(answer)
            conversation_history_len = len(chat_history.messages)
        else:
            # Get from database
            db_conv = get_conversation_from_db(comparison_id)
            conversation_history_len = len(db_conv["messages"]) if db_conv else 0
        
        return {
            "answer": answer,
            "comparison_id": comparison_id,
            "conversation_history": conversation_history_len
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Follow-up error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process follow-up: {str(e)}")

@app.get("/followup-history/{comparison_id}")
async def get_followup_history(comparison_id: str):
    """Get conversation history for a comparison"""
    # Try memory first
    if comparison_id in conversation_memory:
        memory_data = conversation_memory[comparison_id]
        chat_history = memory_data["chat_history"]
        
        history = []
        for msg in chat_history.messages:
            history.append({
                "role": "user" if msg.type == "human" else "assistant",
                "content": msg.content
            })
        
        return {
            "comparison_id": comparison_id,
            "history": history
        }
    
    # Try database
    db_conversation = get_conversation_from_db(comparison_id)
    if db_conversation:
        return {
            "comparison_id": comparison_id,
            "history": db_conversation["messages"]
        }
    
    raise HTTPException(status_code=404, detail="Comparison not found")

@app.delete("/history/{user_id}/{comparison_id}")
def delete_history_item_endpoint(user_id: str, comparison_id: str):
    """Delete specific comparison from history"""
    try:
        deleted = delete_history_item(user_id, comparison_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Comparison not found")
        
        return {"message": "Comparison deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting comparison: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete comparison")


# ========== ANALYTICS ENDPOINTS ==========

@app.get("/analytics/trending")
async def get_trending():
    """Get trending shared comparisons"""
    try:
        from database.connection import get_db_session
        with get_db_session() as db:
            trending = get_trending_shared(db, days=7, limit=10)
            return [
                {
                    "share_id": item.share_id,
                    "category": item.category,
                    "items": item.items,
                    "views": item.views,
                    "created_at": item.created_at.isoformat()
                }
                for item in trending
            ]
    except Exception as e:
        logger.error(f"Error getting trending: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get trending")


@app.get("/analytics/popular-items")
async def get_popular_items():
    """Get most compared items"""
    try:
        from database.connection import get_db_session
        with get_db_session() as db:
            items = get_most_compared_items(db, limit=10)
            return [
                {
                    "name": item.name,
                    "category": item.category,
                    "comparison_count": item.comparison_count
                }
                for item in items
            ]
    except Exception as e:
        logger.error(f"Error getting popular items: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get popular items")


@app.get("/analytics/category-stats")
async def get_category_statistics(days: int = 30):
    """Get category statistics"""
    try:
        from database.connection import get_db_session
        with get_db_session() as db:
            stats = get_category_stats(db, days=days)
            return {"stats": stats}
    except Exception as e:
        logger.error(f"Error getting category stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get category stats")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)