"""
Enhanced Query Classifier with NLP Libraries
Combines heuristics + spaCy + Transformers for JARVIS-like intelligence
"""
import re
from typing import Dict, List, Tuple, Optional
from jarvis.utils.logger import setup_logger

logger = setup_logger(__name__)

# Try importing enhanced NLP libraries
try:
    import spacy
    SPACY_AVAILABLE = True
    nlp = spacy.load("en_core_web_sm")
    logger.info("spaCy loaded successfully")
except ImportError:
    SPACY_AVAILABLE = False
    logger.warning("spaCy not installed - install with: pip install spacy && python -m spacy download en_core_web_sm")

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
    try:
        # Load zero-shot classifier
        zero_shot_classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=-1  # CPU, change to 0 for GPU
        )
        logger.info("Transformers zero-shot classifier loaded")
    except Exception as e:
        logger.warning(f"Could not load transformers model: {e}")
        TRANSFORMERS_AVAILABLE = False
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers not installed - install with: pip install transformers torch")

try:
    from sentence_transformers import SentenceTransformer, util
    SENTENCE_TRANSFORMERS_AVAILABLE = True
    model = SentenceTransformer('all-MiniLM-L6-v2')
    logger.info("SentenceTransformers loaded")
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("SentenceTransformers not installed - install with: pip install sentence-transformers")


class EnhancedQueryClassifier:
    """Enhanced query classifier combining heuristics + NLP libraries"""
    
    def __init__(self):
        """Initialize with comprehensive pattern mappings"""
        # Automation patterns
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
        
        # Real-time patterns
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
        
        # General indicators
        self.general_indicators = [
            'how', 'why', 'what', 'explain', 'understand', 'think', 'believe',
            'discuss', 'talk about', 'meaning', 'definition', 'example', 'help me',
            'advise', 'suggest', 'recommend', 'opinion', 'your opinion', 'you think'
        ]
        
        # Templates for semantic similarity
        self.automation_templates = [
            "open an application",
            "control a device",
            "execute a command",
            "perform an action",
            "send a message",
            "create a file",
            "delete something",
            "schedule a reminder",
            "play media",
            "launch a program"
        ]
        
        self.realtime_templates = [
            "check current information",
            "get live data",
            "search for recent news",
            "find current weather",
            "check stock price",
            "look up person information",
            "find location details",
            "check current time",
            "find latest scores",
            "check upcoming events"
        ]
        
        self.general_templates = [
            "ask a question",
            "have a conversation",
            "discuss a topic",
            "get advice",
            "learn something new",
            "get an explanation",
            "understand a concept",
            "talk about something",
            "ask for opinion",
            "tell me about something"
        ]
        
        logger.info(f"EnhancedQueryClassifier initialized")
        logger.info(f"  spaCy: {'✓' if SPACY_AVAILABLE else '✗'}")
        logger.info(f"  Transformers: {'✓' if TRANSFORMERS_AVAILABLE else '✗'}")
        logger.info(f"  SentenceTransformers: {'✓' if SENTENCE_TRANSFORMERS_AVAILABLE else '✗'}")
    
    def classify(self, query: str) -> Dict:
        """
        Advanced classification using multiple techniques.
        
        Args:
            query: User's query
            
        Returns:
            Dict with classification results
        """
        if not query or not query.strip():
            return {
                "type": "unknown",
                "confidence": 0.0,
                "reasoning": "Empty query",
                "needs_internet": False,
                "needs_automation": False,
                "keywords": [],
                "matched_patterns": [],
                "method": "none"
            }
        
        query_lower = query.lower().strip()
        
        # Step 1: Quick heuristic check (fast)
        heuristic_result, heuristic_score = self._heuristic_classify(query_lower)
        
        # Step 2: spaCy analysis if available (entity recognition)
        spacy_result = None
        if SPACY_AVAILABLE:
            spacy_result = self._spacy_analyze(query_lower)
        
        # Step 3: Transformer zero-shot if available (semantic understanding)
        transformer_result = None
        if TRANSFORMERS_AVAILABLE:
            transformer_result = self._transformer_classify(query_lower)
        
        # Step 4: Semantic similarity if available
        semantic_result = None
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            semantic_result = self._semantic_classify(query_lower)
        
        # Step 5: Combine all results
        final_result = self._combine_results(
            query_lower,
            heuristic_result,
            heuristic_score,
            spacy_result,
            transformer_result,
            semantic_result
        )
        
        return final_result
    
    def _heuristic_classify(self, query: str) -> Tuple[str, float]:
        """Fast heuristic classification (original method)"""
        automation_score, _, _ = self._check_automation(query)
        realtime_score, _, _ = self._check_realtime(query)
        general_score, _ = self._check_general(query)
        
        scores = {
            'automation': automation_score,
            'realtime': realtime_score,
            'general': general_score
        }
        
        query_type = max(scores, key=scores.get)
        confidence = scores[query_type]
        
        return query_type, confidence
    
    def _spacy_analyze(self, query: str) -> Dict:
        """Analyze query using spaCy for entities and structure"""
        try:
            doc = nlp(query)
            
            entities = []
            for ent in doc.ents:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char
                })
            
            # Check entity types to refine classification
            entity_labels = set(ent.label_ for ent in doc.ents)
            
            analysis = {
                'entities': entities,
                'entity_labels': list(entity_labels),
                'tokens': [token.text for token in doc],
                'pos_tags': [(token.text, token.pos_) for token in doc],
                'lemmas': [token.lemma_ for token in doc]
            }
            
            logger.debug(f"spaCy analysis: {entity_labels}")
            return analysis
        except Exception as e:
            logger.error(f"spaCy analysis error: {e}")
            return None
    
    def _transformer_classify(self, query: str) -> Dict:
        """Zero-shot classification using Transformers"""
        try:
            candidate_labels = ["automation", "realtime", "general"]
            
            result = zero_shot_classifier(query, candidate_labels)
            
            scores = {label: score for label, score in zip(result['labels'], result['scores'])}
            best_type = result['labels'][0]
            best_score = result['scores'][0]
            
            logger.debug(f"Transformers result: {best_type} ({best_score:.2f})")
            
            return {
                'type': best_type,
                'scores': scores,
                'confidence': best_score,
                'all_labels': result['labels'],
                'all_scores': result['scores']
            }
        except Exception as e:
            logger.error(f"Transformer classification error: {e}")
            return None
    
    def _semantic_classify(self, query: str) -> Dict:
        """Semantic similarity using SentenceTransformers"""
        try:
            # Encode query
            query_embedding = model.encode(query, convert_to_tensor=True)
            
            # Encode all templates
            auto_embeddings = model.encode(self.automation_templates, convert_to_tensor=True)
            realtime_embeddings = model.encode(self.realtime_templates, convert_to_tensor=True)
            general_embeddings = model.encode(self.general_templates, convert_to_tensor=True)
            
            # Calculate similarities
            auto_scores = util.pytorch_cos_sim(query_embedding, auto_embeddings)[0]
            realtime_scores = util.pytorch_cos_sim(query_embedding, realtime_embeddings)[0]
            general_scores = util.pytorch_cos_sim(query_embedding, general_embeddings)[0]
            
            # Get max similarities
            auto_sim = float(max(auto_scores))
            realtime_sim = float(max(realtime_scores))
            general_sim = float(max(general_scores))
            
            scores = {
                'automation': auto_sim,
                'realtime': realtime_sim,
                'general': general_sim
            }
            
            best_type = max(scores, key=scores.get)
            
            logger.debug(f"Semantic similarity: {best_type} (scores: {scores})")
            
            return {
                'type': best_type,
                'scores': scores,
                'confidence': scores[best_type]
            }
        except Exception as e:
            logger.error(f"Semantic classification error: {e}")
            return None
    
    def _combine_results(self, query: str, heuristic_result: str, heuristic_score: float,
                        spacy_result: Optional[Dict], transformer_result: Optional[Dict],
                        semantic_result: Optional[Dict]) -> Dict:
        """Combine all classification methods into final result"""
        
        votes = {'automation': 0, 'realtime': 0, 'general': 0}
        scores = {'automation': 0, 'realtime': 0, 'general': 0}
        
        # Heuristic vote (weight: 1.0)
        votes[heuristic_result] += 1
        scores[heuristic_result] += heuristic_score / 100.0
        
        # Transformer vote (weight: 1.5)
        if transformer_result:
            votes[transformer_result['type']] += 1.5
            scores[transformer_result['type']] += transformer_result['confidence']
        
        # Semantic vote (weight: 1.3)
        if semantic_result:
            votes[semantic_result['type']] += 1.3
            scores[semantic_result['type']] += semantic_result['confidence']
        
        # spaCy entity-based hint (weight: 0.5)
        if spacy_result and spacy_result['entity_labels']:
            entity_labels = spacy_result['entity_labels']
            
            # Certain entity types suggest certain query types
            if any(label in ['PERSON', 'ORG', 'GPE'] for label in entity_labels):
                votes['realtime'] += 0.5  # Info about people/places/organizations
            
            if 'PRODUCT' in entity_labels:
                votes['automation'] += 0.3  # Likely app/tool control
        
        # Determine final classification
        final_type = max(votes, key=votes.get)
        final_score = scores[final_type] / max(votes[final_type], 0.1)
        
        # Determine method used
        methods = ['heuristic']
        if transformer_result:
            methods.append('transformer')
        if semantic_result:
            methods.append('semantic')
        if spacy_result:
            methods.append('spacy')
        
        method = '+'.join(methods) if len(methods) > 1 else methods[0]
        
        # Get keywords and patterns
        automation_keywords, automation_patterns = self._extract_keywords_patterns(query)
        
        # Build reasoning
        if final_type == 'automation':
            reasoning = f"Action command detected (patterns: {', '.join(automation_patterns[:2])})"
            needs_internet = False
            needs_automation = True
        elif final_type == 'realtime':
            reasoning = f"Real-time information request (entity types: {spacy_result.get('entity_labels', ['generic'])[:2] if spacy_result else ['generic']})"
            needs_internet = True
            needs_automation = False
        else:
            reasoning = "General conversational query"
            needs_internet = False
            needs_automation = False
        
        return {
            'type': final_type,
            'confidence': min(final_score, 1.0),
            'reasoning': reasoning,
            'needs_internet': needs_internet,
            'needs_automation': needs_automation,
            'keywords': automation_keywords,
            'matched_patterns': automation_patterns,
            'method': method,
            'all_votes': votes,
            'all_scores': scores,
            'entity_labels': spacy_result.get('entity_labels', []) if spacy_result else [],
            'transformer_scores': transformer_result.get('scores', {}) if transformer_result else {},
            'semantic_scores': semantic_result.get('scores', {}) if semantic_result else {}
        }
    
    def _extract_keywords_patterns(self, query: str) -> Tuple[List[str], List[str]]:
        """Extract keywords and matched patterns"""
        keywords = []
        patterns = []
        
        for category, pattern_list in self.automation_patterns.items():
            for pattern in pattern_list:
                if pattern in query:
                    keywords.append(pattern)
                    if category not in patterns:
                        patterns.append(category)
        
        for category, pattern_list in self.realtime_patterns.items():
            for pattern in pattern_list:
                if pattern in query:
                    keywords.append(pattern)
                    if category not in patterns:
                        patterns.append(category)
        
        return keywords, patterns
    
    # Original heuristic methods (kept for backward compatibility)
    def _check_automation(self, query: str) -> Tuple[float, List[str], List[str]]:
        """Check automation score"""
        score = 0
        keywords = []
        patterns = []
        
        for category, pattern_list in self.automation_patterns.items():
            for pattern in pattern_list:
                if pattern in query:
                    score += 30
                    keywords.append(pattern)
                    if category not in patterns:
                        patterns.append(category)
        
        action_verbs = ['open', 'close', 'play', 'send', 'delete', 'create', 'remind', 'take', 'generate']
        verb_count = sum(1 for verb in action_verbs if verb in query)
        if verb_count > 0:
            score += 20 * verb_count
        
        automation_phrases = ['open and', 'open the', 'send me', 'remind me', 'tell me to',
                             'take a', 'generate a', 'create a', 'download', 'turn on', 'turn off']
        phrase_matches = sum(1 for phrase in automation_phrases if phrase in query)
        if phrase_matches > 0:
            score += 25 * phrase_matches
            patterns.append('automation_phrase')
        
        if 'tell me about' in query:
            general_topics = ['python', 'java', 'c++', 'javascript', 'machine learning', 'ai',
                             'algorithm', 'data structure', 'design pattern']
            if any(topic in query for topic in general_topics):
                score -= 20
        
        return score, keywords, patterns
    
    def _check_realtime(self, query: str) -> Tuple[float, List[str], List[str]]:
        """Check realtime score"""
        score = 0
        keywords = []
        patterns = []
        
        for category, pattern_list in self.realtime_patterns.items():
            for pattern in pattern_list:
                if pattern in query:
                    score += 35
                    keywords.append(pattern)
                    if category not in patterns:
                        patterns.append(category)
        
        info_requesters = ['who is', 'what is', 'where is', 'when is', 'why is', 'how is',
                          'tell me about', 'information about', 'details about', 'facts about']
        for phrase in info_requesters:
            if phrase in query:
                score += 25
                keywords.append(phrase)
                if 'info_request' not in patterns:
                    patterns.append('info_request')
        
        time_sensitive = ['today', 'now', 'current', 'latest', 'recent', 'just', 'this moment', 'right now']
        ts_matches = sum(1 for ts in time_sensitive if ts in query)
        if ts_matches > 0:
            score += 20 * ts_matches
        
        if 'weather' in query:
            score += 15
        
        if 'tell me about' in query:
            general_knowledge = ['python', 'java', 'einstein', 'newton', 'algorithm', 'machine learning']
            if any(topic in query for topic in general_knowledge):
                score -= 15
        
        return score, keywords, patterns
    
    def _check_general(self, query: str) -> Tuple[float, List[str]]:
        """Check general score"""
        score = 30
        keywords = []
        
        for indicator in self.general_indicators:
            if indicator in query:
                score += 15
                keywords.append(indicator)
        
        conversational = ['hi', 'hello', 'hey', 'how are you', 'what about', 'i wonder',
                         'let\'s talk', 'discuss', 'what do you think', 'your opinion']
        conv_matches = sum(1 for conv in conversational if conv in query)
        if conv_matches > 0:
            score += 20 * conv_matches
        
        knowledge = ['teach me', 'explain', 'meaning', 'definition', 'example', 'understand',
                    'learn', 'help me', 'advice', 'suggest', 'recommend']
        know_matches = sum(1 for know in knowledge if know in query)
        if know_matches > 0:
            score += 15 * know_matches
            keywords.extend([k for k in knowledge if k in query])
        
        if 'tell me about' in query:
            general_topics = ['python', 'java', 'c++', 'javascript', 'algorithm', 
                             'data structure', 'machine learning', 'design pattern']
            if any(topic in query for topic in general_topics):
                score += 30
        
        return score, keywords
