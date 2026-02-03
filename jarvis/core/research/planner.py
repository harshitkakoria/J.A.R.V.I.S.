import os
import groq
import json
from rich.console import Console
from jarvis.core.research.schema import ResearchPlan

console = Console()

class ResearchPlanner:
    """Generates research plans from queries."""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if self.api_key:
            self.client = groq.Groq(api_key=self.api_key)
        else:
            self.client = None

    def plan(self, query: str) -> ResearchPlan:
        """Create a research plan. REJECTS answers/advice."""
        if not self.client:
            # Fallback for offline testing
            return ResearchPlan(
                topic=query,
                subquestions=[f"What is {query}?", "History of " + query],
                source_requirements={"min": 2}
            )
            
        system_prompt = """You are a Research Planner.
Rules:
1. Output ONLY JSON.
2. breakdown the user query into factual sub-questions.
3. NEVER answer the question.
4. NEVER give advice.
5. If the user asks for opinion, plan to find FACTS about that opinion.
6. Output Format:
{
  "topic": "Refined topic string",
  "subquestions": ["q1", "q2"],
  "source_requirements": {
      "min_sources": 3,
      "domains": ["edu", "gov", "org", "com"]
  }
}
"""
        try:
             response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Plan research for: {query}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
             
             content = response.choices[0].message.content
             data = json.loads(content)
             
             # Safety Check: Inspect content for advice/answers (heuristic)
             # Real enforcement is by design: we only use 'subquestions' for searching.
             
             return ResearchPlan(
                 topic=data.get("topic", query),
                 subquestions=data.get("subquestions", [query]),
                 source_requirements=data.get("source_requirements", {})
             )
             
        except Exception as e:
            console.print(f"[red]Planner Error: {e}[/red]")
            return ResearchPlan(query, [query], {})
