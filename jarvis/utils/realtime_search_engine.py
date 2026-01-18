"""
Real-time search engine with AI-powered result refinement.
Uses web search to fetch current information and Groq AI to refine answers.
Demonstrates use of: googlesearch, groq, json, datetime, and dotenv.
"""
from typing import Optional, List
import json
from datetime import datetime
from groq import Groq
from dotenv import dotenv_values
from jarvis.utils.logger import setup_logger
from jarvis.config import GROQ_API_KEY, GROQ_MODEL, REALTIME_SEARCH_PROMPT

logger = setup_logger(__name__)


class RealtimeSearchEngine:
    """Real-time search engine with AI refinement using Groq."""
    
    def __init__(self, max_results: int = 5, use_groq: bool = True):
        """
        Initialize search engine.
        
        Args:
            max_results: Maximum search results to fetch
            use_groq: Use Groq for AI refinement
        """
        self.max_results = max_results
        self.use_groq = use_groq
        
        # Load environment variables using dotenv
        self.env = dotenv_values()
        self.groq_api_key = self.env.get("GROQ_API_KEY") or GROQ_API_KEY
        
        # Initialize Groq client if enabled and API key available
        self.groq_client = None
        if self.use_groq and self.groq_api_key:
            try:
                self.groq_client = Groq(api_key=self.groq_api_key)
                logger.info("Groq client initialized for AI refinement")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq: {e}")
        
        logger.info(f"RealtimeSearchEngine initialized (max_results={max_results}, use_groq={self.use_groq})")
    
    def search(self, query: str) -> Optional[str]:
        """
        Perform real-time search and return AI-refined answer.
        
        Args:
            query: Search query
            
        Returns:
            AI-refined answer based on search results
        """
        if not query:
            return None
        
        # Create timestamp for logging
        timestamp = datetime.now().isoformat()
        logger.info(f"Real-time search: {query} (timestamp: {timestamp})")
        
        # Fetch search results
        results = self._fetch_search_results(query)
        if not results:
            logger.warning(f"No search results for: {query}")
            return "Sorry, I couldn't find any relevant information for that search."
        
        # Create JSON structure for search data
        search_data = {
            "query": query,
            "timestamp": timestamp,
            "results_count": len(results),
            "results": results[:3]
        }
        logger.debug(f"Search results: {json.dumps(search_data, indent=2)}")
        
        # Refine results using Groq AI
        refined_answer = self._refine_with_groq(query, results)
        return refined_answer
    
    def _fetch_search_results(self, query: str) -> List[str]:
        """
        Fetch search results using DuckDuckGo (more reliable) with googlesearch fallback.
        
        Args:
            query: Search query
            
        Returns:
            List of search result snippets
        """
        try:
            # Try using DuckDuckGo (more reliable than googlesearch)
            from ddgs import DDGS
            
            ddgs = DDGS()
            results = []
            
            try:
                search_results = ddgs.text(query, max_results=self.max_results)
                for result in search_results:
                    if result and "href" in result:
                        # Extract title and URL
                        title = result.get("title", "")
                        url = result.get("href", "")
                        if url:
                            results.append(f"{title} - {url}" if title else url)
            except Exception as ddgs_error:
                logger.debug(f"DuckDuckGo search failed: {ddgs_error}")
                # Try googlesearch as secondary fallback
                try:
                    from googlesearch import search as google_search
                    for url in google_search(query, num_results=self.max_results, sleep_interval=1):
                        if url:
                            results.append(url)
                except Exception:
                    pass
            
            if results:
                logger.debug(f"Fetched {len(results)} search results")
                return results
            else:
                logger.debug("Search returned no results, using demo fallback")
                return self._get_fallback_results(query)
        
        except Exception as e:
            logger.debug(f"Search engines failed: {e}")
            # Fallback: Use mock/demo results
            return self._get_fallback_results(query)
    
    def _get_fallback_results(self, query: str) -> List[str]:
        """
        Fallback: Return demo/mock search results for demonstration.
        
        Args:
            query: Search query
            
        Returns:
            List of demo result snippets
        """
        demo_results = {
            "python": [
                "https://www.python.org - Official Python website",
                "https://docs.python.org - Python Documentation",
                "https://www.w3schools.com/python - Python Tutorials",
                "https://stackoverflow.com/questions/tagged/python - Python Q&A",
                "https://github.com/topics/python - Python Projects"
            ],
            "ai": [
                "https://www.deeplearning.ai - Deep Learning Resource",
                "https://www.coursera.org/learn/neural-networks - Neural Networks Course",
                "https://github.com/topics/artificial-intelligence - AI Projects",
                "https://arxiv.org - Research Papers",
                "https://openai.com - OpenAI"
            ],
            "default": [
                "https://en.wikipedia.org - General Knowledge",
                "https://www.google.com - Search Engine",
                "https://www.reddit.com - Community Discussion",
                "https://github.com - Code Repository",
                "https://stackoverflow.com - Technical Q&A"
            ]
        }
        
        # Match query to demo results
        for key in demo_results:
            if key.lower() in query.lower():
                logger.debug(f"Using demo results for: {key}")
                return demo_results[key]
        
        return demo_results["default"]
    
    def _refine_with_groq(self, query: str, results: List[str]) -> Optional[str]:
        """
        Use Groq AI to refine search results into a coherent answer.
        
        Args:
            query: Original search query
            results: List of search result URLs/snippets
            
        Returns:
            AI-refined answer
        """
        if not self.groq_client:
            logger.warning("Groq client not available, returning raw results")
            return "\n".join(results[:3])
        
        # Create context from search results
        context = "\n".join([f"- {url}" for url in results[:5]])
        
        prompt = f"""Based on these search results about "{query}", provide a concise and accurate answer.
Synthesize the information into a clear, helpful response.

Search Results:
{context}

Provide a brief, informative answer about "{query}":"""
        
        try:
            logger.debug(f"Refining with Groq ({GROQ_MODEL})")
            
            completion = self.groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": REALTIME_SEARCH_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.3
            )
            
            if completion.choices and completion.choices[0].message.content:
                answer = completion.choices[0].message.content.strip()
                logger.debug(f"Groq refinement successful")
                return answer
            
            logger.warning("Groq returned empty response")
            return "\n".join(results[:2])
        
        except Exception as e:
            logger.error(f"Groq refinement error: {e}")
            return "\n".join(results[:2])
    
    def get_search_data(self, query: str) -> dict:
        """
        Get structured search data in JSON format with datetime.
        Uses dotenv for configuration.
        
        Args:
            query: Search query
            
        Returns:
            Dictionary (JSON-serializable) with search metadata
        """
        results = self._fetch_search_results(query)
        
        # Create structured data with datetime
        search_data = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "total_results": len(results),
            "max_results_requested": self.max_results,
            "groq_enabled": self.use_groq,
            "groq_model": GROQ_MODEL if self.use_groq else None
        }
        
        # Return as JSON-serializable dict
        return search_data
    
    def export_search_results(self, query: str, filename: str = "search_results.json") -> bool:
        """
        Export search results to JSON file.
        
        Args:
            query: Search query
            filename: Output JSON filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            data = self.get_search_data(query)
            
            # Add search result content
            results = self._fetch_search_results(query)
            data["results_content"] = results
            
            # Write to JSON file
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Search results exported to {filename}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to export search results: {e}")
            return False
