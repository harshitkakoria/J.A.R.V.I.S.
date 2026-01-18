"""
Cohere-based Query Classifier with Decision-Making Model
Uses comprehensive prompt for accurate query classification
"""

from typing import Tuple
from dotenv import dotenv_values

try:
    import cohere
    COHERE_AVAILABLE = True
except ImportError:
    COHERE_AVAILABLE = False
    print("Warning: cohere package not installed. Install with: pip install cohere")

# Load environment variables
env_vars = dotenv_values()
COHERE_API_KEY = env_vars.get("COHERE_API_KEY", "")
USE_COHERE = env_vars.get("USE_COHERE", "true").lower() == "true"
COHERE_MODEL = env_vars.get("COHERE_MODEL", "command-r-v1:7k-token-free-trial")

# Decision-making prompt for Cohere
DECISION_PROMPT = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write a application and open it in notepad'
*** Do not answer any query, just decide what kind of query is given to you. ***
-> Respond with 'general ( query )' if a query can be answered by a llm model (conversational ai chatbot) and doesn't require any up to date information like if the query is 'who was akbar?' respond with 'general who was akbar?', if the query is 'how can i study more effectively?' respond with 'general how can i study more effectively?', if the query is 'can you help me with this math problem?' respond with 'general can you help me with this math problem?', if the query is 'Thanks, i really liked it.' respond with 'general thanks, i really liked it.' , if the query is 'what is python programming language?' respond with 'general what is python programming language?', etc. Respond with 'general (query)' if a query doesn't have a proper noun or is incomplete like if the query is 'who is he?' respond with 'general who is he?', if the query is 'what's his networth?' respond with 'general what's his networth?', if the query is 'tell me more about him.' respond with 'general tell me more about him.', and so on even if it require up-to-date information to answer. Respond with 'general (query)' if the query is asking about time, day, date, month, year, etc like if the query is 'what's the time?' respond with 'general what's the time?'.
-> Respond with 'realtime ( query )' if a query can not be answered by a llm model (because they don't have realtime data) and requires up to date information like if the query is 'who is indian prime minister' respond with 'realtime who is indian prime minister', if the query is 'tell me about facebook's recent update.' respond with 'realtime tell me about facebook's recent update.', if the query is 'tell me news about coronavirus.' respond with 'realtime tell me news about coronavirus.', etc and if the query is asking about any individual or thing like if the query is 'who is akshay kumar' respond with 'realtime who is akshay kumar', if the query is 'what is today's news?' respond with 'realtime what is today's news?', if the query is 'what is today's headline?' respond with 'realtime what is today's headline?', etc.
-> Respond with 'open (application name or website name)' if a query is asking to open any application like 'open facebook', 'open telegram', etc. but if the query is asking to open multiple applications, respond with 'open 1st application name, open 2nd application name' and so on.
-> Respond with 'close (application name)' if a query is asking to close any application like 'close notepad', 'close facebook', etc. but if the query is asking to close multiple applications or websites, respond with 'close 1st application name, close 2nd application name' and so on.
-> Respond with 'play (song name)' if a query is asking to play any song like 'play afsanay by ys', 'play let her go', etc. but if the query is asking to play multiple songs, respond with 'play 1st song name, play 2nd song name' and so on.
-> Respond with 'generate image (image prompt)' if a query is requesting to generate a image with given prompt like 'generate image of a lion', 'generate image of a cat', etc. but if the query is asking to generate multiple images, respond with 'generate image 1st image prompt, generate image 2nd image prompt' and so on.
-> Respond with 'reminder (datetime with message)' if a query is requesting to set a reminder like 'set a reminder at 9:00pm on 25th june for my business meeting.' respond with 'reminder 9:00pm 25th june business meeting'.
-> Respond with 'system (task name)' if a query is asking to mute, unmute, volume up, volume down , etc. but if the query is asking to do multiple tasks, respond with 'system 1st task, system 2nd task', etc.
-> Respond with 'content (topic)' if a query is asking to write any type of content like application, codes, emails or anything else about a specific topic but if the query is asking to write multiple types of content, respond with 'content 1st topic, content 2nd topic' and so on.
-> Respond with 'google search (topic)' if a query is asking to search a specific topic on google but if the query is asking to search multiple topics on google, respond with 'google search 1st topic, google search 2nd topic' and so on.
-> Respond with 'youtube search (topic)' if a query is asking to search a specific topic on youtube but if the query is asking to search multiple topics on youtube, respond with 'youtube search 1st topic, youtube search 2nd topic' and so on.
*** If the query is asking to perform multiple tasks like 'open facebook, telegram and close whatsapp' respond with 'open facebook, open telegram, close whatsapp' ***
*** If the user is saying goodbye or wants to end the conversation like 'bye jarvis.' respond with 'exit'.***
*** Respond with 'general (query)' if you can't decide the kind of query or if a query is asking to perform a task which is not mentioned above. ***
"""


class CohereQueryClassifier:
    """Advanced query classifier using Cohere with comprehensive decision-making model"""
    
    def __init__(self):
        """Initialize Cohere client"""
        self.client = None
        self.enabled = USE_COHERE and COHERE_AVAILABLE and COHERE_API_KEY
        
        if self.enabled:
            try:
                self.client = cohere.ClientV2(api_key=COHERE_API_KEY)
                print(f"✓ Cohere classifier initialized with model: {COHERE_MODEL}")
            except Exception as e:
                print(f"✗ Cohere initialization failed: {e}")
                self.enabled = False
    
    def classify_query(self, query: str) -> Tuple[str, float, str]:
        """
        Classify a query using Cohere or fall back to rule-based classification
        
        Args:
            query: The user query to classify
        
        Returns:
            Tuple of (query_type, confidence, reasoning)
            where query_type is one of: "general", "realtime", "open", "close", "play", 
                                        "generate_image", "reminder", "system", "content",
                                        "google_search", "youtube_search", "exit"
        """
        if self.enabled and self.client:
            try:
                response = self.client.chat(
                    model=COHERE_MODEL,
                    messages=[
                        {"role": "system", "content": DECISION_PROMPT},
                        {"role": "user", "content": query}
                    ]
                )
                
                classification_response = response.message.content[0].text.strip().lower()
                
                # Extract classification type from response
                classification_type = self._extract_classification_type(classification_response)
                
                return classification_type, 0.90, f"Cohere: {classification_response}"
                    
            except Exception as e:
                print(f"Cohere error: {e}, using rule-based fallback")
                return self._classify_rule_based(query)
        else:
            return self._classify_rule_based(query)
    
    def _extract_classification_type(self, response: str) -> str:
        """
        Extract classification type from Cohere response
        
        Args:
            response: Cohere response text
        
        Returns:
            Classification type
        """
        response_lower = response.lower()
        
        # Check for each classification type
        if response_lower.startswith("exit"):
            return "exit"
        elif response_lower.startswith("general"):
            return "general"
        elif response_lower.startswith("realtime"):
            return "realtime"
        elif response_lower.startswith("open"):
            return "open"
        elif response_lower.startswith("close"):
            return "close"
        elif response_lower.startswith("play"):
            return "play"
        elif response_lower.startswith("generate image"):
            return "generate_image"
        elif response_lower.startswith("reminder"):
            return "reminder"
        elif response_lower.startswith("system"):
            return "system"
        elif response_lower.startswith("content"):
            return "content"
        elif response_lower.startswith("google search"):
            return "google_search"
        elif response_lower.startswith("youtube search"):
            return "youtube_search"
        else:
            return "general"
    
    def _classify_rule_based(self, query: str) -> Tuple[str, float, str]:
        """
        Fallback rule-based classification when Cohere is unavailable
        Implements the same logic as the decision-making prompt
        
        Returns:
            Tuple of (query_type, confidence, reasoning)
        """
        query_lower = query.lower()
        
        # Exit
        if any(word in query_lower for word in ["bye", "goodbye", "quit", "exit", "bye jarvis"]):
            return "exit", 0.95, "Exit command detected"
        
        # Open (highest priority for automation)
        if query_lower.startswith("open "):
            return "open", 0.95, "Open application/website command"
        
        # Close
        if query_lower.startswith("close "):
            return "close", 0.95, "Close application command"
        
        # Play
        if query_lower.startswith("play "):
            return "play", 0.95, "Play media command"
        
        # Generate Image
        if "generate image" in query_lower:
            return "generate_image", 0.90, "Image generation request"
        
        # Reminder
        if "reminder" in query_lower or "remind me" in query_lower or "set a reminder" in query_lower:
            return "reminder", 0.90, "Reminder request"
        
        # System commands
        if any(word in query_lower for word in ["mute", "unmute", "volume up", "volume down", "screenshot"]):
            return "system", 0.90, "System command detected"
        
        # Content generation
        if any(phrase in query_lower for phrase in ["write a", "write an", "create a", "compose a", "draft a", "can you write"]):
            return "content", 0.85, "Content generation request"
        
        # Google Search
        if "google search" in query_lower or "search on google" in query_lower:
            return "google_search", 0.90, "Google search request"
        
        # YouTube Search
        if "youtube search" in query_lower or "search on youtube" in query_lower:
            return "youtube_search", 0.90, "YouTube search request"
        
        # Incomplete queries with pronouns MUST be checked first (general per prompt)
        if any(phrase in query_lower for phrase in ["who is he", "who is she", "what's his", "what's her", 
                                                      "tell me more about him", "tell me more about her"]):
            return "general", 0.75, "Incomplete query with pronoun (general per prompt)"
        
        # Real-time indicators (high priority)
        # Per prompt: specific proper nouns, current events, news, individuals
        realtime_keywords = ["who is", "prime minister", "president", "latest", "current", 
                             "recent update", "today's news", "today's headline", "breaking",
                             "tell me about", "news about", "tell me news"]
        realtime_patterns = ["who is the", "what is today's", "what are today's", 
                             "tell me about facebook", "tell me about", "recent update"]
        
        # Check for explicit patterns first
        for pattern in realtime_patterns:
            if pattern in query_lower:
                return "realtime", 0.90, "Real-time query pattern detected"
        
        # Then check keywords
        if any(keyword in query_lower for keyword in realtime_keywords):
            return "realtime", 0.85, "Real-time indicator keywords detected"
        
        # Time/Date queries (general, not realtime as per prompt)
        if any(word in query_lower for word in ["what's the time", "what time is it", "what day", "what date"]):
            return "general", 0.80, "Time/date query (handled by general per prompt)"
        
        # Gratitude/conversational (general)
        if any(word in query_lower for word in ["thanks", "thank you", "appreciated", "liked it"]):
            return "general", 0.85, "Conversational response"
        
        # General queries (default)
        general_keywords = ["who was", "what is", "how can i", "can you help", "explain", 
                           "why", "where", "meaning", "definition", "describe"]
        if any(keyword in query_lower for keyword in general_keywords):
            return "general", 0.80, "General information query pattern"
        
        # Default to general (as per prompt)
        return "general", 0.60, "Default classification (general per prompt)"
    
    def get_classification_analysis(self, query: str) -> dict:
        """
        Get full classification analysis with metadata
        
        Args:
            query: User query to analyze
        
        Returns:
            Dictionary with classification details
        """
        classification_type, confidence, reasoning = self.classify_query(query)
        
        return {
            "query": query,
            "classification_type": classification_type,
            "confidence": confidence,
            "reasoning": reasoning,
            "cohere_enabled": self.enabled
        }


if __name__ == "__main__":
    # Test the classifier
    classifier = CohereQueryClassifier()
    
    test_queries = [
        # General queries
        "who was akbar?",
        "how can i study more effectively?",
        "Thanks, i really liked it.",
        "what is python programming language?",
        "who is he?",
        "what's his networth?",
        "what's the time?",
        
        # Real-time queries
        "who is indian prime minister",
        "tell me about facebook's recent update.",
        "tell me news about coronavirus.",
        "who is akshay kumar",
        "what is today's news?",
        "what is today's headline?",
        
        # Automation queries
        "open facebook",
        "close notepad",
        "play afsanay by ys",
        "generate image of a lion",
        "set a reminder at 9:00pm on 25th june for my business meeting.",
        "mute",
        "can you write an application and open it in notepad",
        "google search artificial intelligence",
        "youtube search python tutorial",
        "open facebook, telegram and close whatsapp",
        "bye jarvis"
    ]
    
    print("\n" + "=" * 80)
    print("COHERE QUERY CLASSIFIER TEST WITH COMPREHENSIVE DECISION-MAKING MODEL")
    print("=" * 80)
    
    for query in test_queries:
        result = classifier.get_classification_analysis(query)
        print(f"\nQuery: {result['query']}")
        print(f"Type: {result['classification_type']} | Confidence: {result['confidence']:.0%}")
        print(f"Reasoning: {result['reasoning']}")
        print("-" * 80)
