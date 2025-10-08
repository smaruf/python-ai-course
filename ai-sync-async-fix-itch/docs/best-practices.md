# Best Practices for Sync-Async Programming

## 📖 Overview

This guide provides proven patterns and practices for writing efficient, maintainable, and correct asynchronous code, with special focus on AI integration.

## 🎯 Core Principles

### 1. Choose the Right Approach

**Rule of Thumb**:
- Use **async** for I/O-bound operations (network, database, file operations)
- Use **sync** for CPU-bound operations (data processing, computation)
- Don't mix without clear bridging strategy

### 2. Be Consistent

**Within a Module**:
- Keep all functions either sync or async
- Use a consistent pattern throughout

**Across Boundaries**:
- Create clear adapter layers when bridging sync/async
- Document which functions are async

### 3. Fail Fast and Clearly

- Add timeouts to all external calls
- Handle errors explicitly
- Provide meaningful error messages

---

## ✅ Best Practices

### Practice 1: Proper Async Function Design

#### Pattern: Async All the Way
```python
# ✅ GOOD: Async from top to bottom
async def fetch_user_data(user_id: int) -> dict:
    """Fetch complete user data with all related information"""
    async with aiohttp.ClientSession() as session:
        # Fetch user and orders concurrently
        user, orders = await asyncio.gather(
            fetch_user(session, user_id),
            fetch_orders(session, user_id)
        )
        
        return {
            "user": user,
            "orders": orders,
            "total": sum(order["amount"] for order in orders)
        }

async def fetch_user(session, user_id: int) -> dict:
    async with session.get(f"/api/users/{user_id}") as response:
        return await response.json()

async def fetch_orders(session, user_id: int) -> list:
    async with session.get(f"/api/users/{user_id}/orders") as response:
        return await response.json()
```

#### Anti-Pattern: Mixing Sync and Async
```python
# ❌ BAD: Mixing sync and async
import requests  # Sync library

async def fetch_user_data(user_id: int) -> dict:
    # Blocks event loop!
    user = requests.get(f"/api/users/{user_id}").json()
    
    # Async call after sync blocking
    orders = await fetch_orders_async(user_id)
    
    return {"user": user, "orders": orders}
```

---

### Practice 2: Concurrent Execution with Gather

#### Pattern: Process Multiple Items Concurrently
```python
import asyncio
from typing import List

async def process_items(items: List[str]) -> List[dict]:
    """Process multiple items concurrently"""
    tasks = [process_single_item(item) for item in items]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle results and exceptions
    processed = []
    for item, result in zip(items, results):
        if isinstance(result, Exception):
            print(f"Error processing {item}: {result}")
            processed.append({"item": item, "error": str(result)})
        else:
            processed.append(result)
    
    return processed

async def process_single_item(item: str) -> dict:
    """Process a single item"""
    await asyncio.sleep(0.1)  # Simulate work
    return {"item": item, "processed": True}
```

**Key Points**:
- Use `asyncio.gather()` for concurrent execution
- Set `return_exceptions=True` to handle errors gracefully
- Process results and errors appropriately

---

### Practice 3: Resource Management with Async Context Managers

#### Pattern: Proper Resource Cleanup
```python
import aiohttp
import asyncio
from contextlib import asynccontextmanager

class DatabaseConnection:
    """Async database connection with proper cleanup"""
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def connect(self):
        print("Connecting to database...")
        await asyncio.sleep(0.1)
        self.connected = True
    
    async def close(self):
        print("Closing database connection...")
        await asyncio.sleep(0.1)
        self.connected = False
    
    async def query(self, sql: str):
        if not self.connected:
            raise RuntimeError("Not connected")
        return f"Results for: {sql}"

# Usage
async def get_data():
    async with DatabaseConnection() as db:
        result = await db.query("SELECT * FROM users")
        return result
    # Connection automatically closed
```

---

### Practice 4: Concurrency Control with Semaphores

#### Pattern: Limit Concurrent Operations
```python
import asyncio
from typing import List, Callable, Any

class ConcurrencyLimiter:
    """Limit concurrent operations to prevent overwhelming resources"""
    
    def __init__(self, max_concurrent: int = 10):
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def run(self, coro):
        """Run coroutine with concurrency limit"""
        async with self.semaphore:
            return await coro

async def process_large_batch(items: List[Any], max_concurrent: int = 10):
    """Process large batch with concurrency control"""
    limiter = ConcurrencyLimiter(max_concurrent)
    
    tasks = [
        limiter.run(process_item(item))
        for item in items
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results

async def process_item(item):
    """Process single item"""
    await asyncio.sleep(1)
    return f"Processed: {item}"

# Usage
async def main():
    items = range(100)
    # Only 10 items processed concurrently
    results = await process_large_batch(items, max_concurrent=10)
    print(f"Processed {len(results)} items")
```

---

### Practice 5: Timeout Management

#### Pattern: Add Timeouts to All External Calls
```python
import asyncio
from typing import Optional

async def fetch_with_timeout(
    url: str,
    timeout: float = 5.0
) -> Optional[dict]:
    """Fetch data with timeout protection"""
    try:
        async with asyncio.timeout(timeout):  # Python 3.11+
            return await fetch_data(url)
    except asyncio.TimeoutError:
        print(f"Request to {url} timed out after {timeout}s")
        return None

# For Python < 3.11, use wait_for
async def fetch_with_timeout_legacy(
    url: str,
    timeout: float = 5.0
) -> Optional[dict]:
    """Fetch data with timeout (compatible with older Python)"""
    try:
        return await asyncio.wait_for(
            fetch_data(url),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        print(f"Request to {url} timed out after {timeout}s")
        return None

async def fetch_data(url: str) -> dict:
    """Simulate API call"""
    await asyncio.sleep(10)  # Slow operation
    return {"data": "result"}
```

---

### Practice 6: Proper Error Handling

#### Pattern: Comprehensive Error Handling
```python
import asyncio
import logging
from typing import Optional, TypeVar, Callable
from functools import wraps

T = TypeVar('T')

def async_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0
):
    """Decorator for retrying async functions with exponential backoff"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Optional[T]:
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logging.warning(
                        f"Attempt {attempt + 1}/{max_attempts} failed: {e}"
                    )
                    
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
            
            logging.error(f"All {max_attempts} attempts failed")
            raise last_exception
        
        return wrapper
    return decorator

# Usage
@async_retry(max_attempts=3, delay=1.0, backoff=2.0)
async def unreliable_api_call(url: str) -> dict:
    """API call that might fail"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()
```

---

### Practice 7: Efficient Task Management

#### Pattern: Create and Cancel Tasks Properly
```python
import asyncio
from typing import List, Optional

class TaskManager:
    """Manage async tasks with proper lifecycle"""
    
    def __init__(self):
        self.tasks: List[asyncio.Task] = []
    
    def create_task(self, coro) -> asyncio.Task:
        """Create and track a task"""
        task = asyncio.create_task(coro)
        self.tasks.append(task)
        
        # Remove from list when done
        task.add_done_callback(lambda t: self.tasks.remove(t))
        
        return task
    
    async def cancel_all(self):
        """Cancel all running tasks"""
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        # Wait for all cancellations
        await asyncio.gather(*self.tasks, return_exceptions=True)
        self.tasks.clear()
    
    async def wait_all(self) -> List[any]:
        """Wait for all tasks to complete"""
        if not self.tasks:
            return []
        
        results = await asyncio.gather(*self.tasks, return_exceptions=True)
        self.tasks.clear()
        return results

# Usage
async def main():
    manager = TaskManager()
    
    # Create multiple tasks
    manager.create_task(worker(1))
    manager.create_task(worker(2))
    manager.create_task(worker(3))
    
    # Wait for completion or cancel
    try:
        await asyncio.sleep(5)
        results = await manager.wait_all()
    except KeyboardInterrupt:
        await manager.cancel_all()

async def worker(id: int):
    """Example worker task"""
    try:
        for i in range(10):
            print(f"Worker {id}: iteration {i}")
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print(f"Worker {id} cancelled")
        raise
```

---

### Practice 8: Async Iterators and Generators

#### Pattern: Stream Processing with Async Iterators
```python
import asyncio
from typing import AsyncIterator

async def data_stream() -> AsyncIterator[dict]:
    """Generate data asynchronously"""
    for i in range(10):
        await asyncio.sleep(0.5)  # Simulate data arrival
        yield {"id": i, "data": f"item_{i}"}

async def process_stream():
    """Process data stream as it arrives"""
    async for item in data_stream():
        result = await process_item(item)
        print(f"Processed: {result}")

async def process_item(item: dict) -> dict:
    """Process individual item"""
    await asyncio.sleep(0.1)
    return {**item, "processed": True}
```

---

### Practice 9: Combining Sync and Async (When Necessary)

#### Pattern: Run Sync Code in Executor
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial

def cpu_intensive_task(data: str) -> str:
    """CPU-bound task that should run in thread"""
    # Simulate heavy computation
    result = data.upper()
    # In reality: complex calculations, data processing, etc.
    return result

async def process_with_cpu_task(items: list) -> list:
    """Combine async I/O with sync CPU tasks"""
    loop = asyncio.get_event_loop()
    
    # Run CPU tasks in thread pool
    with ThreadPoolExecutor(max_workers=4) as executor:
        tasks = [
            loop.run_in_executor(
                executor,
                cpu_intensive_task,
                item
            )
            for item in items
        ]
        
        results = await asyncio.gather(*tasks)
    
    return results

# Usage
async def main():
    items = ["data1", "data2", "data3", "data4"]
    results = await process_with_cpu_task(items)
    print(results)
```

---

## 🤖 AI-Specific Best Practices

### Practice 10: Batch AI API Calls

#### Pattern: Efficient Batch Processing
```python
import asyncio
from typing import List

class AIBatchProcessor:
    """Process AI requests in optimized batches"""
    
    def __init__(self, batch_size: int = 5, delay: float = 0.5):
        self.batch_size = batch_size
        self.delay = delay
    
    async def process_texts(self, texts: List[str]) -> List[dict]:
        """Process texts in batches"""
        results = []
        
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            
            # Process batch
            batch_results = await self._process_batch(batch)
            results.extend(batch_results)
            
            # Rate limiting delay
            if i + self.batch_size < len(texts):
                await asyncio.sleep(self.delay)
        
        return results
    
    async def _process_batch(self, batch: List[str]) -> List[dict]:
        """Process a single batch"""
        # In practice, call AI API batch endpoint
        await asyncio.sleep(1)  # Simulate API call
        return [{"text": text, "result": f"processed_{text}"} for text in batch]

# Usage
async def main():
    processor = AIBatchProcessor(batch_size=5, delay=0.5)
    texts = [f"text_{i}" for i in range(20)]
    results = await processor.process_texts(texts)
    print(f"Processed {len(results)} texts")
```

### Practice 11: Rate Limiting for AI APIs

#### Pattern: Token Bucket Rate Limiter
```python
import asyncio
import time
from collections import deque

class RateLimiter:
    """Token bucket rate limiter for API calls"""
    
    def __init__(self, rate: int, per: float = 1.0):
        """
        Args:
            rate: Number of allowed requests
            per: Time period in seconds
        """
        self.rate = rate
        self.per = per
        self.allowance = rate
        self.last_check = time.monotonic()
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire permission to make a request"""
        async with self.lock:
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

# Usage
async def make_ai_request(limiter: RateLimiter, prompt: str) -> str:
    """Make rate-limited AI request"""
    await limiter.acquire()
    # Make actual API call
    return f"Response to: {prompt}"

async def main():
    # 10 requests per second
    limiter = RateLimiter(rate=10, per=1.0)
    
    tasks = [
        make_ai_request(limiter, f"prompt_{i}")
        for i in range(50)
    ]
    
    results = await asyncio.gather(*tasks)
    print(f"Completed {len(results)} requests")
```

### Practice 12: Circuit Breaker for AI Services

#### Pattern: Prevent Cascading Failures
```python
import asyncio
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit breaker active
    HALF_OPEN = "half_open"  # Testing recovery

class CircuitBreaker:
    """Circuit breaker for AI service calls"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
        recovery_timeout: int = 30
    ):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.recovery_timeout = recovery_timeout
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self.lock = asyncio.Lock()
    
    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        async with self.lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                else:
                    raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as e:
            await self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if not self.last_failure_time:
            return True
        
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout
    
    async def _on_success(self):
        """Handle successful call"""
        async with self.lock:
            self.failure_count = 0
            self.state = CircuitState.CLOSED
    
    async def _on_failure(self):
        """Handle failed call"""
        async with self.lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN

# Usage
circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30)

async def protected_ai_call(prompt: str) -> str:
    """AI call protected by circuit breaker"""
    async def ai_api_call():
        # Actual AI API call
        return f"Response to: {prompt}"
    
    try:
        return await circuit_breaker.call(ai_api_call)
    except Exception as e:
        return f"Circuit breaker prevented call: {e}"
```

---

## 📋 Implementation Checklist

### Design Phase
- [ ] Identify I/O-bound vs CPU-bound operations
- [ ] Choose sync or async based on operation type
- [ ] Design error handling strategy
- [ ] Plan resource management approach
- [ ] Consider rate limiting requirements

### Implementation Phase
- [ ] Use async context managers for resources
- [ ] Add timeouts to all external calls
- [ ] Implement proper error handling
- [ ] Use semaphores for concurrency control
- [ ] Add retry logic where appropriate
- [ ] Implement rate limiting for APIs

### Testing Phase
- [ ] Test concurrent execution scenarios
- [ ] Test error handling and timeouts
- [ ] Test resource cleanup
- [ ] Monitor for resource leaks
- [ ] Test under load conditions

### AI Integration Phase
- [ ] Implement batch processing
- [ ] Add rate limiting
- [ ] Implement circuit breakers
- [ ] Add cost tracking
- [ ] Monitor API usage

---

## 🎓 Key Takeaways

1. **Choose Wisely**: Use async for I/O, sync for CPU-bound operations
2. **Be Consistent**: Stick to one paradigm within a module
3. **Handle Errors**: Use `return_exceptions=True` and proper error handling
4. **Manage Resources**: Always use async context managers
5. **Control Concurrency**: Use semaphores to limit concurrent operations
6. **Add Timeouts**: Protect against hanging operations
7. **Batch Wisely**: Group AI API calls for efficiency
8. **Rate Limit**: Protect external services and manage costs
9. **Be Resilient**: Implement circuit breakers and retry logic
10. **Monitor**: Track performance, errors, and resource usage

---

## 🔗 Related Documentation

- [Sync-Async Differences](sync-async-differences.md) - Understanding the fundamentals
- [Common Pitfalls](common-pitfalls.md) - What to avoid
- [AI Integration Patterns](ai-integration-patterns.md) - AI-specific best practices
