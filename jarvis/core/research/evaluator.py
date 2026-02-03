from typing import List
from jarvis.core.research.schema import Source

class SourceEvaluator:
    """Scores source credibility."""
    
    def evaluate(self, sources: List[Source]) -> List[Source]:
        """Filter and score sources."""
        valid_sources = []
        
        for source in sources:
            score = 0.5 # Baseline
            
            # Domain Authority
            if source.domain.endswith(".gov"):
                score += 0.4
            elif source.domain.endswith(".edu"):
                score += 0.3
            elif source.domain.endswith(".org"):
                score += 0.2
            
            # Penalties
            if "blog" in source.domain or "forum" in source.domain:
                score -= 0.2
                
            source.credibility = min(1.0, max(0.0, score))
            
            if source.credibility >= 0.4:
                valid_sources.append(source)
                
        # Sort by credibility
        valid_sources.sort(key=lambda x: x.credibility, reverse=True)
        return valid_sources
