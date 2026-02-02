import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from jarvis.core.models import ExecutionResult
from jarvis.utils.file_indexer import FileIndexer
from jarvis.utils.memory import Memory

class FileManager:
    """
    Intelligent File Manager.
    - Uses local index (FileIndexer).
    - Parses natural language constraints (provided by Brain).
    - Enforces safety (Search -> Confirm -> Open).
    """
    
    def __init__(self, memory: Memory):
        self.indexer = FileIndexer()
        self.memory = memory
        # Initialize index on startup
        self.indexer.refresh()

    def handle(self, intent: Dict) -> ExecutionResult:
        """
        Handle 'file_search' intent from Brain.
        Intent structure:
        {
            "category": "file_search",
            "args": {
                "type": "pdf", # or 'doc', 'image'
                "time_range": "yesterday", # or specific date string? Brain converts? 
                                          # Ideally Brain gives 'yesterday' and we parse relative time here 
                                          # because Brain doesn't know 'today' accurately without context injection overload.
                "action": "downloaded", # implies location
                "name_contains": "invoice" # optional
            }
        }
        """
        args = intent.get("args", {})
        
        # 1. Parse Constraints
        constraints = self._parse_constraints(args)
        
        # 2. Search
        print(f"[FileManager] Searching with constraints: {constraints}")
        results = self.indexer.search(constraints)
        
        # 3. Handle Results
        if not results:
            return ExecutionResult(False, "I couldn't find any matching files.")
            
        if len(results) == 1:
            file = results[0]
            self.memory.set_context("file_candidates", [file])
            return ExecutionResult(
                True, 
                f"I found one file: '{file['name']}'. Should I open it?",
                data={"count": 1, "candidates": results}
            )
            
        # Multiple results
        self.memory.set_context("file_candidates", results)
        
        # Format list for display/TTS
        choices = []
        for i, r in enumerate(results[:5]): # Limit to 5
            choices.append(f"{i+1}. {r['name']} ({r['location']})")
        
        choices_str = "\n".join(choices)
        return ExecutionResult(
            True,
            f"I found multiple files:\n{choices_str}\nWhich one should I open?",
            data={"count": len(results), "candidates": results}
        )

    def open_confirmed(self, selection: int) -> ExecutionResult:
        """
        Execute open action after user confirms.
        selection: 1-based index (e.g. "first one" -> 1)
        """
        candidates = self.memory.get_context("file_candidates")
        if not candidates:
            return ExecutionResult(False, "No file selected.", error="NO_CONTEXT")
            
        idx = selection - 1
        if idx < 0 or idx >= len(candidates):
            return ExecutionResult(False, "Invalid selection.")
            
        target = candidates[idx]
        try:
            print(f"[FileManager] Opening: {target['path']}")
            os.startfile(target["path"])
            return ExecutionResult(True, f"Opening {target['name']}")
        except Exception as e:
            return ExecutionResult(False, f"Failed to open file: {e}")

    def _parse_constraints(self, args: Dict) -> Dict:
        """Convert natural language args to indexer constraints."""
        c = {}
        
        # Type
        if "type" in args:
            c["type"] = args["type"] # ".pdf", "pdf", etc handled by indexer
            
        # Time Parser
        # "yesterday", "today", "last week"
        tr = args.get("time_range")
        if tr:
            now = datetime.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            
            if tr == "today":
                c["time_range"] = {"start": today_start, "end": now}
            elif tr == "yesterday":
                start = today_start - timedelta(days=1)
                end = today_start - timedelta(seconds=1)
                c["time_range"] = {"start": start, "end": end}
            elif tr == "last week":
                start = today_start - timedelta(days=7)
                c["time_range"] = {"start": start, "end": now}
        
        # Location ("downloaded" -> Downloads)
        action = args.get("action", "")
        if "downloaded" in action:
            c["locations"] = ["Downloads"]
        elif "desktop" in action:
             c["locations"] = ["Desktop"]
             
        # Name
        if "name_contains" in args:
            c["name_contains"] = args["name_contains"]
            
        return c
