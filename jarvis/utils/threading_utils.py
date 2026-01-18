"""
Threading utilities for JARVIS - background task management.
Provides thread pooling, background jobs, and async helpers.
"""
import threading
import queue
import time
from typing import Callable, Optional, Any, Dict, List
from concurrent.futures import ThreadPoolExecutor, Future
from jarvis.utils.logger import setup_logger

logger = setup_logger(__name__)


class BackgroundTaskManager:
    """Manages background tasks with queuing and result tracking."""
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize background task manager.
        
        Args:
            max_workers: Maximum number of background worker threads
        """
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="jarvis-bg")
        self.tasks: Dict[str, Future] = {}
        self._lock = threading.Lock()
        logger.info(f"BackgroundTaskManager initialized with {max_workers} workers")
    
    def submit_task(self, task_id: str, func: Callable, *args, **kwargs) -> Optional[Future]:
        """
        Submit a task to run in background.
        
        Args:
            task_id: Unique identifier for the task
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function
            
        Returns:
            Future object for the task result
        """
        with self._lock:
            if task_id in self.tasks and not self.tasks[task_id].done():
                logger.warning(f"Task '{task_id}' already running, skipping duplicate")
                return self.tasks[task_id]
            
            try:
                future = self.executor.submit(func, *args, **kwargs)
                self.tasks[task_id] = future
                logger.debug(f"Task '{task_id}' submitted to background")
                return future
            except Exception as e:
                logger.error(f"Error submitting task '{task_id}': {e}")
                return None
    
    def get_result(self, task_id: str, timeout: int = 5) -> Optional[Any]:
        """
        Get result of a background task (blocking).
        
        Args:
            task_id: Task identifier
            timeout: Seconds to wait for result
            
        Returns:
            Task result or None if failed
        """
        with self._lock:
            if task_id not in self.tasks:
                logger.warning(f"Task '{task_id}' not found")
                return None
            
            future = self.tasks[task_id]
        
        try:
            result = future.result(timeout=timeout)
            logger.debug(f"Task '{task_id}' result retrieved: {str(result)[:50]}...")
            return result
        except Exception as e:
            logger.error(f"Error getting result for task '{task_id}': {e}")
            return None
    
    def is_running(self, task_id: str) -> bool:
        """Check if a task is currently running."""
        with self._lock:
            if task_id not in self.tasks:
                return False
            return not self.tasks[task_id].done()
    
    def get_all_results(self, timeout: int = 5) -> Dict[str, Optional[Any]]:
        """
        Get results of all completed tasks.
        
        Args:
            timeout: Seconds to wait for each task
            
        Returns:
            Dictionary mapping task IDs to results
        """
        results = {}
        with self._lock:
            tasks_copy = dict(self.tasks)
        
        for task_id, future in tasks_copy.items():
            try:
                results[task_id] = future.result(timeout=timeout)
            except Exception as e:
                logger.debug(f"Task '{task_id}' failed: {e}")
                results[task_id] = None
        
        return results
    
    def shutdown(self):
        """Gracefully shutdown all background workers."""
        logger.info("Shutting down BackgroundTaskManager")
        self.executor.shutdown(wait=True)
        logger.info("BackgroundTaskManager shut down")


class SafeThread(threading.Thread):
    """Enhanced Thread with exception handling and logging."""
    
    def __init__(self, target: Callable, args: tuple = (), kwargs: dict = None, name: str = None):
        """
        Initialize safe thread.
        
        Args:
            target: Function to run in thread
            args: Positional arguments for function
            kwargs: Keyword arguments for function
            name: Thread name
        """
        super().__init__(target=self._run_with_logging, daemon=True, name=name)
        self.target = target
        self.args = args
        self.kwargs = kwargs or {}
        self._exception = None
        self._result = None
    
    def _run_with_logging(self):
        """Run target function with exception handling."""
        try:
            logger.debug(f"Thread '{self.name}' started")
            self._result = self.target(*self.args, **self.kwargs)
            logger.debug(f"Thread '{self.name}' completed successfully")
        except Exception as e:
            self._exception = e
            logger.error(f"Exception in thread '{self.name}': {e}", exc_info=True)
    
    def get_result(self) -> Optional[Any]:
        """Get the result of the thread execution."""
        if self._exception:
            raise self._exception
        return self._result


class ThreadSafeQueue:
    """Thread-safe queue wrapper for inter-thread communication."""
    
    def __init__(self, maxsize: int = 0):
        """
        Initialize thread-safe queue.
        
        Args:
            maxsize: Maximum queue size (0 = unlimited)
        """
        self.queue = queue.Queue(maxsize=maxsize)
        logger.debug(f"ThreadSafeQueue initialized (maxsize={maxsize})")
    
    def put(self, item: Any, timeout: Optional[int] = None):
        """Put item in queue."""
        try:
            self.queue.put(item, timeout=timeout)
        except queue.Full:
            logger.warning("Queue is full, item discarded")
    
    def get(self, timeout: Optional[int] = 5) -> Optional[Any]:
        """Get item from queue."""
        try:
            return self.queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def empty(self) -> bool:
        """Check if queue is empty."""
        return self.queue.empty()
    
    def size(self) -> int:
        """Get queue size."""
        return self.queue.qsize()


class RateLimiter:
    """Rate limiter using threading for concurrent request control."""
    
    def __init__(self, max_calls: int, period: int = 1):
        """
        Initialize rate limiter.
        
        Args:
            max_calls: Maximum calls allowed
            period: Time period in seconds
        """
        self.max_calls = max_calls
        self.period = period
        self._calls = []
        self._lock = threading.Lock()
        logger.info(f"RateLimiter initialized: {max_calls} calls per {period}s")
    
    def is_allowed(self) -> bool:
        """Check if another call is allowed."""
        with self._lock:
            now = time.time()
            # Remove old calls outside the period
            self._calls = [call_time for call_time in self._calls if call_time > now - self.period]
            
            if len(self._calls) < self.max_calls:
                self._calls.append(now)
                return True
            return False
    
    def wait_if_needed(self):
        """Wait if rate limit is reached."""
        while not self.is_allowed():
            time.sleep(0.1)


# Global task manager instance
_task_manager: Optional[BackgroundTaskManager] = None


def get_task_manager() -> BackgroundTaskManager:
    """Get or create global background task manager."""
    global _task_manager
    if _task_manager is None:
        _task_manager = BackgroundTaskManager()
    return _task_manager


def run_in_background(func: Callable, *args, task_id: str = None, **kwargs) -> Optional[Future]:
    """
    Convenience function to run a function in background.
    
    Args:
        func: Function to run
        *args: Positional arguments
        task_id: Task identifier (auto-generated if None)
        **kwargs: Keyword arguments
        
    Returns:
        Future object for result
    """
    task_manager = get_task_manager()
    if task_id is None:
        task_id = f"task_{int(time.time() * 1000)}"
    return task_manager.submit_task(task_id, func, *args, **kwargs)
