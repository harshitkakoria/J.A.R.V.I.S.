from jarvis.core.research.planner import ResearchPlanner
from jarvis.core.research.fetcher import ResearchFetcher
from jarvis.core.research.evaluator import SourceEvaluator
from jarvis.core.research.summarizer import ResearchSummarizer

class ResearchAgent:
    """Orchestrates safe, read-only web research."""
    
    def __init__(self):
        self.planner = ResearchPlanner()
        self.fetcher = ResearchFetcher()
        self.evaluator = SourceEvaluator()
        self.summarizer = ResearchSummarizer()
        
    def research(self, topic: str) -> str:
        """Execute full research pipeline and return formatted string."""
        
        # 1. Plan
        plan = self.planner.plan(topic)
        
        # 2. Fetch (Simulation for now as per fetcher.py)
        # Using subquestions
        try:
             sources = self.fetcher.fetch_simulated(plan.subquestions)
        except:
             sources = []
             
        # 3. Evaluate
        valid_sources = self.evaluator.evaluate(sources)
        
        if not valid_sources:
            return "I couldn't find any credible sources for that topic."
            
        # 4. Summarize
        result = self.summarizer.summarize(plan.topic, valid_sources)
        
        # 5. Format Output
        output = [f"**Research: {plan.topic}**\n"]
        
        output.append("**Summary**")
        for point in result.summary:
            output.append(f"• {point}")
            
        if result.disagreements:
            output.append("\n**Caveats / Disagreements**")
            for cave in result.disagreements:
                output.append(f"• {cave}")
                
        output.append("\n**Sources**")
        for s in result.sources:
            output.append(f"• {s.domain} ({s.published or 'n.d.'}): {s.title}")
            
        return "\n".join(output)
