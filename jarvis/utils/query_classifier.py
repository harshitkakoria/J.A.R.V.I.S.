"""
Query Classifier: Differentiates between General, Real-time, and Automation queries.
Uses advanced heuristic pattern matching and keyword analysis - NO AI REQUIRED.
Fully offline, instant, and highly accurate classification.
"""
import re
from typing import Dict, List, Tuple
from jarvis.utils.logger import setup_logger

logger = setup_logger(__name__)


class QueryClassifier:
    """Classify queries into three categories: General, Real-time, Automation"""
    
    def __init__(self):
        """Initialize classifier with comprehensive keyword mappings"""
        # AUTOMATION: Action-oriented commands (highest priority)
        self.automation_patterns = {
            'app_control': ['open', 'close', 'launch', 'start', 'quit', 'exit', 'shutdown', 'restart'],
            'media_control': ['play', 'pause', 'stop', 'skip', 'next', 'previous', 'mute', 'unmute'],
            'system_control': ['turn on', 'turn off', 'enable', 'disable', 'activate', 'deactivate'],
            'file_operations': ['delete', 'create', 'save', 'copy', 'paste', 'move', 'rename', 'upload', 'download'],
            'communication': ['send', 'email', 'message', 'call', 'text', 'reply', 'forward'],
            'search_actions': ['search for', 'find', 'look for', 'google'],
            'scheduling': ['remind', 'schedule', 'set reminder', 'set timer', 'set alarm', 'alert'],
            'generation': ['generate', 'create', 'make', 'write', 'compose', 'draw'],
            'execution': ['run', 'execute', 'perform', 'do', 'take screenshot', 'capture'],
        }
        
        # REALTIME: Current/live information queries
        self.realtime_patterns = {
            'weather': ['weather', 'temperature', 'climate', 'rain', 'snow', 'cloudy', 'forecast'],
            'news': ['news', 'headline', 'breaking', 'latest', 'current event'],
            'finance': ['price', 'stock', 'market', 'bitcoin', 'crypto', 'exchange rate', 'forex'],
            'people': ['who is', 'tell me about', 'biography', 'information about', 'born', 'age', 'net worth'],
            'location': ['where is', 'location of', 'address', 'coordinates', 'direction'],
            'time': ['what time', 'current time', 'what is the time', 'what\'s the time', 'what time is it'],
            'current': ['today', 'right now', 'now', 'current', 'present', 'this moment'],
            'sports': ['score', 'match', 'game', 'result', 'winner', 'standings'],
            'entertainment': ['movie', 'show', 'release', 'premiere', 'actor', 'cast'],
            'technology': ['latest tech', 'new release', 'announcement', 'product launch'],
        }
        
        # GENERAL: Everything else (conversation, knowledge, reasoning)
        self.general_indicators = [
            'how', 'why', 'what', 'explain', 'understand', 'think', 'believe',
            'discuss', 'talk about', 'meaning', 'definition', 'example', 'help me',
            'advise', 'suggest', 'recommend', 'opinion', 'your opinion', 'you think'
        ]
    
    def classify(self, query: str) -> Dict:
        """
        Classify a query into one of three categories using pattern matching.
        
        Args:
            query: User's query
            
        Returns:
            Dict with:
            {
                'type': 'general' | 'realtime' | 'automation',
                'confidence': 0.0-1.0,
                'reasoning': 'why this classification',
                'needs_internet': bool,
                'needs_automation': bool,
                'keywords': [list of detected keywords],
                'matched_patterns': [patterns that matched]
            }
        """
        if not query or not query.strip():
            return {
                "type": "unknown",
                "confidence": 0.0,
                "reasoning": "Empty query",
                "needs_internet": False,
                "needs_automation": False,
                "keywords": [],
                "matched_patterns": []
            }
        
        # Use pure heuristic classification (NO AI)
        logger.debug("Using advanced heuristic classification (no AI)")
        return self._advanced_classify(query)
    
    def _advanced_classify(self, query: str) -> Dict:
        """Advanced heuristic classification using pattern matching"""
        query_lower = query.lower().strip()
        
        # Check for each type and score confidence
        automation_score, automation_keywords, automation_patterns = self._check_automation(query_lower)
        realtime_score, realtime_keywords, realtime_patterns = self._check_realtime(query_lower)
        general_score, general_keywords = self._check_general(query_lower)
        
        # Determine final type based on highest score
        scores = {
            'automation': automation_score,
            'realtime': realtime_score,
            'general': general_score
        }
        
        query_type = max(scores, key=scores.get)
        confidence = min(scores[query_type] / 100.0, 1.0)
        
        # Get all detected keywords
        all_keywords = automation_keywords + realtime_keywords + general_keywords
        all_patterns = automation_patterns + realtime_patterns
        
        # Build reasoning
        if query_type == 'automation':
            reasoning = f"Detected action command - patterns: {', '.join(set(all_patterns[:3]))}"
            needs_internet = False
            needs_automation = True
        elif query_type == 'realtime':
            reasoning = f"Detected real-time info request - patterns: {', '.join(set(all_patterns[:3]))}"
            needs_internet = True
            needs_automation = False
        else:
            reasoning = "General conversational or knowledge query"
            needs_internet = False
            needs_automation = False
        
        return {
            'type': query_type,
            'confidence': min(confidence, 1.0),
            'reasoning': reasoning,
            'needs_internet': needs_internet,
            'needs_automation': needs_automation,
            'keywords': list(set(all_keywords)),
            'matched_patterns': list(set(all_patterns))
        }
    
    def _check_automation(self, query: str) -> Tuple[float, List[str], List[str]]:
        """Check if query is automation/command type"""
        score = 0
        keywords = []
        patterns = []
        
        # Check each automation pattern
        for category, pattern_list in self.automation_patterns.items():
            for pattern in pattern_list:
                if pattern in query:
                    score += 30
                    keywords.append(pattern)
                    if category not in patterns:
                        patterns.append(category)
        
        # Check for action verbs without object
        action_verbs = ['open', 'close', 'play', 'send', 'delete', 'create', 'remind', 'take', 'generate']
        verb_count = sum(1 for verb in action_verbs if verb in query)
        if verb_count > 0:
            score += 20 * verb_count
        
        # Check for automation phrases
        automation_phrases = ['open and', 'open the', 'send me', 'remind me', 'tell me to',
                             'take a', 'generate a', 'create a', 'download', 'turn on', 'turn off']
        phrase_matches = sum(1 for phrase in automation_phrases if phrase in query)
        if phrase_matches > 0:
            score += 25 * phrase_matches
            patterns.append('automation_phrase')
        
        # Reduce score if it looks like a general info query about the topic
        # (e.g., "tell me about Python" - the topic is general knowledge, not automation)
        if 'tell me about' in query:
            # Check if it's asking about a programming language, concept, or person (general knowledge)
            general_topics = ['python', 'java', 'c++', 'javascript', 'machine learning', 'ai',
                             'algorithm', 'data structure', 'design pattern']
            if any(topic in query for topic in general_topics):
                score -= 20  # Reduce automation score
        
        return score, keywords, patterns
    
    def _check_realtime(self, query: str) -> Tuple[float, List[str], List[str]]:
        """Check if query requests real-time information"""
        score = 0
        keywords = []
        patterns = []
        
        # Check each realtime pattern
        for category, pattern_list in self.realtime_patterns.items():
            for pattern in pattern_list:
                if pattern in query:
                    score += 35
                    keywords.append(pattern)
                    if category not in patterns:
                        patterns.append(category)
        
        # Check for information request patterns
        info_requesters = ['who is', 'what is', 'where is', 'when is', 'why is', 'how is',
                          'tell me about', 'information about', 'details about', 'facts about']
        for phrase in info_requesters:
            if phrase in query:
                score += 25
                keywords.append(phrase)
                if 'info_request' not in patterns:
                    patterns.append('info_request')
        
        # Bonus for time-sensitive keywords
        time_sensitive = ['today', 'now', 'current', 'latest', 'recent', 'just', 'this moment', 'right now']
        ts_matches = sum(1 for ts in time_sensitive if ts in query)
        if ts_matches > 0:
            score += 20 * ts_matches
        
        # Extra boost for weather-specific queries
        if 'weather' in query:
            score += 15
        
        # Reduce if it looks like a general knowledge question about a person
        if 'tell me about' in query:
            general_knowledge = ['python', 'java', 'einstein', 'newton', 'algorithm', 'machine learning']
            if any(topic in query for topic in general_knowledge):
                score -= 15  # Slightly reduce realtime score
        
        return score, keywords, patterns
    
    def _check_general(self, query: str) -> Tuple[float, List[str]]:
        """Check if query is general conversational type"""
        score = 30
        keywords = []
        
        # Check for general indicators
        for indicator in self.general_indicators:
            if indicator in query:
                score += 15
                keywords.append(indicator)
        
        # Conversational starters
        conversational = ['hi', 'hello', 'hey', 'how are you', 'what about', 'i wonder',
                         'let\'s talk', 'discuss', 'what do you think', 'your opinion']
        conv_matches = sum(1 for conv in conversational if conv in query)
        if conv_matches > 0:
            score += 20 * conv_matches
        
        # Knowledge/learning questions
        knowledge = ['teach me', 'explain', 'meaning', 'definition', 'example', 'understand',
                    'learn', 'help me', 'advice', 'suggest', 'recommend']
        know_matches = sum(1 for know in knowledge if know in query)
        if know_matches > 0:
            score += 15 * know_matches
            keywords.extend([k for k in knowledge if k in query])
        
        # Special boost for tech/programming topics with "tell me about"
        # These are typically general knowledge questions, not realtime
        if 'tell me about' in query:
            general_topics = ['python', 'java', 'c++', 'javascript', 'algorithm', 
                             'data structure', 'machine learning', 'design pattern']
            if any(topic in query for topic in general_topics):
                score += 30  # Boost to prioritize general over realtime
        
        return score, keywords
    
    def _heuristic_classify(self, query: str) -> Dict:
        """Legacy heuristic classification method - redirects to advanced"""
        return self._advanced_classify(query)


class QueryRouter:
    """Route queries to appropriate handlers based on classification."""
    
    def __init__(self, brain=None):
        self.brain = brain
        self.classifier = QueryClassifier()
    
    def route(self, query: str) -> Dict:
        """
        Route a query to the appropriate handler.
        
        Returns:
            Dict with routing information and handler
        """
        # Classify the query
        classification = self.classifier.classify(query)
        query_type = classification.get("type", "general")
        
        logger.debug(f"Routing query as: {query_type}")
        
        return {
            "type": query_type,
            "classification": classification,
            "handler": self._get_handler(query_type)
        }
    
    def _get_handler(self, query_type: str):
        """Get the appropriate handler for query type."""
        if query_type == "general":
            return self._handle_general
        elif query_type == "realtime":
            return self._handle_realtime
        elif query_type == "automation":
            return self._handle_automation
        else:
            return self._handle_general
    
    def _handle_general(self, query: str) -> str:
        """Handle general queries with LLM."""
        if not self.brain or not hasattr(self.brain, '_llm_fallback'):
            return "General query handler not available"
        
        logger.debug("Handling as general query")
        response = self.brain._llm_fallback(query)
        return response or "I couldn't process that query"
    
    def _handle_realtime(self, query: str) -> str:
        """Handle real-time queries - web search + LLM."""
        logger.debug("Handling as real-time query")
        
        # Check for specific real-time skills first
        if self.brain:
            # Try keyword matching for real-time skills
            from jarvis.utils.helpers import extract_keywords
            matched_keywords = extract_keywords(
                query.lower(), 
                list(self.brain.keyword_map.keys())
            )
            
            if matched_keywords:
                skill_name = self.brain.keyword_map.get(matched_keywords[0])
                handler = self.brain.skills.get(skill_name)
                if handler:
                    try:
                        return handler(query)
                    except Exception as e:
                        logger.error(f"Error in realtime handler: {e}")
        
        # Fallback to web search + LLM
        try:
            from jarvis.skills.scrape import handle as scrape_handle
            result = scrape_handle(query)
            if result:
                return result
        except:
            pass
        
        # Final fallback to LLM
        if self.brain and hasattr(self.brain, '_llm_fallback'):
            return self.brain._llm_fallback(query)
        
        return "Could not retrieve real-time information"
    
    def _handle_automation(self, query: str) -> str:
        """Handle automation queries - skills + intent parsing."""
        logger.debug("Handling as automation query")
        
        if not self.brain:
            return "Automation handler not available"
        
        # Try AI intent parsing first
        if hasattr(self.brain, 'intent_parser'):
            command = self.brain.intent_parser.parse_command(query)
            if command and command.get("intent") != "unknown" and command.get("confidence", 0) > 0.5:
                if hasattr(self.brain, 'command_executor'):
                    try:
                        return self.brain.command_executor.execute(command)
                    except Exception as e:
                        logger.error(f"Error executing automation: {e}")
        
        # Try keyword matching
        from jarvis.utils.helpers import extract_keywords
        matched_keywords = extract_keywords(
            query.lower(), 
            list(self.brain.keyword_map.keys())
        )
        
        if matched_keywords:
            skill_name = self.brain.keyword_map.get(matched_keywords[0])
            handler = self.brain.skills.get(skill_name)
            if handler:
                try:
                    return handler(query)
                except Exception as e:
                    logger.error(f"Error in automation handler: {e}")
        
        return "I couldn't execute that command"
