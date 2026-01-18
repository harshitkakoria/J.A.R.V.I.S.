"""File operations - create, delete files."""
import os
import subprocess
from pathlib import Path
from datetime import datetime


def handle(query: str) -> str:
    """Handle file operations."""
    q = query.lower()
    
    # Create
    if any(kw in q for kw in ["create", "make", "new"]):
        return create_file(q)
    
    # Delete
    if any(kw in q for kw in ["delete", "remove"]):
        return delete_file(q)
    
    # List
    if "list" in q:
        return list_files()
    
    return None


def create_file(query: str) -> str:
    """Create a file."""
    downloads = Path.home() / "Downloads"
    downloads.mkdir(exist_ok=True)
    
    # Extract name
    name = query.split("create")[-1].split("make")[-1].split("new")[-1].strip()
    if not name:
        name = f"file_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    # Add extension if missing
    if "." not in name:
        if "word" in query or "doc" in query:
            name += ".docx"
            return create_word(downloads / name)
        elif "pdf" in query:
            name += ".pdf"
            return create_pdf(downloads / name)
        elif "ppt" in query or "presentation" in query:
            name += ".pptx"
            return create_ppt(downloads / name)
        else:
            name += ".txt"
    
    # Create
    filepath = downloads / name
    filepath.touch()
    
    # Open
    try:
        subprocess.Popen(["notepad.exe", str(filepath)])
    except:
        pass
    
    return f"Created {name} in Downloads"


def create_word(path: Path) -> str:
    """Create Word doc."""
    try:
        from docx import Document
        doc = Document()
        doc.add_heading("Document", 0)
        doc.add_paragraph("Created by JARVIS")
        doc.save(str(path))
        subprocess.Popen(["start", str(path)], shell=True)
        return f"Created Word document: {path.name}"
    except:
        return "Install python-docx: pip install python-docx"


def create_pdf(path: Path) -> str:
    """Create PDF."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        c = canvas.Canvas(str(path), pagesize=letter)
        c.drawString(100, 750, "Document Created by JARVIS")
        c.save()
        subprocess.Popen(["start", str(path)], shell=True)
        return f"Created PDF: {path.name}"
    except:
        return "Install reportlab: pip install reportlab"


def create_ppt(path: Path) -> str:
    """Create PowerPoint."""
    try:
        from pptx import Presentation
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[0])
        slide.shapes.title.text = "Presentation"
        slide.placeholders[1].text = "Created by JARVIS"
        prs.save(str(path))
        subprocess.Popen(["start", str(path)], shell=True)
        return f"Created presentation: {path.name}"
    except:
        return "Install python-pptx: pip install python-pptx"


def delete_file(query: str) -> str:
    """Delete file."""
    if "confirm" not in query:
        return "Say 'delete file confirm' to delete"
    
    downloads = Path.home() / "Downloads"
    files = list(downloads.glob("*"))
    if files:
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        files[0].unlink()
        return f"Deleted {files[0].name}"
    
    return "No files found"


def list_files() -> str:
    """List files in Downloads."""
    downloads = Path.home() / "Downloads"
    files = [f.name for f in downloads.glob("*") if f.is_file()][:10]
    
    if files:
        return "Files: " + ", ".join(files)
    return "No files in Downloads"
