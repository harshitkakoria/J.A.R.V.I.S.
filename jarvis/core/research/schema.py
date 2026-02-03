from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ResearchPlan:
    topic: str
    subquestions: List[str]
    source_requirements: dict

@dataclass
class Source:
    url: str
    domain: str
    title: str
    content: str
    published: Optional[str] = None
    credibility: float = 0.0
    reason: Optional[str] = None

@dataclass
class ResearchResult:
    summary: List[str]
    disagreements: List[str]
    citations: List[dict] # {"claim_index": 0, "sources": ["url1"]}
    sources: List[Source]
