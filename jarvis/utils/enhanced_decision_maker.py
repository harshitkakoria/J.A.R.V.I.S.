"""
Enhanced Decision-Making Module using Cohere Classification.
Provides intelligent query routing with rich terminal output.
"""

from typing import Dict, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from jarvis.utils.cohere_classifier import CohereQueryClassifier
from jarvis.utils.logger import setup_logger

logger = setup_logger(__name__)

# Initialize Rich console for beautiful output
console = Console()


class EnhancedDecisionMaker:
    """Enhanced decision-making using Cohere AI for query classification."""
    
    def __init__(self):
        """Initialize the enhanced decision maker."""
        self.classifier = CohereQueryClassifier()
        logger.info("Enhanced Decision Maker initialized with Cohere")
    
    def analyze_query(self, query: str) -> Dict:
        """
        Analyze query using Cohere classification.
        
        Args:
            query: User's input query
            
        Returns:
            Dictionary with analysis results
        """
        analysis = self.classifier.get_classification_analysis(query)
        return analysis
    
    def make_decision(self, query: str) -> Dict:
        """
        Make routing decision for query.
        
        Args:
            query: User's input query
            
        Returns:
            Dictionary with decision details
        """
        analysis = self.analyze_query(query)
        
        decision = {
            "query": query,
            "type": analysis["type"],
            "confidence": analysis["confidence"],
            "reasoning": analysis["reasoning"],
            "route": self._get_route(analysis["type"]),
            "priority": self._get_priority(analysis["type"]),
            "recommendation": analysis["recommendation"]
        }
        
        logger.debug(f"Decision made: {decision['type']} -> {decision['route']} ({decision['confidence']:.0%})")
        return decision
    
    def _get_route(self, query_type: str) -> str:
        """Get routing destination for query type."""
        routes = {
            "general": "General LLM (Groq)",
            "realtime": "Real-Time Search Engine",
            "automation": "System Skills/Automation"
        }
        return routes.get(query_type, "General LLM")
    
    def _get_priority(self, query_type: str) -> int:
        """Get priority level for query type."""
        priorities = {
            "automation": 1,  # Highest
            "realtime": 2,
            "general": 3      # Lowest
        }
        return priorities.get(query_type, 3)
    
    def print_analysis(self, query: str, print_output: bool = False) -> None:
        """
        Print rich-formatted analysis of query.
        
        Args:
            query: Query to analyze
            print_output: Whether to print output
        """
        if not print_output:
            return
        
        decision = self.make_decision(query)
        
        # Create colored status based on confidence
        confidence_pct = decision["confidence"] * 100
        if confidence_pct >= 80:
            conf_color = "green"
            conf_emoji = "[+]"
        elif confidence_pct >= 60:
            conf_color = "yellow"
            conf_emoji = "[*]"
        else:
            conf_color = "red"
            conf_emoji = "[!]"
        
        # Create analysis panel
        analysis_text = Text()
        analysis_text.append(f"{conf_emoji} Query Type: ", style="bold")
        analysis_text.append(f"{decision['type'].upper()}", style=f"bold {conf_color}")
        analysis_text.append(f"\n    Confidence: ", style="bold")
        analysis_text.append(f"{confidence_pct:.0f}%", style=f"{conf_color}")
        analysis_text.append(f"\n    Route: ", style="bold")
        analysis_text.append(f"{decision['route']}", style="cyan")
        analysis_text.append(f"\n    Reasoning: ", style="bold")
        analysis_text.append(f"{decision['reasoning']}", style="dim white")
        
        console.print(Panel(
            analysis_text,
            title="Query Classification",
            border_style="blue",
            padding=(1, 2)
        ))
    
    def print_decision_table(self, queries: list, print_output: bool = False) -> None:
        """
        Print table of decisions for multiple queries.
        
        Args:
            queries: List of queries to analyze
            print_output: Whether to print output
        """
        if not print_output:
            return
        
        table = Table(title="Query Routing Decisions", show_header=True, header_style="bold magenta")
        table.add_column("Query", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Confidence", style="green")
        table.add_column("Route", style="yellow")
        table.add_column("Reasoning", style="white")
        
        for query in queries:
            decision = self.make_decision(query)
            conf_pct = f"{decision['confidence']*100:.0f}%"
            table.add_row(
                query[:40],
                decision["type"].upper(),
                conf_pct,
                decision["route"],
                decision["reasoning"][:40]
            )
        
        console.print(table)


# Convenience functions
def create_decision_maker() -> EnhancedDecisionMaker:
    """Create and return an enhanced decision maker instance."""
    return EnhancedDecisionMaker()


def classify_query(query: str) -> Dict:
    """Classify a single query."""
    maker = create_decision_maker()
    return maker.make_decision(query)
