"""
Task scheduler and reminder system for JARVIS.
Remembers tasks, reminders, and scheduled actions even after restart.
"""
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from jarvis.utils.logger import setup_logger
from jarvis.config import DATA_DIR

logger = setup_logger(__name__)

TASKS_FILE = DATA_DIR / "tasks.json"


class TaskScheduler:
    """Manages scheduled tasks, reminders, and long-term memory."""
    
    def __init__(self, tasks_file: Path = TASKS_FILE):
        """Initialize task scheduler.
        
        Args:
            tasks_file: Path to tasks.json file
        """
        self.tasks_file = tasks_file
        self.tasks: List[Dict] = []
        self.load_tasks()
    
    def load_tasks(self) -> None:
        """Load tasks from tasks.json."""
        try:
            if self.tasks_file.exists():
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = data.get('tasks', [])
                    logger.debug(f"Loaded {len(self.tasks)} tasks from memory")
            else:
                self.tasks = []
        except Exception as e:
            logger.error(f"Failed to load tasks: {e}")
            self.tasks = []
    
    def save_tasks(self) -> None:
        """Save tasks to tasks.json."""
        try:
            self.tasks_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Read existing data
            existing_data = {}
            if self.tasks_file.exists():
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            
            # Update tasks
            existing_data['tasks'] = self.tasks
            existing_data['last_updated'] = datetime.now().isoformat()
            
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save tasks: {e}")
    
    def add_task(self, task_type: str, content: str, scheduled_time: Optional[str] = None, 
                 recurring: str = "once") -> Dict:
        """Add a new task or reminder.
        
        Args:
            task_type: Type of task (reminder, notification, todo, action, etc.)
            content: Task description
            scheduled_time: When to execute (ISO format or human readable like "6 pm")
            recurring: 'once', 'daily', 'weekly', 'monthly'
        
        Returns:
            The created task
        """
        task = {
            "id": len(self.tasks) + 1,
            "type": task_type,
            "content": content,
            "scheduled_time": scheduled_time,
            "recurring": recurring,
            "created_at": datetime.now().isoformat(),
            "completed": False,
            "last_triggered": None,
            "active": True
        }
        
        self.tasks.append(task)
        self.save_tasks()
        logger.info(f"Added task: {task_type} - {content}")
        return task
    
    def parse_time_string(self, time_str: str) -> Optional[datetime]:
        """Parse human-readable time strings to datetime.
        
        Args:
            time_str: Time string like "6 pm", "3:30 pm", "tomorrow at 5 pm"
        
        Returns:
            datetime object or None
        """
        time_str = time_str.lower().strip()
        now = datetime.now()
        
        try:
            # Handle "6 pm" or "6 AM" format
            if "pm" in time_str or "am" in time_str:
                time_part = time_str.replace("pm", "").replace("am", "").strip()
                is_pm = "pm" in time_str
                
                # Parse time
                if ":" in time_part:
                    hour, minute = map(int, time_part.split(":"))
                else:
                    hour = int(time_part)
                    minute = 0
                
                if is_pm and hour != 12:
                    hour += 12
                elif not is_pm and hour == 12:
                    hour = 0
                
                # Create datetime for today
                scheduled = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # If time is in past, schedule for tomorrow
                if scheduled < now:
                    scheduled = scheduled + timedelta(days=1)
                
                return scheduled
            
            # Handle "tomorrow at X" format
            elif "tomorrow" in time_str:
                time_part = time_str.replace("tomorrow", "").replace("at", "").strip()
                scheduled = self.parse_time_string(time_part)
                if scheduled:
                    return scheduled + timedelta(days=1)
            
            # Handle ISO format
            elif "T" in time_str:
                return datetime.fromisoformat(time_str)
        
        except Exception as e:
            logger.debug(f"Could not parse time string '{time_str}': {e}")
        
        return None
    
    def get_due_tasks(self) -> List[Dict]:
        """Get all tasks that are due now.
        
        Returns:
            List of tasks ready to execute
        """
        due_tasks = []
        now = datetime.now()
        
        for task in self.tasks:
            if not task.get('active', True):
                continue
            
            if task.get('completed') and task.get('recurring') == 'once':
                continue
            
            scheduled_str = task.get('scheduled_time')
            if not scheduled_str:
                continue
            
            # Parse scheduled time
            scheduled = self.parse_time_string(scheduled_str)
            if not scheduled:
                try:
                    scheduled = datetime.fromisoformat(scheduled_str)
                except:
                    continue
            
            # Check if due (within 1 minute window for notifications)
            time_diff = (scheduled - now).total_seconds()
            
            if -60 <= time_diff <= 60:  # Due within +/- 1 minute
                due_tasks.append(task)
        
        return due_tasks
    
    def mark_completed(self, task_id: int) -> bool:
        """Mark a task as completed.
        
        Args:
            task_id: ID of task to complete
        
        Returns:
            True if successful
        """
        for task in self.tasks:
            if task['id'] == task_id:
                task['completed'] = True
                task['last_triggered'] = datetime.now().isoformat()
                self.save_tasks()
                logger.info(f"Task {task_id} marked as completed")
                return True
        return False
    
    def get_active_reminders(self) -> List[Dict]:
        """Get all active reminders/notifications.
        
        Returns:
            List of active tasks
        """
        return [t for t in self.tasks if t.get('active', True) and not (t.get('completed') and t.get('recurring') == 'once')]
    
    def deactivate_task(self, task_id: int) -> bool:
        """Deactivate a task (don't delete, just disable).
        
        Args:
            task_id: ID of task to deactivate
        
        Returns:
            True if successful
        """
        for task in self.tasks:
            if task['id'] == task_id:
                task['active'] = False
                self.save_tasks()
                logger.info(f"Task {task_id} deactivated")
                return True
        return False
    
    def get_tasks_by_type(self, task_type: str) -> List[Dict]:
        """Get all tasks of a specific type.
        
        Args:
            task_type: Type of task (reminder, notification, todo, etc.)
        
        Returns:
            List of matching tasks
        """
        return [t for t in self.tasks if t.get('type') == task_type and t.get('active', True)]
    
    def get_summary(self) -> str:
        """Get a summary of all active tasks."""
        active = self.get_active_reminders()
        if not active:
            return "No active reminders or tasks."
        
        summary = f"You have {len(active)} active reminder(s):\n"
        for task in active[:5]:  # Show first 5
            time_str = task.get('scheduled_time', 'unscheduled')
            summary += f"  - {task['type']}: {task['content']} at {time_str}\n"
        
        if len(active) > 5:
            summary += f"  ... and {len(active) - 5} more"
        
        return summary
    
    def extract_task_info(self, query: str) -> Optional[Dict]:
        """Extract task information from natural language query.
        
        Args:
            query: User query like "remind me to call mom at 5 pm"
        
        Returns:
            Dict with extracted task info or None
        """
        query_lower = query.lower()
        
        # Detect task type and time
        task_type = None
        time_str = None
        content = query
        
        # Detect task type
        if any(kw in query_lower for kw in ["remind", "remember", "notification", "notify"]):
            task_type = "reminder"
        elif any(kw in query_lower for kw in ["todo", "task", "do", "need to"]):
            task_type = "todo"
        elif any(kw in query_lower for kw in ["alarm", "alert"]):
            task_type = "alert"
        elif any(kw in query_lower for kw in ["message", "tell", "inform"]):
            task_type = "notification"
        
        if not task_type:
            return None
        
        # Extract time (simple extraction)
        time_keywords = [
            ("6 pm", "6 pm"), ("6pm", "6 pm"),
            ("5 pm", "5 pm"), ("5pm", "5 pm"),
            ("at night", "9 pm"),
            ("in the morning", "8 am"),
            ("at noon", "12 pm"),
            ("tomorrow", "tomorrow"),
            ("today", "today at"), 
        ]
        
        for keyword, replacement in time_keywords:
            if keyword in query_lower:
                time_str = replacement
                # Clean content
                content = query.replace(keyword, "").strip()
                break
        
        # Extract time from "at X" pattern
        if not time_str:
            import re
            match = re.search(r'at\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)', query_lower)
            if match:
                time_str = match.group(1)
                content = query[:match.start()].strip()
        
        return {
            "type": task_type,
            "content": content,
            "time": time_str
        }
    
    def list_tasks_human_readable(self) -> str:
        """Get human-readable list of all tasks."""
        active = self.get_active_reminders()
        if not active:
            return "No active reminders or tasks currently."
        
        output = "Your scheduled reminders and tasks:\n\n"
        for i, task in enumerate(active, 1):
            task_type = task.get('type', 'task').upper()
            content = task.get('content', 'No description')
            time_str = task.get('scheduled_time', 'Unscheduled')
            recurring = task.get('recurring', 'once')
            
            output += f"{i}. [{task_type}] {content}\n"
            output += f"   Time: {time_str} ({recurring})\n"
            output += f"   ID: {task['id']}\n\n"
        
        return output
