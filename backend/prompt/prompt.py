"""
Prompt templates for the CompareMate API.

This module contains all prompt templates used by the LangChain LLM chains
for comparison and follow-up question handling.
"""

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage


def get_comparison_prompt(winner_instructions: str, format_instructions: str):
    """
    Returns a function that creates comparison prompt with given parameters.
    
    Args:
        winner_instructions: Dynamic instructions about winner selection based on user preferences
        format_instructions: Format instructions from the Pydantic parser
        
    Returns:
        Function that takes dict with category, items, preferences_text and returns messages list
    """
    # Build the complete system message with format_instructions and winner_instructions already injected
    # No template variables in the system message - it's completely resolved
    system_message_content = f"""You are a smart AI comparison assistant.

Your task is to provide a detailed comparison between the items the user provides.

🔍 CRITICAL: You will receive REAL-TIME SEARCH RESULTS from Brave Search API. 
- Use the search results as your PRIMARY and MOST RELIABLE source of information
- ONLY use facts that are present in the search results
- If specific information is not in the search results, explicitly state "Information not found in search results" rather than guessing
- Do NOT make up specifications, prices, features, or any factual data
- If search results are available, they take precedence over your training data
- This is essential to prevent hallucinations and ensure accuracy

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

{format_instructions}"""
    
    # Return a callable that creates the full prompt with user inputs
    def create_prompt(inputs: dict):
        """Create messages with the given inputs."""
        search_results = inputs.get('search_results', '')
        
        user_message_content = f"""Category: {inputs['category']}
Items to compare: {inputs['items']}
{inputs['preferences_text']}

{search_results}

Please compare these items: {inputs['items']}

Remember: Use ONLY the information from the search results provided above. If information is missing, state that clearly rather than inferring."""
        
        return [
            SystemMessage(content=system_message_content),
            HumanMessage(content=user_message_content)
        ]
    
    return create_prompt


def get_followup_prompt() -> ChatPromptTemplate:
    """
    Returns the follow-up question prompt template.
    
    Returns:
        ChatPromptTemplate for answering follow-up questions about comparisons
    """
    return ChatPromptTemplate.from_messages([
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


def get_winner_instructions_with_preferences() -> str:
    """
    Returns winner instructions when user has provided preferences.
    
    Returns:
        String with instructions for personalized winner selection
    """
    return """The user HAS provided preferences.

You MUST include:
- "personalized_winner": The actual item name that best matches their preferences
- "winner_reason": 2-3 sentences explaining WHY this item won based on their specific needs

Example:
"personalized_winner": "iPhone 15"
"winner_reason": "Based on your priority for camera quality and ecosystem, the iPhone 15 offers the best overall experience."
"""


def get_winner_instructions_without_preferences() -> str:
    """
    Returns winner instructions when user has NOT provided preferences.
    
    Returns:
        String with instructions for balanced recommendation without winner
    """
    return """The user has NOT provided any preferences.

You MUST NOT include a personalized winner. Instead:
- Set "personalized_winner": null
- Set "winner_reason": null  
- Provide a balanced "recommendation" that works for different use cases

Example recommendation:
"The iPhone 15 is ideal for users in the Apple ecosystem. The Samsung S24 offers more customization and flexibility."
"""

