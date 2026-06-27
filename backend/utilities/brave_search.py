"""
Brave Search API integration for fetching real-time information.

This module provides functions to search for items using the Brave Search API
to get accurate, up-to-date information and reduce hallucinations.
"""

import requests
import logging
from typing import List, Dict, Optional
from utilities.constants import (
    BRAVE_API_KEY,
    BRAVE_API_URL,
    BRAVE_SEARCH_COUNT,
    BRAVE_SEARCH_SNIPPETS,
    BRAVE_SEARCH_TIMEOUT
)

logger = logging.getLogger(__name__)


def search_item(item_name: str, category: str = None) -> Optional[Dict]:
    """
    Search for a single item using Brave Search API.
    
    Args:
        item_name: Name of the item to search for
        category: Optional category to refine search (e.g., "smartphone", "laptop")
        
    Returns:
        Dictionary with search results including snippets, descriptions, and web results
        Returns None if API key is not set or search fails
    """
    if not BRAVE_API_KEY:
        logger.warning("Brave API key not set - skipping search")
        return None
    
    try:
        # Build search query - add category context and specs keywords for better results
        query = item_name
        if category:
            # Add category-specific keywords to get more relevant specs
            category_keywords = {
                "gadgets": "specifications features price review",
                "cars": "specifications features price mpg horsepower",
                "technologies": "features comparison pros cons",
                "destinations": "travel guide things to do climate",
                "shows": "review rating cast plot summary",
                "other": "review comparison features"
            }
            keywords = category_keywords.get(category.lower(), "specifications features")
            query = f"{item_name} {keywords}"
        
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": BRAVE_API_KEY
        }
        
        params = {
            "q": query,
            "count": BRAVE_SEARCH_COUNT,
            "search_lang": "en",
            "country": "US",
            "safesearch": "moderate",
            "freshness": "py",
            "text_decorations": False,
            "spellcheck": True
        }
        
        response = requests.get(BRAVE_API_URL, headers=headers, params=params, timeout=BRAVE_SEARCH_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract relevant information
        web_results = data.get("web", {}).get("results", [])
        
        # Compile search results
        search_data = {
            "query": query,
            "results": [],
            "summary": ""
        }
        
        snippets = []
        for result in web_results[:BRAVE_SEARCH_COUNT]:  # Top N results based on configuration
            title = result.get("title", "")
            description = result.get("description", "")
            url = result.get("url", "")
            
            if description:
                snippets.append(description)
            
            search_data["results"].append({
                "title": title,
                "description": description,
                "url": url
            })
        
        # Create a summary from snippets - use configured number of snippets
        # This ensures more balanced information even if some descriptions are shorter
        if snippets:
            search_data["summary"] = "\n".join(snippets[:BRAVE_SEARCH_SNIPPETS])
        
        # Log search result statistics for debugging
        logger.info(f"✅ Brave Search completed for: {item_name}")
        logger.info(f"   Found {len(web_results)} total results, {len(snippets)} with descriptions")
        logger.info(f"   Summary length: {len(search_data.get('summary', ''))} chars")
        logger.info(f"   Total results entries: {len(search_data['results'])}")
        
        return search_data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Brave Search API error for {item_name}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"❌ Unexpected error in Brave Search for {item_name}: {str(e)}")
        return None


def search_items(items: List[str], category: str = None) -> Dict[str, Optional[Dict]]:
    """
    Search for multiple items using Brave Search API.
    
    Args:
        items: List of item names to search for
        category: Optional category to refine searches
        
    Returns:
        Dictionary mapping item names to their search results
    """
    results = {}
    
    for item in items:
        results[item] = search_item(item, category)
    
    return results


def search_specific_feature(item_name: str, feature: str) -> Optional[Dict]:
    """
    Search for a specific feature of an item.
    Used when initial search didn't provide enough information.
    
    Args:
        item_name: Name of the item
        feature: The specific feature to search for (e.g., "battery life", "price")
        
    Returns:
        Dictionary with search results for that specific feature
    """
    if not BRAVE_API_KEY:
        logger.warning("Brave API key not set - skipping feature search")
        return None
    
    try:
        # Build targeted query for the specific feature
        query = f"{item_name} {feature} specifications details"
        
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": BRAVE_API_KEY
        }
        
        params = {
            "q": query,
            "count": 5,  # Fewer results needed for specific feature
            "search_lang": "en",
            "country": "US",
            "safesearch": "moderate",
            "text_decorations": False,
            "spellcheck": True
        }
        
        response = requests.get(BRAVE_API_URL, headers=headers, params=params, timeout=BRAVE_SEARCH_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        web_results = data.get("web", {}).get("results", [])
        
        snippets = []
        for result in web_results[:5]:
            description = result.get("description", "")
            if description:
                snippets.append(description)
        
        logger.info(f"🔍 Feature search for '{item_name} - {feature}': Found {len(snippets)} snippets")
        
        return {
            "query": query,
            "feature": feature,
            "item": item_name,
            "summary": "\n".join(snippets) if snippets else ""
        }
        
    except Exception as e:
        logger.error(f"❌ Feature search error for {item_name} - {feature}: {str(e)}")
        return None


def search_pros_cons(item_name: str) -> Optional[Dict]:
    """
    Search specifically for pros and cons of an item.
    
    Args:
        item_name: Name of the item
        
    Returns:
        Dictionary with pros/cons search results
    """
    if not BRAVE_API_KEY:
        return None
    
    try:
        query = f"{item_name} pros cons advantages disadvantages review"
        
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": BRAVE_API_KEY
        }
        
        params = {
            "q": query,
            "count": 10,
            "search_lang": "en",
            "country": "US",
            "safesearch": "moderate",
            "text_decorations": False,
            "spellcheck": True
        }
        
        response = requests.get(BRAVE_API_URL, headers=headers, params=params, timeout=BRAVE_SEARCH_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        web_results = data.get("web", {}).get("results", [])
        
        snippets = []
        for result in web_results[:10]:
            description = result.get("description", "")
            if description:
                snippets.append(description)
        
        logger.info(f"🔍 Pros/Cons search for '{item_name}': Found {len(snippets)} snippets")
        
        return {
            "query": query,
            "item": item_name,
            "summary": "\n".join(snippets) if snippets else ""
        }
        
    except Exception as e:
        logger.error(f"❌ Pros/Cons search error for {item_name}: {str(e)}")
        return None


def check_for_missing_info(result_dict: dict) -> dict:
    """
    Check comparison result for missing information.
    
    Args:
        result_dict: The comparison result dictionary
        
    Returns:
        Dictionary with lists of missing items/features
    """
    missing = {
        "table_features": [],  # List of (item_name, feature) tuples
        "pros_items": [],      # List of item names missing pros
        "cons_items": []       # List of item names missing cons
    }
    
    # Patterns that indicate missing information
    missing_patterns = [
        "information not found",
        "not found",
        "n/a",
        "not available",
        "unknown",
        "data not available",
        "no information"
    ]
    
    def is_missing(value: str) -> bool:
        if not value:
            return True
        value_lower = value.lower().strip()
        return any(pattern in value_lower for pattern in missing_patterns)
    
    # Check table for missing values
    table = result_dict.get("table", [])
    items = result_dict.get("items", [])
    
    for row in table:
        feature = row.get("feature", "")
        for item in items:
            value = row.get(item, "")
            if is_missing(value):
                missing["table_features"].append((item, feature))
    
    # Check pros for missing info
    pros = result_dict.get("pros", [])
    for item in items:
        item_has_pros = any(item.lower() in pro.lower() for pro in pros if pro)
        if not item_has_pros:
            missing["pros_items"].append(item)
        else:
            # Check if any pro for this item says "not found"
            for pro in pros:
                if item.lower() in pro.lower() and is_missing(pro):
                    missing["pros_items"].append(item)
                    break
    
    # Check cons for missing info
    cons = result_dict.get("cons", [])
    for item in items:
        item_has_cons = any(item.lower() in con.lower() for con in cons if con)
        if not item_has_cons:
            missing["cons_items"].append(item)
        else:
            # Check if any con for this item says "not found"
            for con in cons:
                if item.lower() in con.lower() and is_missing(con):
                    missing["cons_items"].append(item)
                    break
    
    # Remove duplicates
    missing["pros_items"] = list(set(missing["pros_items"]))
    missing["cons_items"] = list(set(missing["cons_items"]))
    
    return missing


def fetch_missing_information(missing: dict) -> str:
    """
    Fetch additional search results for missing information.
    
    Args:
        missing: Dictionary from check_for_missing_info
        
    Returns:
        Formatted string with additional search results
    """
    additional_results = []
    
    # Search for missing table features
    for item, feature in missing["table_features"]:
        result = search_specific_feature(item, feature)
        if result and result.get("summary"):
            additional_results.append(f"\n📌 Additional info for {item} - {feature}:")
            additional_results.append(result["summary"])
    
    # Search for missing pros/cons
    items_needing_pros_cons = set(missing["pros_items"] + missing["cons_items"])
    for item in items_needing_pros_cons:
        result = search_pros_cons(item)
        if result and result.get("summary"):
            additional_results.append(f"\n📌 Pros/Cons for {item}:")
            additional_results.append(result["summary"])
    
    if additional_results:
        return "\n🔄 ADDITIONAL SEARCH RESULTS (for previously missing information):\n" + "\n".join(additional_results)
    
    return ""


def format_search_results_for_prompt(search_results: Dict[str, Optional[Dict]]) -> str:
    """
    Format search results for inclusion in LLM prompt.
    
    Args:
        search_results: Dictionary mapping item names to their search results
        
    Returns:
        Formatted string with search information
    """
    if not search_results or all(v is None for v in search_results.values()):
        return ""
    
    formatted_sections = []
    formatted_sections.append("\n🔍 REAL-TIME SEARCH RESULTS:")
    formatted_sections.append("Use these search results as your PRIMARY source. Supplement with your knowledge for any missing details.")
    formatted_sections.append("")
    
    for item_name, result in search_results.items():
        if result:
            formatted_sections.append(f"**{item_name}:**")
            
            # Include summary (contains up to 5 snippets for better coverage)
            if result.get("summary"):
                formatted_sections.append(result["summary"])
                # Count snippets in summary
                snippets_in_summary = len(result.get("summary", "").split("\n"))
            else:
                logger.warning(f"No summary available for {item_name}")
                formatted_sections.append("No search results summary available.")
                snippets_in_summary = 0
            
            # Include URLs for reference (but not duplicate descriptions since summary already has them)
            results_list = result.get("results", [])[:BRAVE_SEARCH_COUNT]
            urls_added = 0
            for res in results_list:
                if res.get("url"):
                    formatted_sections.append(f"  Source: {res['url']}")
                    urls_added += 1
            
            # Log formatting statistics for each item
            logger.info(f"Formatted search results for {item_name}: {snippets_in_summary} snippets in summary ({len(result.get('summary', ''))} chars), {urls_added} source URLs")
            
            if snippets_in_summary == 0:
                logger.warning(f"⚠️ No snippets found in search results for {item_name}")
            
            formatted_sections.append("")  # Empty line between items
        else:
            logger.warning(f"⚠️ No search results available for {item_name}")
            formatted_sections.append(f"**{item_name}:**")
            formatted_sections.append("No search results found for this item.")
            formatted_sections.append("")
    
    formatted_text = "\n".join(formatted_sections)
    logger.info(f"Total formatted search results length: {len(formatted_text)} chars")
    
    return formatted_text

