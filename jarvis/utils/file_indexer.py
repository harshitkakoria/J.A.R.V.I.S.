import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class FileIndexer:
    """
    Lightweight local file indexer.
    Scans specific user directories (Downloads, Desktop) and maintains an in-memory index.
    """
    
    def __init__(self):
        self.user_home = Path.home()
        self.scan_locations = [
            self.user_home / "Downloads",
            self.user_home / "Desktop",
            self.user_home / "Documents"
        ]
        self.index: List[Dict] = []
        self.last_refresh = None
        
    def refresh(self):
        """Rebuild the index (scan disk)."""
        print("[*] Indexing files...")
        self.index = []
        try:
            for loc in self.scan_locations:
                if not loc.exists(): continue
                
                # Walk with depth limit manually-ish or just os.walk
                for root, dirs, files in os.walk(loc):
                    # Safety: Skip heavy/system folders
                    if any(x in root.lower() for x in ["node_modules", ".git", "appdata", "library", "__pycache__", "venv"]):
                        # Don't descend into these either
                        dirs[:] = [] 
                        continue
                        
                    # 1. Index Directories
                    for d in dirs:
                        if d.startswith("."): continue
                        try:
                            dpath = Path(root) / d
                            stat = dpath.stat()
                            self.index.append({
                                "path": str(dpath),
                                "name": d,
                                "ext": "folder", # Special type for folders
                                "modified": datetime.fromtimestamp(stat.st_mtime),
                                "accessed": datetime.fromtimestamp(stat.st_atime),
                                "location": loc.name
                            })
                        except: continue

                    # 2. Index Files
                    for file in files:
                        try:
                            path = Path(root) / file
                            
                            # Filter hidden files
                            if file.startswith("."): continue
                            
                            stat = path.stat()
                            self.index.append({
                                "path": str(path),
                                "name": file,
                                "ext": path.suffix.lower(),
                                "modified": datetime.fromtimestamp(stat.st_mtime),
                                "accessed": datetime.fromtimestamp(stat.st_atime),
                                "location": loc.name # "Downloads", "Desktop"
                            })
                        except (PermissionError, OSError):
                            continue
                            
            self.last_refresh = datetime.now()
            print(f"[+] Indexing complete. Found {len(self.index)} files.")
            
        except Exception as e:
            print(f"[!] Indexing failed: {e}")

    def search(self, constraints: Dict) -> List[Dict]:
        """
        Filter index based on constraints.
        Constraints: {
            "type": ".pdf",
            "time_range": {"start": dt, "end": dt},
            "locations": ["Downloads"]
        }
        """
        if not self.index:
            self.refresh()
            
        results = []
        for f in self.index:
            # 1. Type Filter
            if "type" in constraints:
                raw_type = constraints["type"].lower().strip()
                
                if raw_type == "folder":
                    target_type = "folder"
                elif not raw_type.startswith("."):
                    target_type = f".{raw_type}"
                else:
                    target_type = raw_type
                    
                if f["ext"] != target_type:
                    continue

            # 2. Time Range
            if "time_range" in constraints:
                start = constraints["time_range"].get("start")
                end = constraints["time_range"].get("end")
                if start and f["modified"] < start: continue
                if end and f["modified"] > end: continue

            # 3. Location
            if "locations" in constraints:
                # Map shorthand to full location names?
                # The index stores "Downloads", "Desktop"
                allowed = constraints["locations"] # list of strings
                if f["location"] not in allowed:
                    continue
            
            # 4. Partial Name Match
            if "name_contains" in constraints:
                 if constraints["name_contains"].lower() not in f["name"].lower():
                     continue

            results.append(f)
            
        # Sort by Modified Time (Newest First)
        return sorted(results, key=lambda x: x["modified"], reverse=True)
