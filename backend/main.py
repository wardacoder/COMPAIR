from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os, json
from typing import List, Optional
from datetime import datetime
import logging
import uuid

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.chat_message_histories import ChatMessageHistory

# ---------- LOGGING SETUP ---------- #
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- ENV SETUP ---------- #
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
logger.info(f"OpenAI key loaded successfully: {bool(openai_api_key)}")

# ---------- FASTAPI APP ---------- #
app = FastAPI(title="CompareMate API")

# ---------- CORS ---------- #
origins = [
    "http://localhost:3000",
    "https://comparemate.com"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- DATA STORAGE ---------- #
HISTORY_FILE = "comparison_history.json"
SHARED_FILE = "shared_comparisons.json"

for file in [HISTORY_FILE, SHARED_FILE]:
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump({}, f)

def load_history():
    with open(HISTORY_FILE, "r") as f:
        return json.load(f)

def save_history(data):
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_shared():
    with open(SHARED_FILE, "r") as f:
        return json.load(f)

def save_shared(data):
    with open(SHARED_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ---------- MEMORY STORAGE FOR FOLLOW-UPS ---------- #
conversation_memory = {}

# ---------- PYDANTIC MODELS ---------- #

class UserPreferences(BaseModel):
    priorities: Optional[List[str]] = Field(
        default=None,
        description="Features user cares about most"
    )
    budget: Optional[str] = Field(
        default=None, 
        description="Budget constraint"
    )
    use_case: Optional[str] = Field(
        default=None, 
        description="How user plans to use it"
    )

class CompareRequest(BaseModel):
    category: str
    items: List[str]
    criteria: Optional[str] = None
    user_preferences: Optional[UserPreferences] = None

class SaveComparisonRequest(BaseModel):
    user_id: str
    category: str
    items: List[str]
    result: dict

class ShareComparisonRequest(BaseModel):
    category: str
    items: List[str]
    result: dict
    user_id: Optional[str] = None

class FollowUpRequest(BaseModel):
    comparison_id: str
    question: str

class ComparisonOutput(BaseModel):
    introduction: Optional[str] = Field(
        default=None, 
        description="2-3 sentence introduction to the comparison"
    )
    table: Optional[List[dict]] = Field(
        default=None, 
        description="List of comparison features as dictionaries"
    )
    pros: Optional[List[str]] = Field(
        default=None, 
        description="List of 3-5 specific advantages"
    )
    cons: Optional[List[str]] = Field(
        default=None, 
        description="List of 3-5 specific disadvantages"
    )
    recommendation: Optional[str] = Field(
        default=None, 
        description="Clear, balanced recommendation"
    )
    personalized_winner: Optional[str] = Field(
        default=None, 
        description="Winner based on user preferences"
    )
    winner_reason: Optional[str] = Field(
        default=None,
        description="Explanation of why this item won"
    )
    message: Optional[str] = Field(
        default=None, 
        description="Error or informational message"
    )

# ---------- LANGCHAIN SETUP ---------- #

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    api_key=openai_api_key
)

parser = PydanticOutputParser(pydantic_object=ComparisonOutput)

# ✅ SIMPLE & CLEAN PROMPT
comparison_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a smart AI comparison assistant.

Your task is to provide a detailed comparison between the items the user provides.

📋 OUTPUT FORMAT:

Return a JSON object with these fields:

1. "introduction": A 4 to 5 sentences introduction to the comparison. Use the actual item names (e.g., "Let's compare iPhone 15 and Samsung S24...")

2. "table": An array of feature comparisons. Each entry should be a dictionary with:
   - "feature": The feature name (e.g., "Price", "Display", "Battery")
   - One key for EACH item using its exact name (e.g., "iPhone 15": "$799", "Samsung S24": "$799")
   
   Example:
   [
     {{"feature": "Price", "iPhone 15": "$799", "Samsung S24": "$799"}},
     {{"feature": "Display", "iPhone 15": "6.1 inch OLED", "Samsung S24": "6.2 inch AMOLED"}}
   ]

3. "pros": An array of advantages. Format each as "[Item Name]: [advantage]"
   Example: ["iPhone 15: Excellent ecosystem integration", "Samsung S24: Superior display technology"]

4. "cons": An array of disadvantages. Format each as "[Item Name]: [disadvantage]"
   Example: ["iPhone 15: Limited customization", "Samsung S24: Bloatware on device"]

For each item there should be 3 specific pros and 3 specific cons.

5. "recommendation": A balanced recommendation using the actual item names and keep it around 4 to 5 sentences long.
     
🏆 WINNER RULES:

{winner_instructions}

📱 CATEGORIES:

The web app has these categories:
- Gadgets (smartphones, laptops, tablets, wearables, etc.). You should expect brand names, model names and specific versions.
- Cars (vehicles of all types)
- Technologies (programming languages, frameworks, software, etc.)
- Destinations (countries, cities, travel locations)
- Shows (TV series, movies, etc.)
- Other (anything else)

✅ VALIDATION RULES:

When the category is Gadgets, Cars, Technologies, Destinations, or Shows:
- Make sure the items actually belong to that category
- If they don't fit, return: {{"message": "These items don't match the [category] category. Please check your selection."}}

When the category is "Other":
- Only reject if items are nonsensical (like single letters "f" vs "d")

🚫 ALWAYS REJECT:
- Single letters or very short gibberish (e.g., "f" vs "d", "xyz" vs "abc")
Return: {{"message": "Please enter clear, distinct, and comparable items."}}

⚠️ CRITICAL: Always use the ACTUAL item names provided by the user. Never use "Item 1", "Item 2", etc.

{format_instructions}"""),
    ("user", """Category: {category}
Items to compare: {items}
{preferences_text}

Please compare these items: {items}""")
])

# Follow-up prompt (unchanged)
followup_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert assistant helping users with follow-up questions about comparisons.

Context: The user previously compared {items} in the {category} category.

Original Comparison Result:
{comparison_result}

Your task: Answer the user's specific question about this comparison.
- Be concise and direct
- Reference specific data from the comparison
- Use the actual item names, not "Item 1", "Item 2"
- Provide actionable insights
- If question is outside the comparison scope, politely mention available information"""),
    ("user", "{question}")
])

# ---------- ENDPOINTS ---------- #

@app.get("/")
def root():
    return {"message": "Compair API is running! 🚀"}

@app.post("/compare")
async def compare_items(data: CompareRequest):
    """
    ✅ Simple validation with clear rules
    """
    try:
        logger.info(f"Comparison request: {data.category}, items: {data.items}")
        
        # Basic validation
        if not data.items or len(data.items) < 2:
            return {
                "message": "Please provide at least 2 items to compare."
            }
        
        # Check for very short items (gibberish)
        if any(len(item.strip()) < 2 for item in data.items):
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
            winner_instructions = """The user HAS provided preferences.

You MUST include:
- "personalized_winner": The actual item name that best matches their preferences
- "winner_reason": 2-3 sentences explaining WHY this item won based on their specific needs

Example:
"personalized_winner": "iPhone 15"
"winner_reason": "Based on your priority for camera quality and ecosystem, the iPhone 15 offers the best overall experience."
"""
        else:
            winner_instructions = """The user has NOT provided any preferences.

You MUST NOT include a personalized winner. Instead:
- Set "personalized_winner": null
- Set "winner_reason": null  
- Provide a balanced "recommendation" that works for different use cases

Example recommendation:
"The iPhone 15 is ideal for users in the Apple ecosystem. The Samsung S24 offers more customization and flexibility."
"""
        
        logger.info(f"Has preferences: {has_preferences}")
        
        # Create and invoke chain
        chain = comparison_prompt | llm | parser
        
        result = chain.invoke({
            "category": data.category,
            "items": ", ".join(data.items),
            "preferences_text": preferences_text,
            "winner_instructions": winner_instructions,
            "format_instructions": parser.get_format_instructions()
        })
        
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
        
        # Store in memory for follow-ups
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
        history = load_history()
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "category": data.category,
            "items": data.items,
            "result": data.result
        }

        if data.user_id not in history:
            history[data.user_id] = []
        history[data.user_id].append(entry)
        save_history(history)

        logger.info(f"Comparison saved for user: {data.user_id}")
        return {"message": "Comparison saved successfully", "entry": entry}
    
    except Exception as e:
        logger.error(f"Error saving comparison: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save comparison")

@app.post("/share-comparison")
async def share_comparison(data: ShareComparisonRequest):
    """Create shareable link for comparison"""
    try:
        share_id = str(uuid.uuid4())[:8]
        
        shared_data = {
            "share_id": share_id,
            "category": data.category,
            "items": data.items,
            "result": data.result,
            "created_at": datetime.utcnow().isoformat(),
            "user_id": data.user_id,
            "views": 0
        }
        
        shared = load_shared()
        shared[share_id] = shared_data
        save_shared(shared)
        
        logger.info(f"Comparison shared - ID: {share_id}")
        
        return {
            "share_url": f"https://compair.com/shared/{share_id}",
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
        shared = load_shared()
        
        if share_id not in shared:
            raise HTTPException(status_code=404, detail="Shared comparison not found")
        
        comparison = shared[share_id]
        comparison["views"] += 1
        shared[share_id] = comparison
        save_shared(shared)
        
        return comparison
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving shared comparison: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve comparison")

@app.get("/history/{user_id}")
def get_history(user_id: str):
    """Retrieve user's comparison history"""
    try:
        history = load_history()
        if user_id not in history:
            return {"user_id": user_id, "history": []}
        
        return {"user_id": user_id, "history": history[user_id]}
    
    except Exception as e:
        logger.error(f"Error retrieving history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve history")

@app.post("/ask-followup")
async def ask_followup(request: FollowUpRequest):
    """Ask follow-up questions about a comparison"""
    try:
        comparison_id = request.comparison_id
        
        if comparison_id not in conversation_memory:
            raise HTTPException(
                status_code=404, 
                detail="Comparison not found. Please create a comparison first."
            )
        
        memory_data = conversation_memory[comparison_id]
        original_comparison = memory_data["original_comparison"]
        chat_history = memory_data["chat_history"]
        
        followup_chain = followup_prompt | llm
        
        response = followup_chain.invoke({
            "items": ", ".join(memory_data["items"]),
            "category": memory_data["category"],
            "comparison_result": json.dumps(original_comparison, indent=2),
            "question": request.question
        })
        
        answer = response.content
        
        chat_history.add_user_message(request.question)
        chat_history.add_ai_message(answer)
        
        return {
            "answer": answer,
            "comparison_id": comparison_id,
            "conversation_history": len(chat_history.messages)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Follow-up error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process follow-up: {str(e)}")

@app.get("/followup-history/{comparison_id}")
async def get_followup_history(comparison_id: str):
    """Get conversation history for a comparison"""
    if comparison_id not in conversation_memory:
        raise HTTPException(status_code=404, detail="Comparison not found")
    
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

@app.delete("/history/{user_id}/{timestamp}")
def delete_history_item(user_id: str, timestamp: str):
    """Delete specific comparison from history"""
    try:
        history = load_history()
        if user_id not in history:
            raise HTTPException(status_code=404, detail="User not found")
        
        original_length = len(history[user_id])
        history[user_id] = [
            item for item in history[user_id] 
            if item.get("timestamp") != timestamp
        ]
        
        if len(history[user_id]) == original_length:
            raise HTTPException(status_code=404, detail="Comparison not found")
        
        save_history(history)
        return {"message": "Comparison deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting comparison: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete comparison")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)