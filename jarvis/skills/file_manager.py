"""
File management skill: Create, delete, rename, move files and folders.
Supports creating Word documents, PDFs, and PowerPoint presentations with AI-generated content.
"""
import os
import shutil
import subprocess
import requests
from pathlib import Path
from typing import Optional
from io import BytesIO
from jarvis.utils.logger import setup_logger

logger = setup_logger(__name__)

# Get Downloads folder path
def get_downloads_folder() -> Path:
    """Get the user's Downloads folder path."""
    if os.name == 'nt':  # Windows
        downloads = Path.home() / 'Downloads'
    else:  # Linux/Mac
        downloads = Path.home() / 'Downloads'
    
    # Create if doesn't exist
    downloads.mkdir(exist_ok=True)
    return downloads

# Check if python-docx is available for Word document creation
try:
    from docx import Document
    from docx.shared import Inches, Pt
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logger.debug("python-docx not available, Word document creation disabled")

# Check if python-pptx is available for PowerPoint creation
try:
    from pptx import Presentation
    from pptx.util import Inches as PptInches, Pt as PptPt
    PPTX_AVAILABLE = True
except ImportError:
    PPTX_AVAILABLE = False
    logger.debug("python-pptx not available, PowerPoint creation disabled")

# Check if reportlab is available for PDF creation
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logger.debug("reportlab not available, PDF creation disabled")


def handle(query: str) -> Optional[str]:
    """
    Handle file management commands.
    
    Args:
        query: User command
        
    Returns:
        Result message or None
    """
    query_lower = query.lower()
    
    # Create file/folder/document/PDF/PPT
    # Check for creation keywords combined with document types
    create_keywords = ["create", "make", "new", "generate"]
    doc_types = ["file", "folder", "document", "word", "pdf", "presentation", "ppt"]
    
    has_create_keyword = any(kw in query_lower for kw in create_keywords)
    has_doc_type = any(dt in query_lower for dt in doc_types)
    
    if has_create_keyword and has_doc_type:
        return create_item(query)
    
    # Open file/document/presentation
    if any(kw in query_lower for kw in ["open file", "open document", "open pdf", "open presentation", "open ppt", "view file", "review presentation", "review ppt", "view presentation"]):
        # Try to find the most recently created document
        downloads = get_downloads_folder()
        if downloads.exists():
            files = sorted(downloads.glob('*'), key=lambda x: x.stat().st_mtime, reverse=True)
            if files:
                return open_document(files[0])
        return "No documents found in Downloads folder."
    
    # Delete file/folder
    if any(kw in query_lower for kw in ["delete file", "remove file", "delete folder", "remove folder"]):
        return delete_item(query)
    
    # Rename file/folder
    if any(kw in query_lower for kw in ["rename file", "rename folder", "change name"]):
        return rename_item(query)
    
    # List files
    if any(kw in query_lower for kw in ["list files", "show files", "what files"]):
        return list_files(query)
    
    return None


def extract_filename_and_topic(query: str) -> tuple:
    """Extract filename and topic from query. If no filename, generate from topic."""
    words = query.split()
    filename = None
    topic = None
    
    # Find topic after keywords
    for keyword in ['about', 'on', 'with', 'regarding', 'for']:
        if keyword in query.lower():
            parts = query.lower().split(keyword, 1)
            if len(parts) > 1:
                topic = parts[1].strip()
                break
    
    # Find explicit filename (if it has . or is right after document/file keywords)
    for i, word in enumerate(words):
        if word.lower() in ["file", "folder", "document", "doc", "pdf", "presentation", "ppt"] and i + 1 < len(words):
            next_word = words[i + 1]
            if '.' in next_word:  # Has extension
                filename = next_word
                break
    
    # If no filename provided, generate from topic
    if not filename and topic:
        # Clean topic and create filename
        topic_clean = topic.strip().split('\n')[0]  # Get first line
        topic_clean = topic_clean.replace(' ', '_').replace('-', '_')[:30]  # Max 30 chars
        filename = topic_clean
    
    return filename, topic


def extract_page_count(query: str) -> Optional[int]:
    """Extract page count from query if mentioned. Returns None if not specified."""
    words = query.lower().split()
    for i, word in enumerate(words):
        if word in ['page', 'pages'] and i > 0:
            try:
                return int(words[i - 1])
            except ValueError:
                pass
    return None


def create_placeholder_image() -> Optional[bytes]:
    """Create a simple placeholder image for documents."""
    try:
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (400, 300), color=(70, 130, 180))
        draw = ImageDraw.Draw(img)
        draw.text((140, 140), "Document Image", fill=(255, 255, 255))
        
        # Save to bytes
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        return img_bytes.getvalue()
    except Exception as e:
        logger.debug(f"Could not create placeholder image: {e}")
        return None


def create_item(query: str) -> str:
    """Create a file, folder, or document (Word/PDF/PPT)."""
    try:
        query_lower = query.lower()
        
        # Determine document type
        is_folder = "folder" in query_lower
        is_word_doc = any(kw in query_lower for kw in ['document', 'word', '.docx', '.doc'])
        is_pdf = any(kw in query_lower for kw in ['pdf', '.pdf'])
        is_ppt = any(kw in query_lower for kw in ['presentation', 'ppt', 'powerpoint', '.pptx'])
        
        # Extract filename, topic, and page count
        filename, topic = extract_filename_and_topic(query)
        page_count = extract_page_count(query)
        
        # If only topic provided (no explicit filename), use topic as base
        if not filename and topic:
            topic_base = topic.strip().split('\n')[0]
            filename = topic_base.replace(' ', '_').replace('-', '_')[:30]
        
        if not filename:
            return "Please specify what you want to create. Example: 'create document about AI trends' or 'create pdf on machine learning' or 'create presentation regarding project planning'"
        
        # Add appropriate extension if not already present
        if is_word_doc and '.' not in filename:
            filename += '.docx'
        elif is_pdf and '.' not in filename:
            filename += '.pdf'
        elif is_ppt and '.' not in filename:
            filename += '.pptx'
        
        # Save to Downloads folder for documents, current directory for simple files
        if is_word_doc or is_pdf or is_ppt:
            downloads_folder = get_downloads_folder()
            path = downloads_folder / filename
        else:
            path = Path(filename)
        
        # Create folder
        if is_folder:
            if path.exists():
                return f"Folder '{filename}' already exists."
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created folder: {path.absolute()}")
            return f"Folder '{filename}' created successfully."
        
        # Create Word document
        elif is_word_doc or filename.endswith('.docx'):
            return create_word_document(path, topic)
        
        # Create PDF
        elif is_pdf or filename.endswith('.pdf'):
            return create_pdf_document(path, topic)
        
        # Create PowerPoint
        elif is_ppt or filename.endswith('.pptx'):
            return create_ppt_document(path, topic, page_count)
        
        # Create basic text file
        else:
            if path.exists():
                return f"File '{filename}' already exists."
            path.touch()
            logger.info(f"Created file: {path.absolute()}")
            return f"File '{filename}' created successfully."
            
    except Exception as e:
        logger.error(f"Create error: {e}")
        return f"Failed to create: {str(e)}"



def generate_content(topic: str) -> str:
    """Generate content for a topic using LLM."""
    if not topic:
        return "This document was created by JARVIS."
    
    try:
        # Use Groq LLM to generate content
        from jarvis.config import GROQ_API_KEY, USE_GROQ
        
        if not USE_GROQ or not GROQ_API_KEY:
            return f"Content about: {topic}\n\nThis document was created by JARVIS. AI content generation requires Groq API."
        
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a professional content writer. Generate well-structured, informative content."},
                {"role": "user", "content": f"Write detailed, professional content about: {topic}. Include an introduction, main points, and conclusion. Make it informative and well-organized."}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        content = response.choices[0].message.content
        logger.info(f"Generated content for topic: {topic}")
        return content
        
    except Exception as e:
        logger.error(f"Content generation error: {e}")
        return f"Content about: {topic}\n\nThis document was created by JARVIS."


def create_word_document(path: Path, topic: str) -> str:
    """Create a Word document with AI-generated content and images."""
    if not DOCX_AVAILABLE:
        return "Word document creation requires python-docx package. Install with: pip install python-docx"
    
    try:
        if path.exists():
            return f"Document '{path.name}' already exists."
        
        # Create new document
        doc = Document()
        
        # Add title
        doc.add_heading(path.stem.replace('-', ' ').replace('_', ' ').title(), 0)
        
        # Try to add a placeholder image at the top
        try:
            image_data = create_placeholder_image()
            if image_data:
                img_stream = BytesIO(image_data)
                doc.add_picture(img_stream, width=Inches(5))
                doc.add_paragraph()  # Add spacing after image
        except Exception as e:
            logger.debug(f"Could not add image: {e}")
        
        # Generate and add content
        if topic:
            content = generate_content(topic)
            # Split content into paragraphs
            paragraphs = content.split('\n\n')
            for i, para in enumerate(paragraphs):
                if para.strip():
                    # Check if it's a heading (starts with #)
                    if para.strip().startswith('#'):
                        heading_text = para.strip().lstrip('#').strip()
                        doc.add_heading(heading_text, level=1)
                    else:
                        doc.add_paragraph(para.strip())
                    
                    # Add image every 3 paragraphs for visual appeal
                    if (i + 1) % 3 == 0 and i > 0:
                        try:
                            image_data = create_placeholder_image()
                            if image_data:
                                img_stream = BytesIO(image_data)
                                doc.add_picture(img_stream, width=Inches(5))
                                doc.add_paragraph()  # Add spacing
                        except Exception as e:
                            logger.debug(f"Could not add section image: {e}")
        else:
            doc.add_paragraph('This document was created by JARVIS.')
        
        # Save document
        doc.save(str(path))
        logger.info(f"Created Word document: {path.absolute()}")
        
        return f"Word document '{path.name}' created successfully in Downloads folder."
        
    except Exception as e:
        logger.error(f"Word document creation error: {e}")
        return f"Failed to create Word document: {str(e)}"


def create_pdf_document(path: Path, topic: str) -> str:
    """Create a PDF document with AI-generated content."""
    if not PDF_AVAILABLE:
        return "PDF creation requires reportlab package. Install with: pip install reportlab"
    
    try:
        if path.exists():
            return f"PDF '{path.name}' already exists."
        
        # Create PDF
        doc = SimpleDocTemplate(str(path), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Add title
        title = path.stem.replace('-', ' ').replace('_', ' ').title()
        title_para = Paragraph(f"<b><font size=18>{title}</font></b>", styles['Title'])
        story.append(title_para)
        story.append(Spacer(1, 0.3 * inch))
        
        # Generate and add content
        if topic:
            content = generate_content(topic)
            # Split and add paragraphs
            paragraphs = content.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    para_text = para.strip().replace('<', '&lt;').replace('>', '&gt;')
                    p = Paragraph(para_text, styles['BodyText'])
                    story.append(p)
                    story.append(Spacer(1, 0.2 * inch))
        else:
            p = Paragraph("This document was created by JARVIS.", styles['BodyText'])
            story.append(p)
        
        # Build PDF
        doc.build(story)
        logger.info(f"Created PDF: {path.absolute()}")
        
        return f"PDF '{path.name}' created successfully in Downloads folder."
        
    except Exception as e:
        logger.error(f"PDF creation error: {e}")
        return f"Failed to create PDF: {str(e)}"


def create_ppt_document(path: Path, topic: str, page_count: Optional[int] = None) -> str:
    """Create a PowerPoint presentation with AI-generated content."""
    if not PPTX_AVAILABLE:
        return "PowerPoint creation requires python-pptx package. Install with: pip install python-pptx"
    
    try:
        if path.exists():
            return f"Presentation '{path.name}' already exists."
        
        # If page count not specified, use default
        if page_count is None:
            page_count = 5  # Default
        
        # Create presentation
        prs = Presentation()
        prs.slide_width = PptInches(10)
        prs.slide_height = PptInches(7.5)
        
        # Title slide
        title_slide_layout = prs.slide_layouts[0]
        slide = prs.slides.add_slide(title_slide_layout)
        title = slide.shapes.title
        subtitle = slide.placeholders[1]
        
        title.text = path.stem.replace('-', ' ').replace('_', ' ').title()
        subtitle.text = "Created by JARVIS"
        
        # Generate content and create slides
        if topic:
            content = generate_content(topic)
            
            # Split content into sections
            sections = content.split('\n\n')
            
            # Limit slides based on page_count
            max_slides = min(page_count, len(sections))
            
            for section in sections[:max_slides]:
                if section.strip():
                    # Content slide
                    bullet_slide_layout = prs.slide_layouts[1]
                    slide = prs.slides.add_slide(bullet_slide_layout)
                    
                    # Use first line as title
                    lines = section.strip().split('\n')
                    slide_title = lines[0][:50] if lines else "Content"
                    slide.shapes.title.text = slide_title
                    
                    # Add content
                    if len(lines) > 1:
                        body = slide.placeholders[1]
                        tf = body.text_frame
                        for line in lines[1:]:
                            if line.strip():
                                p = tf.add_paragraph()
                                p.text = line.strip()[:200]  # Limit line length
                                p.level = 0
        else:
            # Simple content slide
            bullet_slide_layout = prs.slide_layouts[1]
            slide = prs.slides.add_slide(bullet_slide_layout)
            slide.shapes.title.text = "Content"
            body = slide.placeholders[1]
            body.text = "This presentation was created by JARVIS."
        
        # Save presentation
        prs.save(str(path))
        logger.info(f"Created PowerPoint with {len(prs.slides)} slides: {path.absolute()}")
        
        return f"PowerPoint presentation '{path.name}' created with {len(prs.slides)} slides in Downloads folder. Ready for review! Say 'open presentation' or 'review' to view it."
        
    except Exception as e:
        logger.error(f"PowerPoint creation error: {e}")
        return f"Failed to create PowerPoint: {str(e)}"


def open_document(file_path: Path) -> str:
    """Open a document using the default application."""
    try:
        if not file_path.exists():
            return f"File '{file_path.name}' not found."
        
        if os.name == 'nt':  # Windows
            os.startfile(str(file_path))
        elif os.name == 'posix':  # Linux/Mac
            subprocess.Popen(['open', str(file_path)])
        
        logger.info(f"Opened document: {file_path.absolute()}")
        return f"Opening '{file_path.name}' in default application."
        
    except Exception as e:
        logger.error(f"Failed to open document: {e}")
        return f"Could not open document: {str(e)}"


def delete_item(query: str) -> str:
    """Delete a file or folder. REQUIRES CONFIRMATION."""
    try:
        query_lower = query.lower()
        
        # SAFETY: Check for confirmation word
        if "confirm" not in query_lower and "yes" not in query_lower:
            return "Delete is a destructive operation. Please add 'confirm' to your command. Example: 'delete file test.txt confirm'"
        
        # Extract name
        words = query.split()
        name = None
        for i, word in enumerate(words):
            if word.lower() in ["file", "folder"] and i + 1 < len(words):
                next_word = words[i + 1]
                if next_word.lower() not in ["confirm", "yes"]:
                    name = next_word
                    break
        
        if not name:
            return "Please specify a name. Example: 'delete file myfile.txt confirm'"
        
        path = Path(name)
        
        if not path.exists():
            return f"'{name}' does not exist."
        
        # SAFETY: Don't delete system/important files
        dangerous_patterns = [".exe", ".dll", ".sys", "system32", "windows", "program files"]
        if any(pattern in str(path).lower() for pattern in dangerous_patterns):
            logger.warning(f"Blocked dangerous delete attempt: {path}")
            return f"Cannot delete system files for safety."
        
        if path.is_dir():
            shutil.rmtree(path)
            logger.warning(f"DELETED FOLDER: {path.absolute()}")
            return f"Folder '{name}' deleted successfully."
        else:
            path.unlink()
            logger.warning(f"DELETED FILE: {path.absolute()}")
            return f"File '{name}' deleted successfully."
            
    except Exception as e:
        logger.error(f"Delete error: {e}")
        return f"Failed to delete: {str(e)}"


def rename_item(query: str) -> str:
    """Rename a file or folder."""
    try:
        # Simplified: assumes format "rename file old.txt to new.txt"
        words = query.split()
        
        if "to" not in query.lower():
            return "Please use format: 'rename file oldname.txt to newname.txt'"
        
        to_index = [i for i, w in enumerate(words) if w.lower() == "to"]
        if not to_index:
            return "Please specify 'to' in the command"
        
        to_index = to_index[0]
        
        # Get old and new names
        old_name = words[to_index - 1] if to_index > 0 else None
        new_name = words[to_index + 1] if to_index + 1 < len(words) else None
        
        if not old_name or not new_name:
            return "Please specify both old and new names"
        
        old_path = Path(old_name)
        new_path = Path(new_name)
        
        if not old_path.exists():
            return f"'{old_name}' does not exist."
        
        if new_path.exists():
            return f"'{new_name}' already exists."
        
        old_path.rename(new_path)
        logger.info(f"Renamed: {old_path} -> {new_path}")
        return f"Renamed '{old_name}' to '{new_name}' successfully."
        
    except Exception as e:
        logger.error(f"Rename error: {e}")
        return f"Failed to rename: {str(e)}"


def list_files(query: str) -> str:
    """List files in current directory."""
    try:
        # Get current directory files
        files = list(Path.cwd().iterdir())
        
        if not files:
            return "Current directory is empty."
        
        # Separate files and folders
        folders = [f.name for f in files if f.is_dir()]
        file_list = [f.name for f in files if f.is_file()]
        
        result = []
        if folders:
            result.append(f"Folders ({len(folders)}): {', '.join(folders[:5])}")
            if len(folders) > 5:
                result.append(f"...and {len(folders) - 5} more folders")
        
        if file_list:
            result.append(f"Files ({len(file_list)}): {', '.join(file_list[:5])}")
            if len(file_list) > 5:
                result.append(f"...and {len(file_list) - 5} more files")
        
        return ". ".join(result)
        
    except Exception as e:
        logger.error(f"List files error: {e}")
        return f"Failed to list files: {str(e)}"
