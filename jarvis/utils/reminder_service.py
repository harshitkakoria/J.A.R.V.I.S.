"""
Reminder service that checks for due tasks on startup and during runtime.
Persistent notification system that survives restarts.
Supports both sync threading and async operations.
"""
import asyncio
import threading
import time
from datetime import datetime
from typing import Callable, Optional, List
from jarvis.utils.logger import setup_logger
from jarvis.utils.task_scheduler import TaskScheduler

logger = setup_logger(__name__)


class ReminderService:
    """Background service to trigger reminders and notifications."""
    
    def __init__(self, task_scheduler: TaskScheduler, notify_callback: Optional[Callable[[str], None]] = None):
        """Initialize reminder service.
        
        Args:
            task_scheduler: TaskScheduler instance
            notify_callback: Function to call when reminder is due (for TTS/notifications)
        """
        self.scheduler = task_scheduler
        self.notify_callback = notify_callback
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.check_interval = 30  # Check every 30 seconds
    
    def start(self) -> None:
        """Start the reminder service in background."""
        if self.running:
            logger.debug("Reminder service already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info("Reminder service started")
    
    def stop(self) -> None:
        """Stop the reminder service."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Reminder service stopped")
    
    def _run(self) -> None:
        """Main service loop - check for due tasks periodically."""
        processed_task_ids = set()
        
        while self.running:
            try:
                due_tasks = self.scheduler.get_due_tasks()
                
                for task in due_tasks:
                    task_id = task['id']
                    
                    # Avoid duplicate notifications for same task
                    if task_id not in processed_task_ids:
                        self._trigger_task(task)
                        processed_task_ids.add(task_id)
                        
                        # Mark as completed if not recurring
                        if task.get('recurring') == 'once':
                            self.scheduler.mark_completed(task_id)
                
                # Clear processed IDs periodically
                if len(processed_task_ids) > 100:
                    processed_task_ids.clear()
                
            except Exception as e:
                logger.error(f"Error in reminder service: {e}")
            
            # Check less frequently to save resources
            time.sleep(self.check_interval)
    
    def _trigger_task(self, task: dict) -> None:
        """Trigger a task notification.
        
        Args:
            task: Task dict to trigger
        """
        task_type = task.get('type', 'reminder')
        content = task.get('content', 'No description')
        
        # Create notification message
        messages = {
            'reminder': f"🔔 Reminder: {content}",
            'notification': f"📢 Notification: {content}",
            'todo': f"📋 Todo: {content}",
            'alert': f"⚠️ Alert: {content}",
        }
        
        message = messages.get(task_type, f"Task: {content}")
        
        logger.info(f"Triggered task: {message}")
        
        # Call notify callback if available (for TTS)
        if self.notify_callback:
            try:
                self.notify_callback(message)
            except Exception as e:
                logger.error(f"Error calling notify callback: {e}")
    
    def check_startup_reminders(self) -> str:
        """Check for any missed reminders on startup.
        
        Returns:
            Summary of pending reminders
        """
        active = self.scheduler.get_active_reminders()
        
        if not active:
            return "No reminders to check."
        
        summary = f"I found {len(active)} active reminder(s) from our previous conversation.\n"
        
        upcoming = []
        for task in active[:3]:  # Show first 3
            time_str = task.get('scheduled_time', 'unscheduled')
            content = task.get('content', 'No description')
            upcoming.append(f"{content} at {time_str}")
        
        if upcoming:
            summary += "Your reminders: " + ", ".join(upcoming)
            if len(active) > 3:
                summary += f", and {len(active) - 3} more."
        
        return summary
    
    def set_notify_callback(self, callback: Callable[[str], None]) -> None:
        """Set or update the notification callback function.
        
        Args:
            callback: Function that takes a message string
        """
        self.notify_callback = callback
        logger.debug("Notification callback updated")


class AsyncReminderService:
    """Async version of reminder service for concurrent operation."""
    
    def __init__(self, task_scheduler: TaskScheduler, notify_callback: Optional[Callable[[str], None]] = None):
        """Initialize async reminder service.
        
        Args:
            task_scheduler: TaskScheduler instance
            notify_callback: Function to call for notifications
        """
        self.scheduler = task_scheduler
        self.notify_callback = notify_callback
        self.running = False
        self.task: Optional[asyncio.Task] = None
        self.check_interval = 30  # Check every 30 seconds
        self.processed_task_ids = set()
    
    async def start(self) -> None:
        """Start async reminder service."""
        if self.running:
            logger.debug("Async reminder service already running")
            return
        
        self.running = True
        self.task = asyncio.create_task(self._run_async())
        logger.info("Async reminder service started")
    
    async def stop(self) -> None:
        """Stop async reminder service."""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Async reminder service stopped")
    
    async def _run_async(self) -> None:
        """Main async service loop."""
        while self.running:
            try:
                await self._check_reminders()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in async reminder service: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _check_reminders(self) -> None:
        """Check for due reminders asynchronously."""
        due_tasks = self.scheduler.get_due_tasks()
        
        for task in due_tasks:
            task_id = task['id']
            if task_id not in self.processed_task_ids:
                await self._trigger_task_async(task)
                self.processed_task_ids.add(task_id)
                
                if task.get('recurring') == 'once':
                    self.scheduler.mark_completed(task_id)
        
        if len(self.processed_task_ids) > 100:
            self.processed_task_ids.clear()
    
    async def _trigger_task_async(self, task: dict) -> None:
        """Trigger a task asynchronously.
        
        Args:
            task: Task dict
        """
        task_type = task.get('type', 'reminder')
        content = task.get('content', 'No description')
        
        messages = {
            'reminder': f"Reminder: {content}",
            'notification': f"Notification: {content}",
            'todo': f"Todo: {content}",
            'alert': f"Alert: {content}",
        }
        
        message = messages.get(task_type, f"Task: {content}")
        
        logger.info(f"Triggered task: {message}")
        
        if self.notify_callback:
            # Run callback in executor to avoid blocking
            loop = asyncio.get_event_loop()
            try:
                await loop.run_in_executor(None, self.notify_callback, message)
            except Exception as e:
                logger.error(f"Error calling notify callback: {e}")
    
    def set_notify_callback(self, callback: Callable[[str], None]) -> None:
        """Set notification callback.
        
        Args:
            callback: Callback function
        """
        self.notify_callback = callback
        logger.debug("Async notification callback updated")
