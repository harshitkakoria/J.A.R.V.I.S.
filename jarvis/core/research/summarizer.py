import os
import groq
import json
from typing import List
from jarvis.core.research.schema import Source, ResearchResult

class ResearchSummarizer:
    """Synthesizes facts from sources."""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if self.api_key:
            self.client = groq.Groq(api_key=self.api_key)
        else:
            self.client = None

    def summarize(self, plan_topic: str, sources: List[Source]) -> ResearchResult:
        if not sources:
            return ResearchResult(["No valid sources found."], [], [], [])
            
        context_text = "\n\n".join([f"Source [{i}]: {s.title} ({s.domain})\nContent: {s.content}" for i, s in enumerate(sources)])
        
        system_prompt = """You are a Fact Summarizer.
Rules:
1. Use ONLY the provided sources.
2. DO NOT add outside knowledge.
3. DO NOT give advice.
4. Paraphrase claims from sources and cite them using [Source X].
5. Output JSON.
Format:
{
  "summary": ["Point 1 [Source 0]", "Point 2 [Source 1]"],
  "disagreements": ["Source 0 says X, but Source 1 says Y"],
  "citations": [{"claim": 0, "sources": ["domain.com"]}] 
}
"""
        try:
             # Basic offline fallback if no client
            if not self.client:
                 return ResearchResult(
                     summary=[f"Based on {sources[0].domain}, {sources[0].content[:50]}..."],
                     disagreements=[],
                     citations=[],
                     sources=sources
                 )

            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Topic: {plan_topic}\n\nSources:\n{context_text}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            data = json.loads(response.choices[0].message.content)
            
            return ResearchResult(
                summary=data.get("summary", []),
                disagreements=data.get("disagreements", []),
                citations=data.get("citations", []),
                sources=sources
            )
            
        except Exception as e:
            return ResearchResult([f"Error summarizing: {e}"], [], [], sources)
