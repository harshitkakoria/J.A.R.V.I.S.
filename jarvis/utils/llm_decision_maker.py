"""
LLM-based Decision Making Model for Query Classification
Uses Groq LLM with comprehensive decision prompt to classify queries
"""

from groq import Groq
from dotenv import dotenv_values
from typing import Tuple

# Load environment variables
env_vars = dotenv_values()
GROQ_API_KEY = env_vars.get("GROQ_API_KEY", "")

# Decision-making prompt
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


class LLMDecisionMaker:
    """Decision-making model using Groq LLM for query classification"""
    
    def __init__(self):
        """Initialize Groq client"""
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"
    
    def classify_query(self, query: str) -> Tuple[str, str]:
        """
        Classify a query using LLM decision-making model
        
        Args:
            query: User query to classify
        
        Returns:
            Tuple of (classification_type, full_response)
            where classification_type is one of: general, realtime, open, close, play, 
                                                 generate image, reminder, system, content, 
                                                 google search, youtube search, exit
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=150,
                temperature=0.3,
                messages=[
                    {"role": "system", "content": DECISION_PROMPT},
                    {"role": "user", "content": query}
                ]
            )
            
            # Extract response text
            decision_response = response.choices[0].message.content.strip()
            
            # Parse the classification type
            classification_type = self._extract_classification_type(decision_response)
            
            return classification_type, decision_response
            
        except Exception as e:
            print(f"Error in LLM decision maker: {e}")
            # Fallback to rule-based
            return self._fallback_classification(query), query
    
    def _extract_classification_type(self, response: str) -> str:
        """
        Extract classification type from LLM response
        
        Args:
            response: LLM response text
        
        Returns:
            Classification type (general, realtime, open, close, etc.)
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
    
    def _fallback_classification(self, query: str) -> str:
        """
        Fallback rule-based classification when LLM fails
        
        Args:
            query: User query to classify
        
        Returns:
            Classification type
        """
        query_lower = query.lower()
        
        # Exit
        if any(word in query_lower for word in ["bye", "goodbye", "quit", "exit"]):
            return "exit"
        
        # Automation - Open
        if query_lower.startswith("open "):
            return "open"
        
        # Automation - Close
        if query_lower.startswith("close "):
            return "close"
        
        # Automation - Play
        if query_lower.startswith("play "):
            return "play"
        
        # Automation - Generate Image
        if "generate image" in query_lower:
            return "generate_image"
        
        # Automation - Reminder
        if "reminder" in query_lower or "remind me" in query_lower:
            return "reminder"
        
        # Automation - System
        if any(word in query_lower for word in ["mute", "unmute", "volume", "screenshot"]):
            return "system"
        
        # Real-time indicators
        realtime_keywords = ["latest", "current", "recent", "today", "breaking",
                            "news", "prime minister", "president", "who is",
                            "what is today", "today's", "recent update"]
        if any(keyword in query_lower for keyword in realtime_keywords):
            return "realtime"
        
        # Default to general
        return "general"
    
    def get_full_response(self, query: str) -> dict:
        """
        Get full classification response with metadata
        
        Args:
            query: User query to classify
        
        Returns:
            Dictionary with classification details
        """
        classification_type, llm_response = self.classify_query(query)
        
        return {
            "query": query,
            "classification_type": classification_type,
            "llm_response": llm_response,
            "model": self.model
        }


if __name__ == "__main__":
    # Test the decision maker
    decision_maker = LLMDecisionMaker()
    
    test_queries = [
        "What is the latest news?",
        "Open Facebook",
        "Who is the current prime minister of India?",
        "Tell me about quantum mechanics",
        "Close Notepad",
        "Play let her go",
        "What's the time?",
        "Bye Jarvis",
        "Generate image of a lion",
        "Open Chrome, Firefox and close Notepad"
    ]
    
    print("=" * 60)
    print("LLM DECISION MAKER TEST")
    print("=" * 60)
    
    for query in test_queries:
        result = decision_maker.get_full_response(query)
        print(f"\nQuery: {result['query']}")
        print(f"Classification: {result['classification_type']}")
        print(f"Response: {result['llm_response']}")
        print("-" * 60)
