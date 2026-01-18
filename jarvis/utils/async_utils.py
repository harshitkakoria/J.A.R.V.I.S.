"""
Async utilities for concurrent JARVIS operations.
Enables parallel execution of skills, reminders, TTS, and other tasks.
"""
import asyncio
import threading
from typing import Callable, Optional, Any, List, Coroutine
from concurrent.futures import ThreadPoolExecutor
from jarvis.utils.logger import setup_logger

logger = setup_logger(__name__)


class AsyncManager:
    """Manages async operations and thread pools."""
    
    def __init__(self, max_workers: int = 4):
        """Initialize async manager.
        
        Args:
            max_workers: Max workers for thread pool
        """
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.running_tasks: List[asyncio.Task] = []
    
    def set_event_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Set the event loop.
        
        Args:
            loop: Event loop to use
        """
        self.loop = loop
    
    async def run_in_executor(self, func: Callable, *args) -> Any:
        """Run blocking function in executor.
        
        Args:
            func: Blocking function
            *args: Arguments for function
            
        Returns:
            Result from function
        """
        if self.loop is None:
            self.loop = asyncio.get_event_loop()
        return await self.loop.run_in_executor(self.executor, func, *args)
    
    async def gather_tasks(self, *coros: Coroutine) -> List[Any]:
        """Run multiple coroutines concurrently.
        
        Args:
            *coros: Coroutines to run
            
        Returns:
            List of results
        """
        return await asyncio.gather(*coros, return_exceptions=True)
    
    def create_task(self, coro: Coroutine) -> asyncio.Task:
        """Create and track a task.
        
        Args:
            coro: Coroutine to run
            
        Returns:
            Created task
        """
        if self.loop is None:
            self.loop = asyncio.get_event_loop()
        
        task = self.loop.create_task(coro)
        self.running_tasks.append(task)
        task.add_done_callback(self.running_tasks.remove)
        return task
    
    async def wait_for_tasks(self, timeout: Optional[float] = None) -> None:
        """Wait for all running tasks to complete.
        
        Args:
            timeout: Timeout in seconds
        """
        if self.running_tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self.running_tasks),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                logger.warning("Task wait timeout")
    
    def shutdown(self) -> None:
        """Shutdown executor."""
        self.executor.shutdown(wait=True)


class ParallelExecutor:
    """Execute multiple operations in parallel."""
    
    @staticmethod
    async def execute_skills_parallel(skills: List[tuple]) -> List[Any]:
        """Execute multiple skills in parallel.
        
        Args:
            skills: List of (skill_name, skill_func, query) tuples
            
        Returns:
            List of results
        """
        tasks = []
        for skill_name, skill_func, query in skills:
            task = ParallelExecutor._execute_skill(skill_name, skill_func, query)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
    
    @staticmethod
    async def _execute_skill(name: str, func: Callable, query: str) -> Any:
        """Execute a single skill asynchronously.
        
        Args:
            name: Skill name
            func: Skill function
            query: Query string
            
        Returns:
            Skill result
        """
        try:
            # If function is async, await it; otherwise run in executor
            if asyncio.iscoroutinefunction(func):
                result = await func(query)
            else:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, func, query)
            
            logger.debug(f"Skill '{name}' completed")
            return result
        except Exception as e:
            logger.error(f"Skill '{name}' error: {e}")
            return None
    
    @staticmethod
    async def execute_with_timeout(coro: Coroutine, timeout: float) -> Any:
        """Execute coroutine with timeout.
        
        Args:
            coro: Coroutine to execute
            timeout: Timeout in seconds
            
        Returns:
            Result or None if timeout
        """
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning(f"Operation timed out after {timeout}s")
            return None


async def async_sleep(duration: float) -> None:
    """Non-blocking sleep.
    
    Args:
        duration: Sleep duration in seconds
    """
    await asyncio.sleep(duration)


async def async_map(func: Callable, items: List[Any]) -> List[Any]:
    """Apply async function to items in parallel.
    
    Args:
        func: Async function
        items: Items to process
        
    Returns:
        List of results
    """
    tasks = [func(item) for item in items]
    return await asyncio.gather(*tasks, return_exceptions=True)


def run_async(coro: Coroutine) -> Any:
    """Run async code from sync context.
    
    Args:
        coro: Coroutine to run
        
    Returns:
        Result
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Can't use run() if loop already running
            future = asyncio.ensure_future(coro)
            return future
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        # No event loop, create new one
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        try:
            return new_loop.run_until_complete(coro)
        finally:
            new_loop.close()


# Global async manager instance
_async_manager = None


def get_async_manager(max_workers: int = 4) -> AsyncManager:
    """Get global async manager.
    
    Args:
        max_workers: Max workers for executor
        
    Returns:
        AsyncManager instance
    """
    global _async_manager
    if _async_manager is None:
        _async_manager = AsyncManager(max_workers=max_workers)
    return _async_manager
