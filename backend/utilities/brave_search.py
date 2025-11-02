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
        # Build search query - add category context if provided
        query = item_name
        if category:
            query = f"{item_name} {category}"
        
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
    formatted_sections.append("Use the following search results as the PRIMARY source of information.")
    formatted_sections.append("Only use facts from these results. If information is not found, explicitly state that.")
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

