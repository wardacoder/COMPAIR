# ============================================================================
# COMPAIR - AI-Powered Comparison Application Backend
# ============================================================================
# This is the main FastAPI backend server that handles all API requests
# from the frontend and orchestrates AI-powered comparisons using OpenAI GPT
# ============================================================================

# --------------------------------------------------------------------------
# STANDARD LIBRARY IMPORTS
# --------------------------------------------------------------------------
from fastapi import FastAPI, HTTPException  # Web framework for building REST APIs
from fastapi.middleware.cors import CORSMiddleware  # Allow frontend to call backend (cross-origin)
import json  # JSON manipulation for data serialization
from datetime import datetime  # Timestamps for logging and analytics
import logging  # Application logging for debugging and monitoring
import uuid  # Generate unique IDs for comparisons and shares

# --------------------------------------------------------------------------
# LANGCHAIN IMPORTS - AI/LLM Integration
# --------------------------------------------------------------------------
from langchain_openai import ChatOpenAI  # OpenAI GPT integration
from langchain_core.prompts import ChatPromptTemplate  # Structured prompt templates
from langchain_core.output_parsers import PydanticOutputParser  # Parse AI responses into structured objects
from langchain_core.output_parsers import JsonOutputParser  # Parse JSON responses
from langchain_community.chat_message_histories import ChatMessageHistory  # Store conversation history

# --------------------------------------------------------------------------
# CUSTOM MODULE IMPORTS - Prompt Engineering
# --------------------------------------------------------------------------
from prompt.prompt import (
    get_comparison_prompt,  # Main comparison prompt creator
    get_followup_prompt,  # Follow-up question prompt
    get_winner_instructions_with_preferences,  # Tell AI to pick a winner
    get_winner_instructions_without_preferences  # Tell AI NOT to pick a winner
)

# --------------------------------------------------------------------------
# CUSTOM MODULE IMPORTS - Configuration Constants
# --------------------------------------------------------------------------
from utilities.constants import (
    OPENAI_API_KEY,  # OpenAI API key from environment
    OPENAI_MODEL_NAME,  # GPT model to use (e.g., gpt-4)
    OPENAI_TEMPERATURE,  # AI creativity level (0=deterministic, 1=creative)
    APP_TITLE,  # Application title
    CORS_ORIGINS,  # Allowed frontend origins
    HISTORY_FILE,  # File path for history storage
    SHARED_FILE,  # File path for shared comparisons
    SERVER_HOST,  # Server host (e.g., 0.0.0.0)
    SERVER_PORT,  # Server port (e.g., 8000)
    SHARE_URL_BASE,  # Base URL for shareable links
    SHARE_ID_LENGTH,  # Length of share IDs
    MIN_ITEMS_TO_COMPARE,  # Minimum items required (2)
    MIN_ITEM_LENGTH  # Minimum item name length (to reject gibberish)
)

# --------------------------------------------------------------------------
# CUSTOM MODULE IMPORTS - Data Storage & Caching
# --------------------------------------------------------------------------
from utilities.storage import (
    load_shared,  # Load a shared comparison
    save_shared,  # Save a shareable comparison
    increment_shared_view_count,  # Track view counts for analytics
    conversation_memory,  # In-memory storage for active comparison sessions
    save_comparison_to_db,  # Persist comparison to database
    get_comparison_from_db,  # Retrieve comparison from database
    add_comparison_message,  # Add message to comparison's follow-up conversation
    get_cached_comparison_result,  # Check if comparison is cached
    save_cached_comparison,  # Cache comparison result
)

# --------------------------------------------------------------------------
# CUSTOM MODULE IMPORTS - External API Integration
# --------------------------------------------------------------------------
from utilities.brave_search import (
    search_items,  # Search for items using Brave Search API
    format_search_results_for_prompt,  # Format search results for AI prompt
    check_for_missing_info,  # Check result for missing information
    fetch_missing_information  # Fetch additional search results for missing info
)

# --------------------------------------------------------------------------
# CUSTOM MODULE IMPORTS - Database Operations
# --------------------------------------------------------------------------
from database.connection import init_db, get_db_session  # Initialize database tables
from database.repository import (
    get_trending_shared,  # Get most viewed shared comparisons
    get_most_compared_items,  # Get most popular items
    get_category_stats,  # Get category usage statistics
    cleanup_expired_shares,  # Remove expired shared links
    cleanup_expired_cache,  # Remove expired cache entries
    create_feedback,  # Create user feedback
    get_feedback_by_comparison,  # Get feedback for comparison
    get_feedback_stats,  # Get feedback statistics
    get_winner_distribution,  # Get winner statistics
    get_dashboard_summary,  # Get comprehensive dashboard data
    get_comparison_count_by_date,  # Get trends over time
    create_comparison,  # Create comparison entry
)

# --------------------------------------------------------------------------
# CUSTOM MODULE IMPORTS - Pydantic Data Models
# --------------------------------------------------------------------------
from models.model import (
    UserPreferences,  # User preferences model (budget, priorities, use_case)
    CompareRequest,  # Request model for /compare endpoint
    ShareComparisonRequest,  # Request model for /share-comparison endpoint
    FollowUpRequest,  # Request model for /ask-followup endpoint
    ComparisonOutput,  # Response model for comparison results
    FeedbackRequest  # Request model for /feedback endpoint
)

# ============================================================================
# APPLICATION INITIALIZATION
# ============================================================================

# --------------------------------------------------------------------------
# LOGGING CONFIGURATION
# --------------------------------------------------------------------------
# Set up application-wide logging for debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Verify OpenAI API key is loaded from environment variables
logger.info(f"OpenAI key loaded successfully: {bool(OPENAI_API_KEY)}")

# --------------------------------------------------------------------------
# DATABASE INITIALIZATION
# --------------------------------------------------------------------------
# Initialize PostgreSQL database and create tables if they don't exist
# This runs once when the server starts
init_db()
logger.info("Database initialized")

# --------------------------------------------------------------------------
# FASTAPI APPLICATION SETUP
# --------------------------------------------------------------------------
# Create the FastAPI application instance
app = FastAPI(title=APP_TITLE)

# --------------------------------------------------------------------------
# CORS MIDDLEWARE CONFIGURATION
# --------------------------------------------------------------------------
# CORS (Cross-Origin Resource Sharing) allows the frontend (React on port 3000)
# to make requests to the backend (FastAPI on port 8000)
# Without CORS, browsers block requests between different origins for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=False,  # Must be False when using allow_origins=["*"]
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# --------------------------------------------------------------------------
# AI/LLM SETUP - OpenAI GPT Integration
# --------------------------------------------------------------------------
# Initialize connection to OpenAI's GPT model (ChatGPT)
# This is used for generating comparisons and answering follow-up questions
if OPENAI_API_KEY:
    llm = ChatOpenAI(
        model=OPENAI_MODEL_NAME,  # e.g., "gpt-4" or "gpt-3.5-turbo"
        temperature=OPENAI_TEMPERATURE,  # 0=deterministic, 1=creative
        api_key=OPENAI_API_KEY
    )
else:
    logger.warning("⚠️  OPENAI_API_KEY not set. LLM features will be disabled.")
    llm = None

# Create parser to convert AI's text responses into structured ComparisonOutput objects
# This ensures the AI returns data in the format we expect
parser = PydanticOutputParser(pydantic_object=ComparisonOutput)

# ============================================================================
# API ENDPOINTS
# ============================================================================

# --------------------------------------------------------------------------
# ROOT ENDPOINT - Basic API Health Check
# --------------------------------------------------------------------------
@app.get("/")
def root():
    """
    Simple endpoint to verify the API is running.
    URL: GET /
    Returns: Welcome message
    """
    return {"message": "Compair API is running! 🚀"}


# --------------------------------------------------------------------------
# HEALTH CHECK ENDPOINT - Server Status
# --------------------------------------------------------------------------
@app.get("/health")
def health_check():
    """
    Check if the server is healthy and running.
    URL: GET /health
    Returns: Server status, timestamp, and version
    Use: Monitoring tools, load balancers
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


# --------------------------------------------------------------------------
# DATABASE HEALTH CHECK ENDPOINT - Database Connection Status
# --------------------------------------------------------------------------
@app.get("/health/db")
def health_db():
    """
    Check if database connection is working and get connection pool stats.
    URL: GET /health/db
    Returns: Database status and connection pool statistics
    Use: Verify PostgreSQL is connected and check performance metrics
    """
    try:
        from database.connection import engine
        from sqlalchemy import text
        
        # Test database connection with simple query
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            
        # Get connection pool statistics for monitoring
        pool = engine.pool
        return {
            "status": "healthy",
            "database": "connected",
            "pool_size": pool.size(),  # Total connections in pool
            "checked_in_connections": pool.checkedin(),  # Available connections
            "checked_out_connections": pool.checkedout(),  # Active connections
            "overflow": pool.overflow(),  # Extra connections beyond pool size
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(
            status_code=503,  # Service Unavailable
            detail={"status": "unhealthy", "database": "disconnected", "error": str(e)}
        )

# ============================================================================
# MAIN COMPARISON ENDPOINT - The Heart of the Application
# ============================================================================
@app.post("/compare")
async def compare_items(data: CompareRequest):
    """
    🌟 PRIMARY ENDPOINT - Compare items using AI and return structured comparison.
    
    URL: POST /compare
    
    Request Body (CompareRequest):
        - category: str (e.g., "gadgets", "cars", "technologies")
        - items: List[str] (e.g., ["iPhone 15", "Samsung S24"])
        - user_preferences: Optional[UserPreferences] (budget, priorities, use_case)
    
    Returns (ComparisonOutput):
        - introduction: Overview of comparison
        - table: Feature-by-feature comparison
        - pros: Advantages for each item
        - cons: Disadvantages for each item
        - recommendation: Balanced recommendation
        - personalized_winner: Winner if preferences provided
        - winner_reason: Explanation of why item won
        - comparison_id: Unique ID for follow-up questions
    
    Process Flow:
        1. Validate input (at least 2 items, no duplicates, no gibberish)
        2. Check cache (return cached result if available)
        3. Process user preferences
        4. Fetch real-time data from Brave Search API
        5. Create AI prompt with instructions and search results
        6. Call OpenAI GPT to generate comparison
        7. Parse and validate AI response
        8. Cache result for future requests
        9. Store in memory for follow-up questions
        10. Return structured comparison to frontend
    """
    try:
        logger.info(f"📥 Comparison request: {data.category}, items: {data.items}")
        
        # ---------------------------------------------------------------
        # STEP 1: INPUT VALIDATION
        # ---------------------------------------------------------------
        # Ensure at least 2 items provided
        if not data.items or len(data.items) < MIN_ITEMS_TO_COMPARE:
            return {
                "message": "Please provide at least 2 items to compare."
            }
        
        # Reject very short items (likely gibberish like "f" vs "d")
        if any(len(item.strip()) < MIN_ITEM_LENGTH for item in data.items):
            logger.info("❌ Rejected: Items too short")
            return {
                "message": "Please enter clear, distinct, and comparable items."
            }
        
        # Reject duplicate items (case-insensitive check)
        items_lower = [item.strip().lower() for item in data.items]
        if len(items_lower) != len(set(items_lower)):
            logger.info("❌ Rejected: Identical items")
            return {
                "message": "Please enter different items to compare."
            }
        
        # ---------------------------------------------------------------
        # STEP 2: CHECK CACHE
        # ---------------------------------------------------------------
        # If this exact comparison was done before, return cached result
        # This saves API costs and provides instant responses
        user_prefs_dict = data.user_preferences.dict() if data.user_preferences else None
        cached_result = get_cached_comparison_result(data.category, data.items, user_prefs_dict)
        
        # Generate comparison_id early (needed for both cached and new comparisons)
        comparison_id = str(uuid.uuid4())
        
        if cached_result:
            logger.info("⚡ Returning cached comparison result (fast path)")
            cached_result["comparison_id"] = comparison_id
            cached_result["items"] = data.items
            cached_result["category"] = data.category
            
            # IMPORTANT: Still save to database for analytics, even if using cache
            # This ensures all comparisons are tracked for dashboard metrics
            logger.info(f"🔄 Attempting to save cached comparison to database...")
            logger.info(f"   Comparison ID: {comparison_id}")
            logger.info(f"   Items: {data.items}")
            logger.info(f"   Category: {data.category}")
            logger.info(f"   Cached result keys: {list(cached_result.keys()) if isinstance(cached_result, dict) else 'Not a dict'}")
            
            try:
                with get_db_session() as db:
                    logger.info(f"   Database session created")
                    comp = create_comparison(
                        db, 
                        comparison_id=comparison_id,
                        user_id=None,
                        original_comparison=cached_result,
                        items=data.items,
                        category=data.category
                    )
                    logger.info(f"   Comparison object created: {comp.comparison_id[:8]}...")
                    # Context manager will commit automatically
                logger.info(f"✅ SUCCESSFULLY saved cached comparison to database!")
                logger.info(f"   Comparison ID: {comparison_id}")
                logger.info(f"   Items: {data.items}, Category: {data.category}")
            except Exception as e:
                logger.error(f"❌❌❌ FAILED to save cached comparison to database ❌❌❌")
                logger.error(f"❌ Error: {e}")
                logger.error(f"❌ Error type: {type(e).__name__}")
                import traceback
                logger.error(f"❌ Full traceback:\n{traceback.format_exc()}")
                # Don't fail the request, but log the error clearly
            
            return cached_result
        
        # ---------------------------------------------------------------
        # STEP 3: PROCESS USER PREFERENCES
        # ---------------------------------------------------------------
        # Check if user provided preferences (budget, priorities, use_case)
        # This determines whether AI should pick a winner or give balanced recommendation
        has_preferences = False
        preferences_text = ""
        
        if data.user_preferences:
            prefs = []
            # Collect all provided preferences
            if data.user_preferences.priorities and len(data.user_preferences.priorities) > 0:
                prefs.append(f"Priorities: {', '.join(data.user_preferences.priorities)}")
                has_preferences = True
            if data.user_preferences.budget:
                prefs.append(f"Budget: {data.user_preferences.budget}")
                has_preferences = True
            if data.user_preferences.use_case:
                prefs.append(f"Use case: {data.user_preferences.use_case}")
                has_preferences = True
            
            # Format preferences for AI prompt
            if prefs:
                preferences_text = "User Preferences:\n" + "\n".join(prefs)
        
        # Choose appropriate winner instructions based on preferences
        # WITH preferences: AI picks a winner based on user needs
        # WITHOUT preferences: AI gives balanced recommendation without picking winner
        if has_preferences:
            winner_instructions = get_winner_instructions_with_preferences()
        else:
            winner_instructions = get_winner_instructions_without_preferences()
        
        logger.info(f"🎯 Has preferences: {has_preferences}")
        
        # ---------------------------------------------------------------
        # STEP 4: FETCH REAL-TIME DATA FROM BRAVE SEARCH
        # ---------------------------------------------------------------
        # Search for up-to-date information about the items
        # This prevents AI hallucinations and ensures accurate data
        logger.info("🔍 Fetching search results from Brave Search API...")
        search_results = search_items(data.items, data.category)
        
        # Format search results into text that AI can understand
        search_results_text = format_search_results_for_prompt(search_results)
        
        # ---------------------------------------------------------------
        # STEP 5: VERIFY LLM AVAILABILITY
        # ---------------------------------------------------------------
        if not llm:
            raise HTTPException(
                status_code=503,  # Service Unavailable
                detail="LLM service is not available. Please set OPENAI_API_KEY environment variable."
            )
        
        # ---------------------------------------------------------------
        # STEP 6: CREATE AI PROMPT
        # ---------------------------------------------------------------
        # Get the prompt creation function with winner instructions baked in
        # This uses the closure pattern from prompt.py
        create_comparison_messages = get_comparison_prompt(
            winner_instructions=winner_instructions,  # Tell AI whether to pick winner
            format_instructions=parser.get_format_instructions()  # JSON schema for response
        )
        
        # Call the inner function with actual user data
        # Returns [SystemMessage, HumanMessage] for AI
        messages = create_comparison_messages({
            "category": data.category,
            "items": ", ".join(data.items),  # Convert list to comma-separated string
            "preferences_text": preferences_text,  # User preferences (if any)
            "search_results": search_results_text  # Real-time search data
        })
        
        # ---------------------------------------------------------------
        # STEP 7: LOG PROMPT FOR DEBUGGING (Optional - helpful during development)
        # ---------------------------------------------------------------
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
        
        # ---------------------------------------------------------------
        # STEP 8: CALL AI (OpenAI GPT) AND PARSE RESPONSE
        # ---------------------------------------------------------------
        # Send messages to OpenAI and get response
        llm_response = llm.invoke(messages)
        
        # Log raw LLM response for debugging
        logger.info(f"📝 Raw LLM response length: {len(llm_response.content)} chars")
        logger.info(f"📝 Raw LLM response preview: {llm_response.content[:500]}...")
        
        # Parse AI's text response into structured ComparisonOutput object
        # This validates the response matches our expected schema
        try:
            result = parser.parse(llm_response.content)
        except Exception as parse_error:
            logger.error(f"❌ Failed to parse LLM response: {parse_error}")
            logger.error(f"❌ LLM response content: {llm_response.content}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse AI response. Please try again."
            )
        
        # Convert Pydantic model to dictionary for JSON serialization
        result_dict = result.dict()
        result_dict["items"] = data.items  # Add items for missing info check
        
        # Validate that table exists and is not empty
        table = result_dict.get("table")
        if not table or not isinstance(table, list) or len(table) == 0:
            logger.error(f"❌ Invalid table in response: {table}")
            logger.error(f"❌ Full result_dict keys: {result_dict.keys()}")
            logger.error(f"❌ Full result_dict: {result_dict}")
            raise HTTPException(
                status_code=500,
                detail="AI response did not include a valid comparison table. Please try again."
            )
        
        logger.info(f"✅ Parsed response successfully. Table has {len(table)} rows")
        
        # ---------------------------------------------------------------
        # STEP 8.5: RETRY MECHANISM FOR MISSING INFORMATION
        # ---------------------------------------------------------------
        # Check if result has "Information not found" and retry with targeted searches
        # Increased retries to ensure all pros/cons are generated
        MAX_RETRIES = 3
        for retry in range(MAX_RETRIES):
            # Check for missing information in the result
            missing = check_for_missing_info(result_dict)
            
            has_missing = (
                len(missing["table_features"]) > 0 or
                len(missing["pros_items"]) > 0 or
                len(missing["cons_items"]) > 0
            )
            
            if not has_missing:
                logger.info(f"✅ No missing information detected (retry {retry})")
                break
            
            logger.info(f"🔄 Retry {retry + 1}/{MAX_RETRIES}: Found missing info - "
                       f"Table: {len(missing['table_features'])}, "
                       f"Pros: {len(missing['pros_items'])}, "
                       f"Cons: {len(missing['cons_items'])}")
            
            # Fetch additional search results for missing information
            additional_search_text = fetch_missing_information(missing)
            
            if not additional_search_text:
                logger.info("No additional search results found, stopping retries")
                break
            
            # Create new prompt with additional search results
            enhanced_search_text = search_results_text + "\n" + additional_search_text
            
            retry_messages = create_comparison_messages({
                "category": data.category,
                "items": ", ".join(data.items),
                "preferences_text": preferences_text,
                "search_results": enhanced_search_text
            })
            
            # Add instruction to fix missing info
            retry_instruction = f"""

⚠️ IMPORTANT: Your previous response had missing information. 
Please use the ADDITIONAL SEARCH RESULTS provided above to fill in:
- Missing table values for: {[f"{item}-{feat}" for item, feat in missing['table_features']]}
- Missing pros for: {missing['pros_items']}
- Missing cons for: {missing['cons_items']}

CRITICAL REQUIREMENTS:
1. You MUST provide pros and cons for ALL items: {data.items}
2. Format each pro/con as "[Exact Item Name]: [description]"
3. Use the EXACT item names as provided: {data.items}
4. DO NOT write "Information not found", "N/A", or "No pros/cons" - always provide actual pros and cons
5. If search results don't have specific info, use your knowledge to provide reasonable pros/cons
6. Every item must have at least 2-3 pros and 2-3 cons"""

            # Append retry instruction to user message
            retry_messages[1].content += retry_instruction
            
            logger.info(f"🔄 Sending retry request to LLM...")
            retry_response = llm.invoke(retry_messages)
            
            try:
                retry_result = parser.parse(retry_response.content)
                retry_result_dict = retry_result.dict()
                retry_result_dict["items"] = data.items
                
                # Validate retry result has a valid table
                retry_table = retry_result_dict.get("table")
                if retry_table and isinstance(retry_table, list) and len(retry_table) > 0:
                    result_dict = retry_result_dict
                    logger.info(f"✅ Retry {retry + 1} completed successfully with {len(retry_table)} table rows")
                else:
                    logger.warning(f"⚠️ Retry {retry + 1} returned invalid table, keeping previous result")
            except Exception as parse_error:
                logger.warning(f"⚠️ Failed to parse retry response: {parse_error}")
                break
        
        # ---------------------------------------------------------------
        # STEP 9: VALIDATE FINAL RESULT BEFORE RETURNING
        # ---------------------------------------------------------------
        # Ensure table is still valid after retries
        table = result_dict.get("table")
        if not table or not isinstance(table, list) or len(table) == 0:
            logger.error(f"❌ Final validation failed: table is invalid after retries")
            logger.error(f"❌ Table value: {table}")
            raise HTTPException(
                status_code=500,
                detail="Comparison failed: Unable to generate a valid comparison table. Please try again."
            )
        
        logger.info(f"✅ Final validation passed: table has {len(table)} rows")
        
        # ---------------------------------------------------------------
        # STEP 10: HANDLE AI VALIDATION ERRORS
        # ---------------------------------------------------------------
        # If AI detected invalid input (e.g., "car" in "gadgets" category)
        # it returns an error message instead of comparison
        if result_dict.get("message"):
            logger.info(f"🚫 AI returned error: {result_dict['message']}")
            return result_dict
        
        # ---------------------------------------------------------------
        # STEP 11: ENFORCE WINNER LOGIC
        # ---------------------------------------------------------------
        # Ensure no winner is returned if user didn't provide preferences
        # (AI might still return a winner, so we override it)
        if not has_preferences:
            result_dict["personalized_winner"] = None
            result_dict["winner_reason"] = None
            logger.info("No preferences - removed winner")
        
        # ---------------------------------------------------------------
        # STEP 12: GENERATE UNIQUE COMPARISON ID (if not already generated)
        # ---------------------------------------------------------------
        # This ID is used for follow-up questions and conversation tracking
        # comparison_id was already generated at the top if cache was hit
        # Only generate if we didn't hit cache (new comparison path)
        if cached_result is None:  # Only generate if we're doing a new comparison
            comparison_id = str(uuid.uuid4())
        
        # ---------------------------------------------------------------
        # STEP 13: CACHE THE RESULT
        # ---------------------------------------------------------------
        # Save to cache so identical future requests are instant
        # Cache key = (category + items + preferences)
        save_cached_comparison(data.category, data.items, result_dict, user_prefs_dict)
        
        # ---------------------------------------------------------------
        # STEP 14: CREATE COMPARISON ENTRY FOR FOLLOW-UPS AND ANALYTICS
        # ---------------------------------------------------------------
        # Create comparison entry immediately (needed for follow-ups and dashboard analytics)
        # Comparisons store the comparison data and serve as the source of truth
        try:
            with get_db_session() as db:
                comparison_entry = create_comparison(
                    db, 
                    comparison_id=comparison_id,
                    user_id=None,  # No user tracking
                    original_comparison=result_dict,
                    items=data.items,
                    category=data.category
                )
                # Explicitly flush to ensure data is written
                db.flush()
            logger.info(f"💾 Created comparison entry for analytics and follow-ups: {comparison_id}")
        except Exception as e:
            logger.error(f"❌ Failed to create comparison entry: {e}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            # Don't fail the request if save fails, but log the error clearly
        
        # ---------------------------------------------------------------
        # STEP 15: STORE IN MEMORY FOR FOLLOW-UP QUESTIONS
        # ---------------------------------------------------------------
        # Keep in-memory for active session so users can ask follow-up questions
        conversation_memory[comparison_id] = {
            "chat_history": ChatMessageHistory(),  # Empty chat history (no messages yet)
            "original_comparison": result_dict,  # The comparison result
            "items": data.items,  # Items that were compared
            "category": data.category  # Category of comparison
        }
        
        # ---------------------------------------------------------------
        # STEP 16: ADD METADATA AND RETURN
        # ---------------------------------------------------------------
        # Add additional metadata to response
        result_dict["comparison_id"] = comparison_id
        result_dict["items"] = data.items
        result_dict["category"] = data.category
        
        # Final validation before returning
        if not result_dict.get("table") or len(result_dict.get("table", [])) == 0:
            logger.error(f"❌ CRITICAL: Table is empty before returning response!")
            raise HTTPException(
                status_code=500,
                detail="Comparison failed: Unable to generate comparison table. Please try again."
            )
        
        logger.info(f"✅ Comparison successful! ID: {comparison_id}, Table rows: {len(result_dict.get('table', []))}")
        return result_dict
    
    except Exception as e:
        # Catch any unexpected errors and return 500 Internal Server Error
        logger.error(f"❌ Comparison error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# SHARE COMPARISON ENDPOINT - Create Shareable Link
# --------------------------------------------------------------------------
@app.post("/share-comparison")
async def share_comparison(data: ShareComparisonRequest):
    """
    Create a shareable public link for a comparison.
    
    URL: POST /share-comparison
    
    Request Body:
        - category: Comparison category
        - items: List of compared items
        - result: Complete comparison result
        - user_id: Optional user identifier
    
    Returns:
        - share_url: Full URL to shared comparison
        - share_id: Unique share identifier
        - message: Success message
    
    Example Response:
        {
            "share_url": "http://localhost:3000/shared/abc123",
            "share_id": "abc123"
        }
    
    Use: When user clicks "Share" button to create public link
    """
    try:
        # Generate short unique ID for the share link
        share_id = str(uuid.uuid4())[:SHARE_ID_LENGTH]
        comparison_id = data.result.get("comparison_id") if isinstance(data.result, dict) else None
        
        # Save to database with share_id
        save_shared(share_id, comparison_id, data.category, data.items, data.result)
        
        logger.info(f"🔗 Comparison shared - ID: {share_id}")
        
        return {
            "share_url": f"{SHARE_URL_BASE}{share_id}",
            "share_id": share_id,
            "message": "Comparison shared successfully"
        }
        
    except Exception as e:
        logger.error(f"Share error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to share comparison")


# --------------------------------------------------------------------------
# GET SHARED COMPARISON ENDPOINT - Retrieve Shared Link
# --------------------------------------------------------------------------
@app.get("/shared/{share_id}")
async def get_shared_comparison(share_id: str):
    """
    Retrieve a shared comparison by its ID.
    
    URL: GET /shared/{share_id}
    
    Path Parameters:
        - share_id: Unique identifier from share URL
    
    Returns: Complete comparison result with metadata
    
    Side Effect: Increments view count for analytics
    
    Use: When someone opens a shared comparison link
    """
    try:
        # Load shared comparison from database
        shared = load_shared(share_id)
        
        if not shared:
            raise HTTPException(status_code=404, detail="Shared comparison not found")
        
        # Track analytics: increment view count
        increment_shared_view_count(share_id)
        shared["views"] += 1
        
        return shared
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving shared comparison: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve comparison")


# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# ASK FOLLOW-UP QUESTION ENDPOINT - Conversational Q&A
# --------------------------------------------------------------------------
@app.post("/ask-followup")
async def ask_followup(request: FollowUpRequest):
    """
    Ask follow-up questions about a comparison.
    
    URL: POST /ask-followup
    
    Request Body:
        - comparison_id: ID of the original comparison
        - question: User's follow-up question
    
    Returns:
        - answer: AI's response to the question
        - comparison_id: Comparison identifier
        - conversation_history: Number of messages in conversation
    
    Examples:
        "Which one has better battery life?"
        "What if I need it for gaming?"
        "Can you explain the price difference?"
    
    Process Flow:
        1. Retrieve original comparison (from memory or database)
        2. Create prompt with comparison context + user question
        3. Get answer from AI
        4. Save Q&A to database and memory
        5. Return answer to user
    
    Use: Chat interface below comparison results
    """
    try:
        comparison_id = request.comparison_id
        
        # ---------------------------------------------------------------
        # STEP 1: RETRIEVE ORIGINAL COMPARISON
        # ---------------------------------------------------------------
        # Try memory first (fast - active session)
        memory_data = conversation_memory.get(comparison_id)
        
        # If not in memory, try database (slower - persistent storage)
        if not memory_data:
            db_comparison = get_comparison_from_db(comparison_id)
            if db_comparison:
                memory_data = {
                    "original_comparison": db_comparison["original_comparison"],
                    "items": db_comparison["items"],
                    "category": db_comparison["category"],
                    "messages": db_comparison["messages"]
                }
        
        # Comparison not found anywhere
        if not memory_data:
            raise HTTPException(
                status_code=404, 
                detail="Comparison not found. Please create a comparison first."
            )
        
        # Extract comparison data
        original_comparison = memory_data["original_comparison"]
        items = memory_data["items"]
        category = memory_data["category"]
        
        # ---------------------------------------------------------------
        # STEP 2: VERIFY LLM AVAILABILITY
        # ---------------------------------------------------------------
        if not llm:
            raise HTTPException(
                status_code=503,
                detail="LLM service is not available. Please set OPENAI_API_KEY environment variable."
            )
        
        # ---------------------------------------------------------------
        # STEP 3: CREATE FOLLOW-UP PROMPT AND GET ANSWER
        # ---------------------------------------------------------------
        # Get the follow-up prompt template
        followup_prompt = get_followup_prompt()
        
        # Create a LangChain chain (prompt | llm)
        # The | operator pipes prompt output to llm input
        followup_chain = followup_prompt | llm
        
        # Invoke the chain with context + question
        response = followup_chain.invoke({
            "items": ", ".join(items),  # Items that were compared
            "category": category,  # Category of comparison
            "comparison_result": json.dumps(original_comparison, indent=2),  # Full comparison
            "question": request.question  # User's question
        })
        
        # Extract text answer from AI response
        answer = response.content
        
        # ---------------------------------------------------------------
        # STEP 4: SAVE Q&A TO DATABASE
        # ---------------------------------------------------------------
        # Persist follow-up conversation for future retrieval
        add_comparison_message(comparison_id, "user", request.question)
        add_comparison_message(comparison_id, "assistant", answer)
        
        # ---------------------------------------------------------------
        # STEP 5: UPDATE IN-MEMORY CONVERSATION
        # ---------------------------------------------------------------
        # If comparison is in active memory, update the chat history
        if comparison_id in conversation_memory:
            chat_history = conversation_memory[comparison_id]["chat_history"]
            chat_history.add_user_message(request.question)
            chat_history.add_ai_message(answer)
            conversation_history_len = len(chat_history.messages)
        else:
            # Otherwise get count from database
            db_comp = get_comparison_from_db(comparison_id)
            conversation_history_len = len(db_comp["messages"]) if db_comp else 0
        
        logger.info(f"💬 Follow-up answered for comparison {comparison_id}")
        
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

# --------------------------------------------------------------------------
# GET FOLLOW-UP HISTORY ENDPOINT - Retrieve Conversation
# --------------------------------------------------------------------------
@app.get("/followup-history/{comparison_id}")
async def get_followup_history(comparison_id: str):
    """
    Get all follow-up Q&A messages for a comparison.
    
    URL: GET /followup-history/{comparison_id}
    
    Path Parameters:
        - comparison_id: Unique comparison identifier
    
    Returns:
        - comparison_id: Comparison identifier
        - history: List of messages [{"role": "user/assistant", "content": "..."}]
    
    Use: Display conversation history in chat interface
    """
    # Try memory first (faster - active session)
    if comparison_id in conversation_memory:
        memory_data = conversation_memory[comparison_id]
        chat_history = memory_data["chat_history"]
        
        # Convert LangChain message objects to simple dictionaries
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
    
    # Try database (slower - persistent storage)
    db_comparison = get_comparison_from_db(comparison_id)
    if db_comparison:
        return {
            "comparison_id": comparison_id,
            "history": db_comparison["messages"]
        }
    
    # Not found anywhere
    raise HTTPException(status_code=404, detail="Comparison not found")


# --------------------------------------------------------------------------
# ============================================================================
# ANALYTICS ENDPOINTS - Usage Statistics & Insights
# ============================================================================

# --------------------------------------------------------------------------
# TRENDING COMPARISONS ENDPOINT - Most Viewed Shared Links
# --------------------------------------------------------------------------
@app.get("/analytics/trending")
async def get_trending():
    """
    Get trending shared comparisons based on view counts.
    
    URL: GET /analytics/trending
    
    Returns: List of top 10 most viewed shared comparisons from last 7 days
    
    Response Format:
        [
            {
                "share_id": "abc123",
                "category": "gadgets",
                "items": ["iPhone 15", "Samsung S24"],
                "views": 142,
                "created_at": "2024-01-15T10:30:00"
            },
            ...
        ]
    
    Use: Display trending comparisons on homepage
    """
    try:
        from database.connection import get_db_session
        with get_db_session() as db:
            # Query top 10 most viewed from last 7 days
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


# --------------------------------------------------------------------------
# POPULAR ITEMS ENDPOINT - Most Compared Products/Services
# --------------------------------------------------------------------------
@app.get("/analytics/popular-items")
async def get_popular_items():
    """
    Get most frequently compared items across all users.
    
    URL: GET /analytics/popular-items
    
    Returns: Top 10 most compared items with their comparison counts
    
    Response Format:
        [
            {
                "name": "iPhone 15",
                "category": "gadgets",
                "comparison_count": 234
            },
            ...
        ]
    
    Use: Display "Popular Comparisons" section, trending items
    """
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


# --------------------------------------------------------------------------
# CATEGORY STATISTICS ENDPOINT - Usage by Category
# --------------------------------------------------------------------------
@app.get("/analytics/category-stats")
async def get_category_statistics(days: int = 30):
    """
    Get comparison statistics broken down by category.
    
    URL: GET /analytics/category-stats?days=30
    
    Query Parameters:
        - days: Number of days to analyze (default: 30)
    
    Returns: Statistics for each category
    
    Response Format:
        {
            "stats": {
                "gadgets": {"count": 150, "percentage": 35.5},
                "cars": {"count": 80, "percentage": 18.9},
                "technologies": {"count": 120, "percentage": 28.4},
                ...
            }
        }
    
    Use: Analytics dashboard, usage insights
    """
    try:
        from database.connection import get_db_session
        with get_db_session() as db:
            stats = get_category_stats(db, days=days)
            return {"stats": stats}
    except Exception as e:
        logger.error(f"Error getting category stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get category stats")


# --------------------------------------------------------------------------
# DASHBOARD SUMMARY ENDPOINT - Comprehensive Analytics
# --------------------------------------------------------------------------
@app.get("/analytics/dashboard")
async def get_dashboard(days: int = 30):
    """
    Get comprehensive dashboard summary with all analytics.
    
    URL: GET /analytics/dashboard?days=30
    
    Query Parameters:
        - days: Number of days to analyze (default: 30)
    
    Returns: Comprehensive dashboard data including:
        - Total comparisons and users
        - Most compared items
        - Category statistics
        - Feedback metrics
        - Trends over time
        - Winner distribution
    
    Use: Main dashboard page
    """
    try:
        from database.connection import get_db_session
        with get_db_session() as db:
            summary = get_dashboard_summary(db, days=days)
            return summary
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error getting dashboard: {error_msg}")
        logger.exception(e)  # Log full traceback
        # Return more detailed error message for debugging
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to get dashboard data: {error_msg}"
        )


# --------------------------------------------------------------------------
# TRENDS ENDPOINT - Time-based Trends
# --------------------------------------------------------------------------
@app.get("/analytics/trends")
async def get_trends(days: int = 30):
    """
    Get comparison trends over time.
    
    URL: GET /analytics/trends?days=30
    
    Query Parameters:
        - days: Number of days to analyze (default: 30)
    
    Returns: Daily comparison counts
    
    Response Format:
        [
            {"date": "2024-01-15", "count": 45},
            {"date": "2024-01-16", "count": 52},
            ...
        ]
    
    Use: Trend charts, time-series visualization
    """
    try:
        from database.connection import get_db_session
        with get_db_session() as db:
            trends = get_comparison_count_by_date(db, days=days)
            return {"trends": trends}
    except Exception as e:
        logger.error(f"Error getting trends: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get trends")


# --------------------------------------------------------------------------
# WINNER DISTRIBUTION ENDPOINT - Winner Statistics
# --------------------------------------------------------------------------
@app.get("/analytics/winner-distribution")
async def get_winner_stats(days: int = 30):
    """
    Get distribution of winners from personalized comparisons.
    
    URL: GET /analytics/winner-distribution?days=30
    
    Query Parameters:
        - days: Number of days to analyze (default: 30)
    
    Returns: Winner statistics
    
    Response Format:
        [
            {"item": "iPhone 15", "count": 42, "percentage": 28.5},
            {"item": "Samsung S24", "count": 35, "percentage": 23.7},
            ...
        ]
    
    Use: Winner charts, popularity metrics
    """
    try:
        from database.connection import get_db_session
        with get_db_session() as db:
            winners = get_winner_distribution(db, days=days)
            return {"winners": winners}
    except Exception as e:
        logger.error(f"Error getting winner distribution: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get winner distribution")


# ============================================================================
# FEEDBACK ENDPOINTS - User Feedback System
# ============================================================================

# --------------------------------------------------------------------------
# SUBMIT FEEDBACK ENDPOINT - Create Feedback
# --------------------------------------------------------------------------
@app.post("/feedback")
async def submit_feedback(data: FeedbackRequest):
    """
    Submit feedback for a comparison.
    
    URL: POST /feedback
    
    Request Body:
        - comparison_id: ID of the comparison
        - rating: 1-5 star rating
        - comment: Optional text comment
        - user_id: Optional user identifier
    
    Returns: Created feedback entry
    
    Use: After user views comparison results
    """
    try:
        from database.connection import get_db_session
        with get_db_session() as db:
            # comparison_id in FeedbackRequest is the comparison's comparison_id
            feedback = create_feedback(
                db,
                comparison_id=data.comparison_id,  # This is the comparison's comparison_id
                rating=data.rating,
                comment=data.comment
            )
            
            logger.info(f"⭐ Feedback submitted for comparison {data.comparison_id}: {data.rating} stars")
            
            return {
                "message": "Feedback submitted successfully",
                "feedback_id": feedback.id,
                "rating": feedback.rating
            }
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit feedback")


# --------------------------------------------------------------------------
# GET FEEDBACK ENDPOINT - Retrieve Feedback
# --------------------------------------------------------------------------
@app.get("/feedback/{comparison_id}")
async def get_feedback(comparison_id: str):
    """
    Get all feedback for a specific comparison.
    
    URL: GET /feedback/{comparison_id}
    
    Path Parameters:
        - comparison_id: ID of the comparison
    
    Returns: List of feedback entries
    
    Use: Display feedback on comparison page
    """
    try:
        from database.connection import get_db_session
        with get_db_session() as db:
            feedback_list = get_feedback_by_comparison(db, comparison_id)  # comparison_id is comparison's comparison_id
            
            return {
                "comparison_id": comparison_id,
                "feedback_count": len(feedback_list),
                "feedback": [
                    {
                        "id": f.id,
                        "rating": f.rating,
                        "comment": f.comment,
                        "created_at": f.created_at.isoformat()
                    }
                    for f in feedback_list
                ]
            }
    except Exception as e:
        logger.error(f"Error getting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get feedback")


# --------------------------------------------------------------------------
# FEEDBACK STATISTICS ENDPOINT - Aggregate Feedback Metrics
# --------------------------------------------------------------------------
@app.get("/analytics/feedback-stats")
async def get_feedback_statistics(days: int = 30):
    """
    Get aggregate feedback statistics.
    
    URL: GET /analytics/feedback-stats?days=30
    
    Query Parameters:
        - days: Number of days to analyze (default: 30)
    
    Returns: Feedback metrics including:
        - Total feedback count
        - Average rating (comprehensiveness score)
        - Rating distribution
        - Decision helpfulness metrics
        - Winner match scores
    
    Use: Dashboard, quality metrics
    """
    try:
        from database.connection import get_db_session
        with get_db_session() as db:
            stats = get_feedback_stats(db, days=days)
            return stats
    except Exception as e:
        logger.error(f"Error getting feedback stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get feedback statistics")


# ============================================================================
# ANALYTICS CHAT ENDPOINT - MCP-powered dashboard chat
# ============================================================================
@app.post("/analytics/chat")
async def analytics_chat(request: dict):
    """
    Chat with AI assistant about dashboard analytics using MCP tools.
    
    URL: POST /analytics/chat
    
    Request Body:
        - message: User's question about dashboard
        - conversation_history: Optional list of previous messages
    
    Returns:
        - answer: AI's response
        - tool_used: Optional tool name if MCP tool was called
        - conversation_history: Updated conversation history
    
    Use: Dashboard analytics chat interface in frontend
    """
    try:
        import os
        import json
        import requests
        from typing import Dict, List
        
        # Check if Groq is available
        try:
            from groq import Groq
            GROQ_AVAILABLE = True
        except ImportError:
            raise HTTPException(
                status_code=503,
                detail="Groq library not installed. Install with: pip install groq"
            )
        
        # Get API key
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=503,
                detail="GROQ_API_KEY not set. Set it as environment variable."
            )
        
        user_message = request.get("message", "")
        conversation_history = request.get("conversation_history", [])
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # MCP Server URL
        MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001")
        
        # Get available tools from MCP server
        try:
            logger.info(f"🔧 Connecting to MCP server at {MCP_SERVER_URL}...")
            tools_response = requests.get(f"{MCP_SERVER_URL}/tools", timeout=5)
            if tools_response.status_code == 200:
                tools = tools_response.json().get("tools", [])
                logger.info(f"✅ Connected to MCP server, found {len(tools)} tools")
            else:
                logger.warning(f"⚠️ MCP server returned status {tools_response.status_code}")
                tools = []
        except requests.exceptions.ConnectionError as e:
            logger.error(f"❌ Could not connect to MCP server at {MCP_SERVER_URL}")
            logger.error(f"   Make sure MCP server is running: python backend/mcp_server.py")
            tools = []
        except Exception as e:
            logger.warning(f"⚠️ Could not connect to MCP server: {e}")
            tools = []
        
        # Format tools for prompt
        def format_tools_for_prompt(tools: List[Dict]) -> str:
            if not tools:
                return "No tools available."
            tool_descriptions = []
            for tool in tools:
                name = tool.get("name", "")
                desc = tool.get("description", "")
                tool_descriptions.append(f"- {name}: {desc}")
            return "\n".join(tool_descriptions)
        
        # Invoke MCP tool
        def invoke_mcp_tool(tool_name: str, parameters: Dict = None) -> Dict:
            try:
                payload = {
                    "tool_name": tool_name,
                    "parameters": parameters or {}
                }
                response = requests.post(
                    f"{MCP_SERVER_URL}/tools/invoke",
                    json=payload,
                    timeout=10
                )
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        return result.get("data", {})
                    else:
                        return {"error": result.get("error", "Unknown error")}
                return {"error": f"HTTP {response.status_code}"}
            except Exception as e:
                return {"error": str(e)}
        
        # Initialize Groq client
        client = Groq(api_key=api_key.strip())
        
        # Build system prompt
        system_prompt = f"""You are an intelligent analytics assistant for COMPAIR, a product comparison platform.

IMPORTANT CONTEXT - What COMPAIR Already Has:
✅ User feedback system (ratings, comments)
✅ Comprehensive analytics dashboard
✅ Comparison caching system
✅ Follow-up conversation feature
✅ Personalization (preferences, budget, use case)
✅ Real-time search integration (Brave Search API - external service, no custom search algorithm)
✅ Database storage (PostgreSQL)
✅ Trending comparisons tracking
✅ Category statistics
✅ MCP server for AI assistants

CRITICAL: ABOUT SEARCH:
- COMPAIR uses Brave Search API (external service) - there is NO custom search algorithm
- The only search-related code is query building (adding category keywords to search queries)
- Brave Search handles all ranking, relevance, and search logic
- DO NOT suggest "improving search algorithms" - suggest optimizing query building instead (e.g., "refine category-specific keywords in search queries", "tune search query parameters")

CRITICAL: ABOUT CATEGORIES:
- Categories (Gadgets, Cars, Technologies, Destinations, Shows, Other) are primarily organizational labels
- The ONLY difference between categories is the PERSONALIZATION OPTIONS:
  * Each category has different priority options (e.g., Gadgets: "Camera Quality", Cars: "Fuel Efficiency")
  * Each category has different use case labels (e.g., Gadgets: "How will you use it?", Cars: "What's your driving need?")
- ALL categories use the SAME comparison engine, same features, same logic
- Categories do NOT have different features or capabilities - they're just labels for context
- DO NOT suggest copying features from one category to another - categories don't have category-specific features
- If a category is popular, suggest OPTIMIZING that category based on data (e.g., "Analyze what makes Cars comparisons successful and replicate those patterns", "Review feedback from Cars category to identify optimization opportunities")

You have access to these tools to analyze dashboard data:
{format_tools_for_prompt(tools)}

When the user asks about:
- Dashboard overview, general metrics → use get_dashboard_overview or generate_insights_report
- Quality scores, ratings, comprehensiveness → use get_comparison_quality
- Decision making, winner matching → use get_decision_confidence
- User preferences (personalized vs general) → use get_preference_usage
- Category statistics → use get_category_insights
- Popular comparisons → use get_popular_comparisons
- User feedback, comments → use get_user_feedback_summary
- Trends, activity over time → use get_activity_trends
- General insights and recommendations → use generate_insights_report
- Last/most recent comparison → use get_last_comparison
- Recent comparisons (last N) → use get_recent_comparisons
- Questions about the last comparison (what was it about, what items, who won, etc.) → use get_last_comparison

IMPORTANT INSTRUCTIONS:
1. When the user asks a question that requires data, you MUST call the appropriate tool FIRST
2. To call a tool, respond with EXACTLY: TOOL_CALL:tool_name
3. For tools that accept parameters, you can specify them like: TOOL_CALL:tool_name:param1=value1,param2=value2
4. I will execute the tool and give you the results
5. Then provide a clear, conversational answer using that data
6. When answering questions about the last comparison, use get_last_comparison to get full details, then answer based on that data
7. ALWAYS include actionable recommendations - but focus on OPTIMIZATION and DATA-DRIVEN INSIGHTS, not new features
8. Be helpful, insightful, and solution-oriented

CRITICAL: RECOMMENDATIONS MUST BE SPECIFIC AND ACTIONABLE:

- For AREAS OF IMPROVEMENT (low scores, declining trends, negative feedback):
  * Identify the SPECIFIC problem and explain what the data reveals
  * Suggest OPTIMIZATION strategies (e.g., "Focus on improving prompts for categories with low scores", "Analyze feedback from 2-star ratings to identify patterns")
  * Provide DATA-DRIVEN insights (e.g., "13% giving 2 stars suggests targeting specific comparison types")
  * DO NOT suggest features that already exist (feedback collection, analytics, etc.)

- For STRENGTHS (high scores, positive trends, good metrics):
  * Acknowledge what's working well
  * Suggest how to MAINTAIN or AMPLIFY success (e.g., "Continue focusing on categories with high scores", "Replicate successful patterns")
  * Identify what's driving success from the data
  * If a specific category is popular/successful, suggest analyzing WHY it's successful and how to optimize it further (e.g., "Cars category is popular - analyze what makes those comparisons successful and see if you can optimize prompt tuning or search strategies for that category")
  * DO NOT suggest copying features from one category to another - categories don't have different features

- For NEUTRAL DATA (just reporting metrics):
  * Explain what the data means in plain language
  * Suggest OPTIMIZATION opportunities based on patterns in the data
  * Focus on TUNING existing features rather than new features
  * If a category shows high usage, suggest ways to optimize that category based on data patterns (e.g., "Cars category has high usage - analyze feedback patterns, review comparison quality scores, and optimize prompts specifically for car comparisons")
  * DO NOT suggest copying features between categories - suggest data-driven optimizations instead
  * DO NOT suggest "improving search algorithms" - COMPAIR uses Brave Search API (external), suggest optimizing query building instead (e.g., "refine search query keywords for better results")

RESPONSE STYLE:
- Be conversational and natural - write as if you're having a friendly discussion
- Explain what the data means in plain language
- ALWAYS include 2-3 specific, data-driven recommendations
- Focus on OPTIMIZATION, TUNING, and DATA INSIGHTS - not new features
- Make recommendations feel like helpful suggestions based on the actual data

Example of good conversational style with data-driven recommendations:
"Your comparison quality score is 4.3/5, which is pretty good! About 56% of users gave 5-star ratings, showing most people are happy. However, 13% gave 2-star ratings - that's worth investigating.

Looking at the data, I'd suggest diving into those 2-star ratings to see if there's a pattern - maybe certain categories or comparison types are consistently scoring lower. You could analyze the feedback comments to identify common themes. Also, if you notice certain item pairs getting lower scores, you might want to review how the AI handles those specific comparisons and tune the prompts accordingly.

The good news is you're doing well overall - maybe focus on replicating what's working for the 56% who love it!"

REMEMBER: Recommendations should be SPECIFIC, DATA-DRIVEN, and focus on OPTIMIZATION of existing features, not suggesting new features that already exist."""
        
        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})
        
        # Call Groq with timeout handling
        try:
            logger.info(f"💬 Calling Groq API for analytics chat...")
            logger.info(f"   User message: {user_message[:100]}...")
            logger.info(f"   Conversation history length: {len(conversation_history)}")
            
            # Groq SDK timeout is handled via client initialization or request-level timeout
            # Note: timeout parameter may not be available in all SDK versions
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_tokens=1500
            )
            assistant_message = response.choices[0].message.content
            logger.info(f"✅ Groq API responded successfully (length: {len(assistant_message)} chars)")
        except Exception as e:
            logger.error(f"❌ Groq API error: {e}")
            logger.error(f"   Error type: {type(e).__name__}")
            import traceback
            logger.error(f"   Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get response from AI: {str(e)}"
            )
        
        tool_used = None
        
        # Check if LLM wants to call a tool
        if "TOOL_CALL:" in assistant_message:
            # Extract tool name and parameters
            tool_line = [line for line in assistant_message.split("\n") if "TOOL_CALL:" in line]
            if tool_line:
                tool_call_str = tool_line[0].replace("TOOL_CALL:", "").strip()
                
                # Parse tool name and parameters
                # Format: TOOL_CALL:tool_name or TOOL_CALL:tool_name:param1=value1,param2=value2
                if ":" in tool_call_str and "=" in tool_call_str:
                    # Has parameters
                    parts = tool_call_str.split(":", 1)
                    tool_name = parts[0].strip()
                    params_str = parts[1].strip()
                    # Parse parameters (simple format: param1=value1,param2=value2)
                    parameters = {}
                    for param_pair in params_str.split(","):
                        if "=" in param_pair:
                            key, value = param_pair.split("=", 1)
                            key = key.strip()
                            value = value.strip()
                            # Try to convert to int if possible
                            try:
                                if value.isdigit():
                                    value = int(value)
                            except:
                                pass
                            parameters[key] = value
                else:
                    tool_name = tool_call_str
                    parameters = {}
                
                tool_used = tool_name
                
                # Invoke tool
                tool_result = invoke_mcp_tool(tool_name, parameters)
                
                # Format tool result
                if "error" in tool_result:
                    tool_data = f"Error: {tool_result['error']}"
                else:
                    tool_data = json.dumps(tool_result, indent=2)
                
                # Check if tool result already has recommendations
                has_recommendations = False
                recommendations_text = ""
                if isinstance(tool_result, dict):
                    if "recommendations" in tool_result and tool_result["recommendations"]:
                        has_recommendations = True
                        recs = tool_result["recommendations"]
                        if isinstance(recs, list):
                            recommendations_text = "\n".join([f"- {r}" if isinstance(r, str) else f"- {r.get('text', r)}" for r in recs])
                        else:
                            recommendations_text = str(recs)
                    elif "improvements" in tool_result and tool_result["improvements"]:
                        has_recommendations = True
                        improvements = tool_result["improvements"]
                        if isinstance(improvements, list):
                            recommendations_text = "\n".join([f"- {i}" if isinstance(i, str) else f"- {i.get('text', i)}" for i in improvements])
                
                # Get final answer with tool data
                if has_recommendations:
                    follow_up = f"""The tool '{tool_name}' returned this data:
{tool_data}

Provide a clear, conversational answer to the user's question using this data. 

IMPORTANT: This data includes recommendations that you should naturally incorporate into your response:
{recommendations_text}

Be conversational and natural - explain what the data means and include the recommendations naturally in your response. Don't use rigid formatting like "**Summary:**" or "**Key Findings:**" - just have a natural conversation."""
                else:
                    follow_up = f"""The tool '{tool_name}' returned this data:
{tool_data}

Provide a clear, conversational answer to the user's question using this data. 

IMPORTANT: You MUST include 2-3 actionable recommendations based on the data. Focus on OPTIMIZATION and DATA-DRIVEN INSIGHTS - suggest how to tune existing features, analyze patterns, or replicate success. DO NOT suggest new features that already exist (feedback collection, analytics, etc.). Make recommendations natural and conversational - weave them into your response. Explain what the data means and then naturally suggest specific optimizations based on the actual data patterns."""
                
                messages.append({"role": "assistant", "content": assistant_message})
                messages.append({"role": "user", "content": follow_up})
                
                try:
                    logger.info(f"💬 Calling Groq API for final response with tool data...")
                    logger.info(f"   Tool used: {tool_name}")
                    final_response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=messages,
                        temperature=0.7,
                        max_tokens=2000  # Increased to allow for recommendations
                    )
                    assistant_message = final_response.choices[0].message.content
                    logger.info(f"✅ Groq API final response received (length: {len(assistant_message)} chars)")
                except Exception as e:
                    logger.error(f"❌ Groq API error on final response: {e}")
                    logger.error(f"   Error type: {type(e).__name__}")
                    import traceback
                    logger.error(f"   Traceback: {traceback.format_exc()}")
                    # Fallback: return tool data directly
                    assistant_message = f"I retrieved the data, but encountered an error processing it. Here's what I found:\n\n{tool_data}"
                
                # Validate that recommendations are present, if not add them
                # Check for recommendation keywords (more flexible - not just "recommendations:")
                has_recs = any(keyword in assistant_message.lower() for keyword in [
                    "recommend", "suggest", "should", "consider", "try", "improve", 
                    "enhance", "focus on", "next step", "action"
                ])
                
                if not has_recs:
                    logger.warning("⚠️ Response missing recommendations, adding them naturally...")
                    # Extract key metrics from tool result to generate recommendations
                    if isinstance(tool_result, dict):
                        quality_score = tool_result.get("comprehensiveness_score") or tool_result.get("data", {}).get("comprehensiveness_score")
                        if quality_score is None and "data" in tool_result:
                            quality_score = tool_result["data"].get("comprehensiveness_score")
                        
                        # Generate optimization-focused recommendations based on data
                        recs = []
                        if quality_score is not None:
                            if quality_score < 3.5:
                                recs.append("analyze patterns in low-rated comparisons to identify which categories or item types need prompt tuning")
                                recs.append("review feedback comments from 2-star ratings to find common themes that could guide prompt improvements")
                            elif quality_score < 4.0:
                                recs.append("focus on replicating successful comparison patterns from high-scoring categories")
                                recs.append("tune prompts for categories showing lower scores based on feedback patterns")
                            else:
                                recs.append("continue monitoring trends to maintain quality")
                                recs.append("analyze what's working well in high-scoring comparisons to replicate success")
                        
                        if not recs:
                            recs = [
                                "analyze data patterns to identify optimization opportunities",
                                "review feedback trends to guide prompt tuning",
                                "focus on replicating successful patterns from high-performing areas"
                            ]
                        
                        # Add recommendations naturally at the end
                        recommendations_text = " To improve things, I'd recommend: " + ", ".join([f"{r}" for r in recs[:-1]]) + f", and {recs[-1]}."
                        assistant_message += recommendations_text
                        logger.info("✅ Added recommendations naturally to response")
        
        logger.info(f"💬 Analytics chat completed successfully")
        logger.info(f"   User message: {user_message[:100]}...")
        logger.info(f"   Tool used: {tool_used or 'None'}")
        logger.info(f"   Response length: {len(assistant_message)} chars")
        
        # Update conversation history
        updated_history = conversation_history + [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_message}
        ]
        
        return {
            "answer": assistant_message,
            "tool_used": tool_used,
            "conversation_history": updated_history
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analytics chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process chat: {str(e)}")


# ============================================================================
# SERVER STARTUP
# ============================================================================
if __name__ == "__main__":
    """
    Start the FastAPI server using Uvicorn.
    
    Run with: python main.py
    
    The server will be available at:
        - Local: http://localhost:8000
        - API Docs: http://localhost:8000/docs (Swagger UI)
        - ReDoc: http://localhost:8000/redoc (Alternative API docs)
    
    Configuration:
        - host: Defined in utilities/constants.py (default: 0.0.0.0)
        - port: Defined in utilities/constants.py (default: 8000)
    """
    import uvicorn
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)