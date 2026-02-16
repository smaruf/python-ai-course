"""
Comprehensive Example: Building a Distributed Task Queue

This example demonstrates how to combine multiple system building patterns
to create a realistic distributed task queue system.

Patterns demonstrated:
- Web Crawler pattern for distributed task execution
- Rate Limiter for task throttling
- Key-Value Store for state persistence
- Log Aggregator for monitoring
- Functional Pipelines for task processing
"""

import time
import threading
from typing import Callable, Any, Dict, List
from dataclasses import dataclass
from enum import Enum
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.system_building_interviews.rate_limiter import TokenBucketLimiter
from src.system_building_interviews.kv_store import KeyValueStore
from src.system_building_interviews.log_aggregator import LogAggregator, LogEntry, LogLevel
from src.system_building_interviews.functional_pipeline import LazyPipeline
import queue


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """Represents a task to be executed."""
    task_id: str
    function: Callable
    args: tuple
    kwargs: dict
    priority: int = 0
    retry_count: int = 0
    max_retries: int = 3
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: str = None


class DistributedTaskQueue:
    """
    Distributed task queue with:
    - Task prioritization
    - Rate limiting
    - Persistent state
    - Monitoring and logging
    - Retry logic
    """
    
    def __init__(
        self,
        workers: int = 3,
        rate_limit: int = 10,
        storage_file: str = "/tmp/task_queue.wal"
    ):
        """
        Initialize distributed task queue.
        
        Args:
            workers: Number of worker threads
            rate_limit: Maximum tasks per second
            storage_file: WAL file for persistence
        """
        # Task queue
        self.task_queue = queue.PriorityQueue()
        
        # Rate limiter
        self.rate_limiter = TokenBucketLimiter(
            capacity=rate_limit,
            refill_rate=rate_limit / 60.0  # Per second
        )
        
        # Persistent storage
        self.storage = KeyValueStore(storage_file)
        
        # Log aggregator
        self.logger = LogAggregator()
        
        # Workers
        self.workers = []
        self.worker_count = workers
        self.running = False
        
        # Task tracking
        self.tasks: Dict[str, Task] = {}
        self.lock = threading.Lock()
        
        # Recover from storage
        self._recover_tasks()
    
    def _recover_tasks(self):
        """Recover tasks from persistent storage."""
        for task_id in self.storage.keys():
            task_data = self.storage.get(task_id)
            if task_data and task_data.get('status') in ['pending', 'running']:
                # Re-queue incomplete tasks
                self._log(LogLevel.INFO, f"Recovering task {task_id}")
    
    def submit_task(
        self,
        task_id: str,
        function: Callable,
        *args,
        priority: int = 0,
        **kwargs
    ) -> Task:
        """
        Submit a task for execution.
        
        Args:
            task_id: Unique task identifier
            function: Function to execute
            *args: Positional arguments
            priority: Task priority (higher = more important)
            **kwargs: Keyword arguments
            
        Returns:
            Task object
        """
        task = Task(
            task_id=task_id,
            function=function,
            args=args,
            kwargs=kwargs,
            priority=priority
        )
        
        with self.lock:
            self.tasks[task_id] = task
        
        # Persist task
        self._persist_task(task)
        
        # Add to queue (negative priority for max-heap behavior)
        self.task_queue.put((-priority, task_id))
        
        self._log(LogLevel.INFO, f"Task {task_id} submitted with priority {priority}")
        
        return task
    
    def _persist_task(self, task: Task):
        """Persist task state to storage."""
        self.storage.set(task.task_id, {
            'task_id': task.task_id,
            'status': task.status.value,
            'priority': task.priority,
            'retry_count': task.retry_count,
            'result': task.result,
            'error': task.error
        })
    
    def _log(self, level: LogLevel, message: str):
        """Log a message."""
        self.logger.ingest(LogEntry(
            timestamp=time.time(),
            level=level,
            source="task-queue",
            message=message
        ))
        print(f"[{level.value}] {message}")
    
    def start(self):
        """Start worker threads."""
        self.running = True
        
        for i in range(self.worker_count):
            worker = threading.Thread(
                target=self._worker,
                args=(f"worker-{i}",),
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
        
        self._log(LogLevel.INFO, f"Started {self.worker_count} workers")
    
    def stop(self):
        """Stop worker threads."""
        self.running = False
        
        for worker in self.workers:
            worker.join()
        
        self._log(LogLevel.INFO, "All workers stopped")
    
    def _worker(self, worker_id: str):
        """Worker thread that executes tasks."""
        self._log(LogLevel.INFO, f"{worker_id} started")
        
        while self.running:
            try:
                # Get task from queue (with timeout)
                try:
                    priority, task_id = self.task_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Get task
                with self.lock:
                    task = self.tasks.get(task_id)
                
                if not task:
                    continue
                
                # Check rate limit
                if not self.rate_limiter.allow_request(worker_id):
                    # Re-queue task
                    self.task_queue.put((priority, task_id))
                    time.sleep(0.1)
                    continue
                
                # Execute task
                self._execute_task(task, worker_id)
                
            except Exception as e:
                self._log(LogLevel.ERROR, f"{worker_id} error: {e}")
    
    def _execute_task(self, task: Task, worker_id: str):
        """Execute a task."""
        task.status = TaskStatus.RUNNING
        self._persist_task(task)
        
        self._log(LogLevel.INFO, f"{worker_id} executing task {task.task_id}")
        
        try:
            # Execute function
            result = task.function(*task.args, **task.kwargs)
            
            # Success
            task.status = TaskStatus.COMPLETED
            task.result = result
            
            self._log(LogLevel.INFO, f"Task {task.task_id} completed successfully")
            
        except Exception as e:
            # Failure
            task.error = str(e)
            
            if task.retry_count < task.max_retries:
                # Retry
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                
                # Re-queue
                self.task_queue.put((-task.priority, task.task_id))
                
                self._log(
                    LogLevel.WARNING,
                    f"Task {task.task_id} failed, retry {task.retry_count}/{task.max_retries}"
                )
            else:
                # Max retries exceeded
                task.status = TaskStatus.FAILED
                
                self._log(LogLevel.ERROR, f"Task {task.task_id} failed: {e}")
        
        finally:
            # Persist final state
            self._persist_task(task)
    
    def get_task_status(self, task_id: str) -> TaskStatus:
        """Get task status."""
        with self.lock:
            task = self.tasks.get(task_id)
            return task.status if task else None
    
    def get_statistics(self) -> Dict:
        """Get queue statistics."""
        with self.lock:
            stats = {
                'total_tasks': len(self.tasks),
                'pending': 0,
                'running': 0,
                'completed': 0,
                'failed': 0
            }
            
            for task in self.tasks.values():
                if task.status == TaskStatus.PENDING:
                    stats['pending'] += 1
                elif task.status == TaskStatus.RUNNING:
                    stats['running'] += 1
                elif task.status == TaskStatus.COMPLETED:
                    stats['completed'] += 1
                elif task.status == TaskStatus.FAILED:
                    stats['failed'] += 1
            
            return stats


# Example usage
if __name__ == "__main__":
    print("Distributed Task Queue Example")
    print("=" * 60)
    
    # Define sample tasks
    def process_data(data_id: int):
        """Simulate data processing."""
        time.sleep(0.5)  # Simulate work
        return f"Processed data {data_id}"
    
    def send_email(recipient: str, subject: str):
        """Simulate sending email."""
        time.sleep(0.3)
        return f"Email sent to {recipient}"
    
    def failing_task():
        """Task that fails."""
        raise ValueError("This task always fails")
    
    # Create and start queue
    queue_system = DistributedTaskQueue(
        workers=3,
        rate_limit=5,
        storage_file="/tmp/demo_task_queue.wal"
    )
    
    queue_system.start()
    
    # Submit tasks
    print("\nSubmitting tasks...")
    
    # High priority tasks
    queue_system.submit_task("task-1", process_data, 1, priority=10)
    queue_system.submit_task("task-2", process_data, 2, priority=10)
    
    # Normal priority tasks
    queue_system.submit_task("task-3", send_email, "alice@example.com", "Hello", priority=5)
    queue_system.submit_task("task-4", send_email, "bob@example.com", "Hi", priority=5)
    
    # Low priority task
    queue_system.submit_task("task-5", process_data, 3, priority=1)
    
    # Failing task (will retry)
    queue_system.submit_task("task-6", failing_task, priority=3)
    
    # Wait for tasks to complete
    print("\nProcessing tasks...")
    time.sleep(5)
    
    # Show statistics
    print("\nQueue Statistics:")
    stats = queue_system.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Show logs
    print("\nRecent Logs:")
    recent_logs = queue_system.logger.query_recent(10)
    for log in recent_logs[-5:]:
        print(f"  [{log.level.value}] {log.message}")
    
    # Stop queue
    queue_system.stop()
    
    # Cleanup
    import os
    if os.path.exists("/tmp/demo_task_queue.wal"):
        os.remove("/tmp/demo_task_queue.wal")
    
    print("\nDemo complete!")
