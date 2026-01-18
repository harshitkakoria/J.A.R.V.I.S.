"""
Example implementation: How to use the Query Classifier in your brain.py
Add this to your brain or response module to activate smart routing.
"""

from jarvis.utils.query_classifier import QueryClassifier, QueryRouter
from jarvis.utils.logger import setup_logger

logger = setup_logger(__name__)


def classify_and_respond(query: str, brain_instance) -> str:
    """
    Main entry point: Classify query and route to appropriate handler.
    
    Call this instead of directly calling brain handlers.
    
    Args:
        query: User's query
        brain_instance: The main Brain instance
        
    Returns:
        Response string
    """
    # Initialize router with brain context
    router = QueryRouter(brain=brain_instance)
    
    # Get routing information
    routing_info = router.route(query)
    query_type = routing_info['type']
    classification = routing_info['classification']
    handler = routing_info['handler']
    
    # Log classification
    logger.info(f"Query Type: {query_type}")
    logger.info(f"Confidence: {classification.get('confidence', 0):.2%}")
    logger.info(f"Reasoning: {classification.get('reasoning', 'N/A')}")
    
    # Print for debugging (optional)
    print(f"\n📊 Classification: {query_type.upper()}")
    print(f"   Confidence: {classification.get('confidence', 0):.1%}")
    print(f"   Needs Internet: {classification.get('needs_internet', False)}")
    print(f"   Needs Automation: {classification.get('needs_automation', False)}\n")
    
    # Call the appropriate handler
    try:
        response = handler(query)
        return response
    except Exception as e:
        logger.error(f"Handler error: {e}")
        return f"I encountered an error processing your {query_type} query"


def get_query_type(query: str) -> str:
    """
    Quick utility: Get just the query type without handling.
    
    Returns:
        'general', 'realtime', or 'automation'
    """
    classifier = QueryClassifier()
    classification = classifier.classify(query)
    return classification.get('type', 'general')


# ============ INTEGRATION EXAMPLES ============

# OPTION 1: Replace direct brain calls
# Instead of:
#   response = brain.respond_to_query(query)
# Use:
#   response = classify_and_respond(query, brain_instance)


# OPTION 2: Update in response.py
# Add this to the get_response() function in jarvis/core/response.py
#
# from jarvis.utils.query_classifier import classify_and_respond
#
# def get_response(query: str, brain) -> str:
#     """Main response handler with smart routing."""
#     return classify_and_respond(query, brain)


# OPTION 3: Conditional handling with different response styles
def get_response_with_style(query: str, brain_instance) -> str:
    """Get response with different output based on query type."""
    classifier = QueryClassifier()
    classification = classifier.classify(query)
    query_type = classification.get('type', 'general')
    
    router = QueryRouter(brain=brain_instance)
    handler = router._get_handler(query_type)
    response = handler(query)
    
    # Format response based on type
    if query_type == 'automation':
        return f"🤖 {response}"  # Add automation emoji
    elif query_type == 'realtime':
        return f"🌐 {response}"  # Add internet emoji
    else:
        return response  # No special formatting for general
