"""Search utilities for different LLM providers."""

import os
import requests
from typing import List, Dict, Any, Optional
from google.genai import Client
from langchain_core.runnables import RunnableConfig

from agent.configuration import Configuration
from agent.llm_factory import LLMFactory
from agent.utils import get_citations, insert_citation_markers, resolve_urls


class SearchUtils:
    """Utilities for performing web searches with different LLM providers."""

    @staticmethod
    def perform_web_research(
        search_query: str,
        provider: str,
        model_name: str,
        prompt: str,
        search_id: int,
        config: RunnableConfig
    ) -> Dict[str, Any]:
        """Perform web research using the appropriate method for the provider.
        
        Args:
            search_query: The search query to execute
            provider: The LLM provider
            model_name: The model name
            prompt: The formatted prompt
            search_id: Unique ID for this search
            config: Configuration for the runnable
            
        Returns:
            Dictionary containing search results and metadata
        """
        if provider == "gemini":
            return SearchUtils._gemini_web_search(search_query, model_name, prompt, search_id)
        else:
            return SearchUtils._generic_web_search(search_query, provider, model_name, prompt, search_id)

    @staticmethod
    def _gemini_web_search(
        search_query: str,
        model_name: str,
        prompt: str,
        search_id: int
    ) -> Dict[str, Any]:
        """Perform web search using Gemini's native Google Search tool."""
        from google.genai import Client
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set")
        genai_client = Client(api_key=api_key)
        
        response = genai_client.models.generate_content(
            model=model_name,
            contents=prompt,
            config={
                "tools": [{"google_search": {}}],
                "temperature": 0,
            },
        )
        
        # Resolve URLs and get citations
        resolved_urls = resolve_urls(
            response.candidates[0].grounding_metadata.grounding_chunks, search_id
        )
        citations = get_citations(response, resolved_urls)
        modified_text = insert_citation_markers(response.text, citations)
        sources_gathered = [item for citation in citations for item in citation["segments"]]
        
        return {
            "sources_gathered": sources_gathered,
            "search_query": [search_query],
            "web_research_result": [modified_text],
        }

    @staticmethod
    def _generic_web_search(
        search_query: str,
        provider: str,
        model_name: str,
        prompt: str,
        search_id: int
    ) -> Dict[str, Any]:
        """Perform web search using external search API and then use LLM to analyze results."""
        # First, perform web search using external API
        search_results = SearchUtils._perform_search_api(search_query)
        
        if not search_results:
            # If no search API is available, use LLM to provide a general response
            llm = LLMFactory.create_llm(
                provider=provider,
                model_name=model_name,
                temperature=0,
                max_retries=2,
            )
            
            enhanced_prompt = f"""{prompt}

Note: Unable to perform web search due to missing search API configuration. Please provide a response based on your training data knowledge for the query: "{search_query}"
"""
            
            response = llm.invoke(enhanced_prompt)
            
            return {
                "sources_gathered": [{
                    "label": "LLM Knowledge Base",
                    "value": "No external search performed",
                    "short_url": "[1]",
                    "snippet": "Response based on model training data"
                }],
                "search_query": [search_query],
                "web_research_result": [response.content],
            }
        
        # Format search results for LLM
        formatted_results = SearchUtils._format_search_results(search_results)
        
        # Create enhanced prompt with search results
        enhanced_prompt = f"""{prompt}

Based on the following search results, provide a comprehensive analysis:

{formatted_results}

Please provide your analysis with citations in the format [1], [2], etc., referencing the sources above."""
        
        # Use LLM to analyze the search results
        llm = LLMFactory.create_llm(
            provider=provider,
            model_name=model_name,
            temperature=0,
            max_retries=2,
        )
        
        response = llm.invoke(enhanced_prompt)
        
        # Create sources list
        sources_gathered = []
        for i, result in enumerate(search_results, 1):
            sources_gathered.append({
                "label": result.get("title", ""),
                "value": result.get("link", ""),
                "short_url": f"[{i}]",
                "snippet": result.get("snippet", "")
            })
        
        return {
            "sources_gathered": sources_gathered,
            "search_query": [search_query],
            "web_research_result": [response.content],
        }

    @staticmethod
    def _perform_search_api(query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Perform web search using external search API."""
        # Try Google Custom Search API first
        google_api_key = os.getenv("GOOGLE_API_KEY")
        google_cx = os.getenv("GOOGLE_CX")
        
        if google_api_key and google_cx:
            return SearchUtils._google_custom_search(query, google_api_key, google_cx, num_results)
        
        # Try SerpAPI as fallback
        serpapi_key = os.getenv("SERPAPI_API_KEY")
        if serpapi_key:
            return SearchUtils._serpapi_search(query, serpapi_key, num_results)
        
        # Try Bing Search API as another fallback
        bing_api_key = os.getenv("BING_SEARCH_API_KEY")
        if bing_api_key:
            return SearchUtils._bing_search(query, bing_api_key, num_results)
        
        print("Warning: No search API configured. Please set one of: GOOGLE_API_KEY+GOOGLE_CX, SERPAPI_API_KEY, or BING_SEARCH_API_KEY")
        return []

    @staticmethod
    def _google_custom_search(
        query: str, 
        api_key: str, 
        cx: str, 
        num_results: int
    ) -> List[Dict[str, Any]]:
        """Perform search using Google Custom Search API."""
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": api_key,
                "cx": cx,
                "q": query,
                "num": min(num_results, 10)  # Google API limit
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get("items", []):
                results.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", "")
                })
            
            return results
        except Exception as e:
            print(f"Google Custom Search API error: {e}")
            return []

    @staticmethod
    def _serpapi_search(query: str, api_key: str, num_results: int) -> List[Dict[str, Any]]:
        """Perform search using SerpAPI."""
        try:
            url = "https://serpapi.com/search"
            params = {
                "api_key": api_key,
                "engine": "google",
                "q": query,
                "num": num_results
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get("organic_results", []):
                results.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", "")
                })
            
            return results
        except Exception as e:
            print(f"SerpAPI error: {e}")
            return []

    @staticmethod
    def _bing_search(query: str, api_key: str, num_results: int) -> List[Dict[str, Any]]:
        """Perform search using Bing Search API."""
        try:
            url = "https://api.bing.microsoft.com/v7.0/search"
            headers = {
                "Ocp-Apim-Subscription-Key": api_key
            }
            params = {
                "q": query,
                "count": num_results,
                "responseFilter": "Webpages"
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get("webPages", {}).get("value", []):
                results.append({
                    "title": item.get("name", ""),
                    "link": item.get("url", ""),
                    "snippet": item.get("snippet", "")
                })
            
            return results
        except Exception as e:
            print(f"Bing Search API error: {e}")
            return []

    @staticmethod
    def _format_search_results(results: List[Dict[str, Any]]) -> str:
        """Format search results for LLM consumption."""
        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(
                f"[{i}] {result.get('title', 'No title')}\n"
                f"URL: {result.get('link', 'No URL')}\n"
                f"Snippet: {result.get('snippet', 'No snippet')}\n"
            )
        return "\n".join(formatted)

    @staticmethod
    def get_available_search_apis() -> List[str]:
        """Get list of available search APIs based on environment variables."""
        available = []
        
        if os.getenv("GOOGLE_API_KEY") and os.getenv("GOOGLE_CX"):
            available.append("google_custom_search")
        
        if os.getenv("SERPAPI_API_KEY"):
            available.append("serpapi")
        
        if os.getenv("BING_SEARCH_API_KEY"):
            available.append("bing_search")
        
        return available 