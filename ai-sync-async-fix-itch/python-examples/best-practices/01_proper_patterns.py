#!/usr/bin/env python3
"""
Proper Async Patterns and Best Practices
=========================================

This example demonstrates recommended async patterns for production code.
"""

import asyncio
import time
from typing import List, Dict, Optional, TypeVar, Callable
from dataclasses import dataclass
from enum import Enum


# ============================================================================
# PATTERN 1: Async Context Manager for Resource Management
# ============================================================================

class DatabaseConnection:
    """Example async context manager for database connections"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connected = False
    
    async def __aenter__(self):
        """Called when entering async with block"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Called when exiting async with block"""
        await self.close()
        return False  # Don't suppress exceptions
    
    async def connect(self):
        """Establish connection"""
        print(f"   Connecting to {self.connection_string}...")
        await asyncio.sleep(0.1)
        self.connected = True
        print("   ✅ Connected")
    
    async def close(self):
        """Close connection"""
        print("   Closing connection...")
        await asyncio.sleep(0.1)
        self.connected = False
        print("   ✅ Closed")
    
    async def query(self, sql: str) -> List[Dict]:
        """Execute a query"""
        if not self.connected:
            raise RuntimeError("Not connected to database")
        await asyncio.sleep(0.1)
        return [{"id": 1, "data": "result"}]


async def pattern_context_manager():
    """Demonstrate proper resource management"""
    print("\n" + "="*60)
    print("PATTERN 1: Async Context Manager")
    print("="*60)
    
    # Resources are automatically cleaned up
    async with DatabaseConnection("postgres://localhost/mydb") as db:
        results = await db.query("SELECT * FROM users")
        print(f"   Results: {results}")
    # Connection automatically closed here, even if exception occurs
    
    print("\n   ✅ Resource properly managed and cleaned up")


# ============================================================================
# PATTERN 2: Concurrency Control with Semaphore
# ============================================================================

async def pattern_semaphore():
    """Demonstrate concurrency limiting"""
    print("\n" + "="*60)
    print("PATTERN 2: Concurrency Control with Semaphore")
    print("="*60)
    
    # Limit to 3 concurrent operations
    semaphore = asyncio.Semaphore(3)
    
    async def limited_operation(item_id: int):
        """Operation with concurrency limit"""
        async with semaphore:
            print(f"   Processing item {item_id}")
            await asyncio.sleep(0.5)
            return f"Result {item_id}"
    
    # Process 10 items, but max 3 at a time
    items = range(1, 11)
    tasks = [limited_operation(i) for i in items]
    
    print("   Processing 10 items with max 3 concurrent...")
    results = await asyncio.gather(*tasks)
    
    print(f"   ✅ Processed {len(results)} items with controlled concurrency")


# ============================================================================
# PATTERN 3: Proper Error Handling
# ============================================================================

async def pattern_error_handling():
    """Demonstrate proper error handling in async code"""
    print("\n" + "="*60)
    print("PATTERN 3: Proper Error Handling")
    print("="*60)
    
    async def risky_operation(item_id: int):
        """Operation that might fail"""
        await asyncio.sleep(0.1)
        if item_id == 3:
            raise ValueError(f"Item {item_id} failed")
        return f"Success {item_id}"
    
    # Gather with return_exceptions to handle errors gracefully
    results = await asyncio.gather(
        risky_operation(1),
        risky_operation(2),
        risky_operation(3),  # This will fail
        risky_operation(4),
        return_exceptions=True
    )
    
    # Process results and errors
    print("   Results:")
    for i, result in enumerate(results, 1):
        if isinstance(result, Exception):
            print(f"      ❌ Item {i}: {result}")
        else:
            print(f"      ✅ Item {i}: {result}")
    
    print("\n   ✅ All tasks completed, errors handled gracefully")


# ============================================================================
# PATTERN 4: Timeout Management
# ============================================================================

async def pattern_timeouts():
    """Demonstrate proper timeout handling"""
    print("\n" + "="*60)
    print("PATTERN 4: Timeout Management")
    print("="*60)
    
    async def slow_operation(duration: float):
        """Operation that might take too long"""
        await asyncio.sleep(duration)
        return "Success"
    
    # Pattern 4a: Single operation with timeout
    print("\n   4a. Single operation with timeout:")
    try:
        result = await asyncio.wait_for(
            slow_operation(2.0),
            timeout=1.0
        )
        print(f"      ✅ {result}")
    except asyncio.TimeoutError:
        print("      ⏰ Operation timed out (as expected)")
    
    # Pattern 4b: Multiple operations with individual timeouts
    print("\n   4b. Multiple operations with individual timeouts:")
    
    async def operation_with_timeout(duration: float, timeout: float):
        """Wrapper that adds timeout to operation"""
        try:
            return await asyncio.wait_for(slow_operation(duration), timeout)
        except asyncio.TimeoutError:
            return f"Timed out after {timeout}s"
    
    results = await asyncio.gather(
        operation_with_timeout(0.5, 1.0),
        operation_with_timeout(1.5, 1.0),
        operation_with_timeout(0.3, 1.0)
    )
    
    for i, result in enumerate(results, 1):
        print(f"      Task {i}: {result}")


# ============================================================================
# PATTERN 5: Task Management and Cancellation
# ============================================================================

async def pattern_task_management():
    """Demonstrate proper task management"""
    print("\n" + "="*60)
    print("PATTERN 5: Task Management and Cancellation")
    print("="*60)
    
    async def long_running_task(task_id: int):
        """A long-running task that can be cancelled"""
        try:
            print(f"   Task {task_id} started")
            for i in range(5):
                await asyncio.sleep(0.5)
                print(f"   Task {task_id}: iteration {i+1}/5")
            print(f"   Task {task_id} completed")
            return f"Task {task_id} result"
        except asyncio.CancelledError:
            print(f"   Task {task_id} cancelled")
            # Cleanup code here
            raise
    
    # Create tasks
    task1 = asyncio.create_task(long_running_task(1))
    task2 = asyncio.create_task(long_running_task(2))
    
    # Let them run briefly
    await asyncio.sleep(1.5)
    
    # Cancel task 2
    print("\n   Cancelling task 2...")
    task2.cancel()
    
    # Wait for both (task2 will raise CancelledError)
    results = await asyncio.gather(task1, task2, return_exceptions=True)
    
    print("\n   Results:")
    for i, result in enumerate(results, 1):
        if isinstance(result, asyncio.CancelledError):
            print(f"      Task {i}: Cancelled")
        else:
            print(f"      Task {i}: {result}")


# ============================================================================
# PATTERN 6: Retry Logic with Exponential Backoff
# ============================================================================

async def pattern_retry_logic():
    """Demonstrate retry logic with exponential backoff"""
    print("\n" + "="*60)
    print("PATTERN 6: Retry Logic with Exponential Backoff")
    print("="*60)
    
    async def unreliable_operation():
        """Operation that fails randomly"""
        import random
        if random.random() < 0.7:  # 70% failure rate
            raise ConnectionError("Connection failed")
        return "Success"
    
    async def retry_with_backoff(
        operation: Callable,
        max_retries: int = 3,
        base_delay: float = 1.0,
        backoff_factor: float = 2.0
    ):
        """Retry operation with exponential backoff"""
        for attempt in range(max_retries):
            try:
                return await operation()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                
                delay = base_delay * (backoff_factor ** attempt)
                print(f"   Attempt {attempt + 1} failed: {e}")
                print(f"   Retrying in {delay:.1f}s...")
                await asyncio.sleep(delay)
    
    # Try the unreliable operation with retry logic
    try:
        result = await retry_with_backoff(unreliable_operation)
        print(f"   ✅ {result}")
    except Exception as e:
        print(f"   ❌ All retries failed: {e}")


# ============================================================================
# PATTERN 7: Rate Limiting
# ============================================================================

class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, rate: float, per: float = 1.0):
        """
        Args:
            rate: Number of operations allowed
            per: Time period in seconds
        """
        self.rate = rate
        self.per = per
        self.allowance = rate
        self.last_check = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire permission to perform an operation"""
        async with self._lock:
            current = time.monotonic()
            time_passed = current - self.last_check
            self.last_check = current
            
            # Replenish tokens
            self.allowance += time_passed * (self.rate / self.per)
            if self.allowance > self.rate:
                self.allowance = self.rate
            
            # Wait if no tokens available
            if self.allowance < 1.0:
                sleep_time = (1.0 - self.allowance) * (self.per / self.rate)
                await asyncio.sleep(sleep_time)
                self.allowance = 1.0
            
            self.allowance -= 1.0


async def pattern_rate_limiting():
    """Demonstrate rate limiting"""
    print("\n" + "="*60)
    print("PATTERN 7: Rate Limiting")
    print("="*60)
    
    # Allow 5 operations per second
    limiter = RateLimiter(rate=5, per=1.0)
    
    async def rate_limited_operation(op_id: int):
        """Operation with rate limiting"""
        await limiter.acquire()
        print(f"   Operation {op_id} executed at {time.time():.2f}")
        await asyncio.sleep(0.1)
        return f"Result {op_id}"
    
    # Try to execute 10 operations
    print("   Executing 10 operations with 5/second limit...")
    start = time.time()
    
    tasks = [rate_limited_operation(i) for i in range(1, 11)]
    results = await asyncio.gather(*tasks)
    
    elapsed = time.time() - start
    print(f"\n   ✅ Completed {len(results)} operations in {elapsed:.2f}s")
    print(f"   Expected: ~2s (10 ops at 5/sec), Actual: {elapsed:.2f}s")


# ============================================================================
# PATTERN 8: Async Iterator for Streaming
# ============================================================================

async def pattern_async_iterator():
    """Demonstrate async iterators for streaming data"""
    print("\n" + "="*60)
    print("PATTERN 8: Async Iterator for Streaming")
    print("="*60)
    
    async def data_stream(count: int):
        """Generate data asynchronously"""
        for i in range(count):
            await asyncio.sleep(0.2)  # Simulate data arrival
            yield {"id": i, "data": f"item_{i}"}
    
    print("   Processing data stream...")
    
    # Process data as it arrives
    async for item in data_stream(5):
        print(f"      Received: {item}")
    
    print("   ✅ Stream processing completed")


# ============================================================================
# PATTERN 9: Task Group (Python 3.11+)
# ============================================================================

async def pattern_task_group():
    """Demonstrate structured concurrency with TaskGroup"""
    print("\n" + "="*60)
    print("PATTERN 9: Structured Concurrency (Python 3.11+)")
    print("="*60)
    
    async def worker(worker_id: int):
        """A worker task"""
        await asyncio.sleep(0.5)
        print(f"   Worker {worker_id} completed")
        return f"Result {worker_id}"
    
    try:
        # Python 3.11+ feature
        async with asyncio.TaskGroup() as tg:
            task1 = tg.create_task(worker(1))
            task2 = tg.create_task(worker(2))
            task3 = tg.create_task(worker(3))
        
        print("   ✅ All tasks in group completed")
    except AttributeError:
        print("   ⚠️  TaskGroup requires Python 3.11+")
        print("   Using alternative pattern...")
        
        # Alternative for older Python versions
        results = await asyncio.gather(
            worker(1),
            worker(2),
            worker(3)
        )
        print("   ✅ All tasks completed (alternative method)")


# ============================================================================
# MAIN
# ============================================================================

async def main():
    """Run all pattern demonstrations"""
    print("\n🔄 Proper Async Patterns and Best Practices\n")
    print("This example demonstrates recommended patterns for production code.")
    
    await pattern_context_manager()
    await pattern_semaphore()
    await pattern_error_handling()
    await pattern_timeouts()
    await pattern_task_management()
    await pattern_retry_logic()
    await pattern_rate_limiting()
    await pattern_async_iterator()
    await pattern_task_group()
    
    print("\n" + "="*60)
    print("✅ All patterns demonstrated!")
    print("="*60)
    
    print("\n💡 Key Takeaways:")
    print("1. Use async context managers for resource management")
    print("2. Control concurrency with semaphores")
    print("3. Handle errors gracefully with return_exceptions=True")
    print("4. Always add timeouts to external operations")
    print("5. Properly manage and cancel tasks")
    print("6. Implement retry logic for unreliable operations")
    print("7. Use rate limiting to respect API limits")
    print("8. Use async iterators for streaming data")
    print("9. Consider TaskGroup for structured concurrency")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
