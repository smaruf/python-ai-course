# Common Pitfalls: Sync-Async Problems

## 📖 Overview

When working with asynchronous code, especially while integrating with AI services, developers often encounter specific pitfalls that lead to bugs, performance issues, or unexpected behavior. This guide covers the most common problems and how to avoid them.

## 🚨 Critical Pitfalls

### 1. Forgetting to Await Async Functions

**Problem**: Calling an async function without `await` returns a coroutine object instead of the actual result.

#### ❌ Wrong
```python
import asyncio

async def fetch_ai_response(prompt):
    await asyncio.sleep(1)  # Simulate API call
    return f"Response to: {prompt}"

async def main():
    # WRONG: Not awaiting
    result = fetch_ai_response("Hello")
    print(result)  # Prints: <coroutine object fetch_ai_response at 0x...>

asyncio.run(main())
```

**Output**: `<coroutine object fetch_ai_response at 0x...>`

#### ✅ Correct
```python
async def main():
    # CORRECT: Properly awaiting
    result = await fetch_ai_response("Hello")
    print(result)  # Prints: Response to: Hello

asyncio.run(main())
```

**Output**: `Response to: Hello`

**Why It Happens**:
- Async functions return coroutine objects that must be awaited
- Without `await`, the function doesn't actually execute
- Python doesn't automatically await async functions

**Warning Signs**:
- `RuntimeWarning: coroutine was never awaited`
- Results showing `<coroutine object ...>` instead of actual values
- Functions appearing to do nothing

---

### 2. Blocking the Event Loop

**Problem**: Using blocking synchronous operations in async code prevents other tasks from running.

#### ❌ Wrong
```python
import asyncio
import time

async def slow_operation():
    print("Starting operation 1")
    time.sleep(3)  # WRONG: Blocks event loop!
    print("Finished operation 1")

async def fast_operation():
    print("Starting operation 2")
    await asyncio.sleep(0.1)
    print("Finished operation 2")

async def main():
    await asyncio.gather(
        slow_operation(),
        fast_operation()
    )

asyncio.run(main())
```

**Output**:
```
Starting operation 1
[3 second pause - NOTHING ELSE RUNS]
Finished operation 1
Starting operation 2
Finished operation 2
```

#### ✅ Correct
```python
async def slow_operation():
    print("Starting operation 1")
    await asyncio.sleep(3)  # CORRECT: Non-blocking sleep
    print("Finished operation 1")

async def fast_operation():
    print("Starting operation 2")
    await asyncio.sleep(0.1)
    print("Finished operation 2")

async def main():
    await asyncio.gather(
        slow_operation(),
        fast_operation()
    )

asyncio.run(main())
```

**Output**:
```
Starting operation 1
Starting operation 2
Finished operation 2
[continues waiting for operation 1]
Finished operation 1
```

**Common Blocking Operations**:
- `time.sleep()` → Use `asyncio.sleep()`
- `requests.get()` → Use `aiohttp` or `httpx`
- `open().read()` → Use `aiofiles`
- Synchronous database calls → Use async database drivers

---

### 3. Creating Event Loop Conflicts

**Problem**: Attempting to create or run nested event loops causes errors.

#### ❌ Wrong
```python
import asyncio

async def nested_async_call():
    return "Result"

def sync_wrapper():
    # WRONG: Creates nested event loop
    result = asyncio.run(nested_async_call())
    return result

async def main():
    # This will fail if event loop already exists
    result = await asyncio.to_thread(sync_wrapper)
    print(result)

# ERROR: Cannot run event loop inside event loop
asyncio.run(main())
```

**Error**: `RuntimeError: asyncio.run() cannot be called from a running event loop`

#### ✅ Correct - Option 1: Stay Async
```python
async def main():
    # CORRECT: Just await directly
    result = await nested_async_call()
    print(result)

asyncio.run(main())
```

#### ✅ Correct - Option 2: Use Proper Bridge
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def nested_async_call():
    return "Result"

def sync_function():
    """Sync function that needs to call async code"""
    # Create new event loop in this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(nested_async_call())
        return result
    finally:
        loop.close()

# Use from sync context
result = sync_function()
print(result)
```

---

### 4. Mixing Sync and Async Without Proper Bridging

**Problem**: Calling synchronous blocking code from async functions without proper isolation.

#### ❌ Wrong
```python
import asyncio
import requests  # Synchronous library

async def fetch_multiple_urls(urls):
    results = []
    for url in urls:
        # WRONG: Blocks event loop during each request
        response = requests.get(url)
        results.append(response.json())
    return results
```

#### ✅ Correct - Option 1: Use Async Library
```python
import asyncio
import aiohttp

async def fetch_multiple_urls(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
    return results

async def fetch_url(session, url):
    async with session.get(url) as response:
        return await response.json()
```

#### ✅ Correct - Option 2: Run Sync in Thread Pool
```python
import asyncio
import requests
from functools import partial

async def fetch_multiple_urls(urls):
    loop = asyncio.get_event_loop()
    tasks = [
        loop.run_in_executor(None, partial(requests.get, url))
        for url in urls
    ]
    responses = await asyncio.gather(*tasks)
    return [r.json() for r in responses]
```

---

### 5. Not Handling Async Context Properly

**Problem**: Resources like database connections or HTTP sessions not being properly managed in async contexts.

#### ❌ Wrong
```python
import aiohttp

async def fetch_data():
    session = aiohttp.ClientSession()
    # WRONG: Session not properly closed
    async with session.get('https://api.example.com/data') as response:
        return await response.json()
```

**Issues**:
- Resource leak (session not closed)
- Warning: `Unclosed client session`

#### ✅ Correct
```python
import aiohttp

async def fetch_data():
    # CORRECT: Using async context manager
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.example.com/data') as response:
            return await response.json()
```

---

### 6. Race Conditions and Shared State

**Problem**: Multiple async tasks modifying shared state without proper synchronization.

#### ❌ Wrong
```python
import asyncio

counter = 0

async def increment():
    global counter
    temp = counter
    await asyncio.sleep(0.001)  # Simulate some async work
    counter = temp + 1

async def main():
    # WRONG: Race condition
    await asyncio.gather(
        increment(),
        increment(),
        increment()
    )
    print(f"Counter: {counter}")  # Expected: 3, Actual: might be 1 or 2

asyncio.run(main())
```

**Result**: Counter might be 1, 2, or 3 (unpredictable)

#### ✅ Correct - Use Lock
```python
import asyncio

counter = 0
lock = asyncio.Lock()

async def increment():
    global counter
    async with lock:
        temp = counter
        await asyncio.sleep(0.001)
        counter = temp + 1

async def main():
    # CORRECT: Protected by lock
    await asyncio.gather(
        increment(),
        increment(),
        increment()
    )
    print(f"Counter: {counter}")  # Always 3

asyncio.run(main())
```

---

### 7. Improper Error Handling in Async Code

**Problem**: Errors in one async task not being caught properly, affecting other tasks.

#### ❌ Wrong
```python
import asyncio

async def risky_operation(n):
    await asyncio.sleep(0.1)
    if n == 2:
        raise ValueError("Error in task 2")
    return f"Success {n}"

async def main():
    # WRONG: One error stops everything
    results = await asyncio.gather(
        risky_operation(1),
        risky_operation(2),  # This will raise
        risky_operation(3)
    )
    print(results)

asyncio.run(main())
```

**Result**: Entire program crashes, tasks 1 and 3 don't complete

#### ✅ Correct - Handle Errors Gracefully
```python
import asyncio

async def risky_operation(n):
    await asyncio.sleep(0.1)
    if n == 2:
        raise ValueError("Error in task 2")
    return f"Success {n}"

async def main():
    # CORRECT: return_exceptions=True
    results = await asyncio.gather(
        risky_operation(1),
        risky_operation(2),
        risky_operation(3),
        return_exceptions=True
    )
    
    for i, result in enumerate(results, 1):
        if isinstance(result, Exception):
            print(f"Task {i} failed: {result}")
        else:
            print(f"Task {i}: {result}")

asyncio.run(main())
```

**Output**:
```
Task 1: Success 1
Task 2 failed: Error in task 2
Task 3: Success 3
```

---

### 8. Forgetting to Cancel Tasks

**Problem**: Long-running tasks not being cancelled when no longer needed.

#### ❌ Wrong
```python
import asyncio

async def long_running_task():
    try:
        while True:
            await asyncio.sleep(1)
            print("Still running...")
    except asyncio.CancelledError:
        print("Task was cancelled")

async def main():
    task = asyncio.create_task(long_running_task())
    await asyncio.sleep(3)
    # WRONG: Task keeps running forever
    print("Main finished")

asyncio.run(main())
```

#### ✅ Correct
```python
async def main():
    task = asyncio.create_task(long_running_task())
    await asyncio.sleep(3)
    
    # CORRECT: Cancel the task
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("Task cancelled successfully")
    
    print("Main finished")

asyncio.run(main())
```

---

### 9. Not Using Proper Timeouts

**Problem**: Async operations hanging indefinitely without timeouts.

#### ❌ Wrong
```python
import asyncio

async def potentially_slow_api_call():
    # Might hang forever
    await asyncio.sleep(1000)
    return "data"

async def main():
    # WRONG: No timeout
    result = await potentially_slow_api_call()
    print(result)

asyncio.run(main())
```

#### ✅ Correct
```python
import asyncio

async def potentially_slow_api_call():
    await asyncio.sleep(1000)
    return "data"

async def main():
    # CORRECT: With timeout
    try:
        result = await asyncio.wait_for(
            potentially_slow_api_call(),
            timeout=5.0
        )
        print(result)
    except asyncio.TimeoutError:
        print("Operation timed out after 5 seconds")

asyncio.run(main())
```

---

### 10. Creating Too Many Concurrent Tasks

**Problem**: Creating thousands of tasks without limiting concurrency, overwhelming resources.

#### ❌ Wrong
```python
import asyncio

async def process_item(item):
    await asyncio.sleep(1)
    return item * 2

async def main():
    items = range(10000)
    # WRONG: Creates 10000 concurrent tasks
    results = await asyncio.gather(
        *[process_item(item) for item in items]
    )
    print(f"Processed {len(results)} items")

asyncio.run(main())
```

#### ✅ Correct - Use Semaphore
```python
import asyncio

async def process_item(item, semaphore):
    async with semaphore:
        await asyncio.sleep(1)
        return item * 2

async def main():
    items = range(10000)
    # CORRECT: Limit to 100 concurrent tasks
    semaphore = asyncio.Semaphore(100)
    
    results = await asyncio.gather(
        *[process_item(item, semaphore) for item in items]
    )
    print(f"Processed {len(results)} items")

asyncio.run(main())
```

---

## 🎯 AI-Specific Pitfalls

### 11. Not Batching AI API Calls

**Problem**: Making sequential API calls when batch processing is available.

#### ❌ Wrong
```python
async def process_texts(texts):
    results = []
    for text in texts:
        # WRONG: One API call per text
        result = await ai_api.analyze(text)
        results.append(result)
    return results
```

#### ✅ Correct
```python
async def process_texts(texts):
    # CORRECT: Batch API call
    batch_size = 10
    results = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_results = await ai_api.analyze_batch(batch)
        results.extend(batch_results)
        await asyncio.sleep(0.1)  # Rate limiting
    
    return results
```

### 12. Ignoring Rate Limits

**Problem**: Overwhelming AI APIs without rate limiting.

#### ❌ Wrong
```python
async def analyze_all_documents(documents):
    # WRONG: No rate limiting
    tasks = [ai_api.analyze(doc) for doc in documents]
    return await asyncio.gather(*tasks)
```

#### ✅ Correct
```python
import asyncio
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, calls_per_minute):
        self.calls_per_minute = calls_per_minute
        self.calls = []
    
    async def acquire(self):
        now = datetime.now()
        self.calls = [call for call in self.calls 
                     if now - call < timedelta(minutes=1)]
        
        if len(self.calls) >= self.calls_per_minute:
            sleep_time = (self.calls[0] + timedelta(minutes=1) - now).total_seconds()
            await asyncio.sleep(sleep_time)
        
        self.calls.append(now)

async def analyze_all_documents(documents):
    rate_limiter = RateLimiter(calls_per_minute=60)
    
    async def rate_limited_analyze(doc):
        await rate_limiter.acquire()
        return await ai_api.analyze(doc)
    
    # CORRECT: With rate limiting
    tasks = [rate_limited_analyze(doc) for doc in documents]
    return await asyncio.gather(*tasks)
```

---

## 📋 Checklist: Avoiding Pitfalls

### Before Writing Async Code
- [ ] Understand if the operation is I/O-bound or CPU-bound
- [ ] Check if all libraries support async operations
- [ ] Plan how to handle errors across async tasks
- [ ] Consider resource management (connections, sessions)

### While Writing Async Code
- [ ] Always use `await` with async functions
- [ ] Use `asyncio.sleep()` instead of `time.sleep()`
- [ ] Use async context managers (`async with`)
- [ ] Add timeouts to all external calls
- [ ] Implement proper error handling
- [ ] Limit concurrency with semaphores

### Testing Async Code
- [ ] Test with `pytest-asyncio` or similar
- [ ] Test error conditions and timeouts
- [ ] Test concurrent execution scenarios
- [ ] Monitor for resource leaks
- [ ] Check for race conditions

### For AI Integration
- [ ] Implement rate limiting
- [ ] Use batch processing where available
- [ ] Add retry logic with exponential backoff
- [ ] Monitor API costs and usage
- [ ] Implement circuit breakers for resilience

---

## 🔗 Next Steps

- Review [Best Practices](best-practices.md) for proper implementation patterns
- Study [AI Integration Patterns](ai-integration-patterns.md) for AI-specific solutions
- Practice with examples in `python-examples/problems/` directory
