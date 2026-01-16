"""
File management skill: Create, delete, rename, move files and folders.
"""
import os
import shutil
from pathlib import Path
from typing import Optional
from jarvis.utils.logger import setup_logger

logger = setup_logger(__name__)


def handle(query: str) -> Optional[str]:
    """
    Handle file management commands.
    
    Args:
        query: User command
        
    Returns:
        Result message or None
    """
    query_lower = query.lower()
    
    # Create file/folder
    if any(kw in query_lower for kw in ["create file", "new file", "make file", "create folder", "new folder", "make folder"]):
        return create_item(query)
    
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


def create_item(query: str) -> str:
    """Create a file or folder."""
    try:
        query_lower = query.lower()
        
        # Extract name from query (simplified - assumes format like "create file test.txt")
        words = query.split()
        
        # Find the name after "file" or "folder"
        name = None
        for i, word in enumerate(words):
            if word.lower() in ["file", "folder"] and i + 1 < len(words):
                name = words[i + 1]
                break
        
        if not name:
            return "Please specify a name. Example: 'create file myfile.txt' or 'create folder myfolder'"
        
        # Determine if file or folder
        is_folder = "folder" in query_lower
        
        # Create in current directory
        path = Path(name)
        
        if is_folder:
            if path.exists():
                return f"Folder '{name}' already exists."
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created folder: {path.absolute()}")
            return f"Folder '{name}' created successfully."
        else:
            if path.exists():
                return f"File '{name}' already exists."
            path.touch()
            logger.info(f"Created file: {path.absolute()}")
            return f"File '{name}' created successfully."
            
    except Exception as e:
        logger.error(f"Create error: {e}")
        return f"Failed to create: {str(e)}"


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
