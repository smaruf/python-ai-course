#!/usr/bin/env python3
"""
Common Async Mistakes and How to Fix Them
==========================================

This example demonstrates common pitfalls when working with
async code and shows the correct patterns.
"""

import asyncio
import time


# ============================================================================
# MISTAKE 1: Forgetting to Await
# ============================================================================

async def fetch_data():
    """Simulate fetching data"""
    await asyncio.sleep(1)
    return {"data": "important information"}


async def mistake_not_awaiting():
    """❌ WRONG: Not awaiting async function"""
    print("\n" + "="*60)
    print("❌ MISTAKE 1: Forgetting to Await")
    print("="*60)
    
    print("\n🔴 Wrong way (not awaiting):")
    result = fetch_data()  # WRONG! Returns coroutine, not the result
    print(f"   Result: {result}")
    print(f"   Type: {type(result)}")
    print("   ⚠️  This is a coroutine object, not the actual data!")
    
    # Clean up the unawaited coroutine
    result.close()


async def correct_awaiting():
    """✅ CORRECT: Properly awaiting async function"""
    print("\n🟢 Correct way (awaiting properly):")
    result = await fetch_data()  # CORRECT! Waits for and returns actual data
    print(f"   Result: {result}")
    print(f"   Type: {type(result)}")
    print("   ✅ Got the actual data!")


# ============================================================================
# MISTAKE 2: Blocking the Event Loop
# ============================================================================

async def mistake_blocking_event_loop():
    """❌ WRONG: Using blocking operations in async code"""
    print("\n" + "="*60)
    print("❌ MISTAKE 2: Blocking the Event Loop")
    print("="*60)
    
    print("\n🔴 Wrong way (using time.sleep):")
    
    async def task_a():
        print("   Task A starting")
        time.sleep(2)  # WRONG! Blocks entire event loop
        print("   Task A done")
    
    async def task_b():
        print("   Task B starting")
        await asyncio.sleep(0.1)
        print("   Task B done")
    
    start = time.time()
    await asyncio.gather(task_a(), task_b())
    elapsed = time.time() - start
    
    print(f"\n   Time elapsed: {elapsed:.2f}s")
    print("   ⚠️  Task B had to wait for Task A's blocking sleep!")


async def correct_non_blocking():
    """✅ CORRECT: Using non-blocking operations"""
    print("\n🟢 Correct way (using asyncio.sleep):")
    
    async def task_a():
        print("   Task A starting")
        await asyncio.sleep(2)  # CORRECT! Non-blocking
        print("   Task A done")
    
    async def task_b():
        print("   Task B starting")
        await asyncio.sleep(0.1)
        print("   Task B done")
    
    start = time.time()
    await asyncio.gather(task_a(), task_b())
    elapsed = time.time() - start
    
    print(f"\n   Time elapsed: {elapsed:.2f}s")
    print("   ✅ Task B completed while Task A was waiting!")


# ============================================================================
# MISTAKE 3: Creating Nested Event Loops
# ============================================================================

async def nested_async_call():
    """An async function that we want to call"""
    await asyncio.sleep(0.1)
    return "Result from async function"


def mistake_nested_event_loop():
    """❌ WRONG: Trying to run async code from sync context incorrectly"""
    print("\n" + "="*60)
    print("❌ MISTAKE 3: Creating Nested Event Loops")
    print("="*60)
    
    print("\n🔴 Wrong way (calling asyncio.run inside event loop):")
    print("   This would cause: RuntimeError: asyncio.run() cannot be")
    print("   called from a running event loop")
    print("   (Not executing to avoid error)")


async def correct_no_nested_loop():
    """✅ CORRECT: Properly calling async functions"""
    print("\n🟢 Correct way (just await directly):")
    result = await nested_async_call()
    print(f"   Result: {result}")
    print("   ✅ No nested event loop needed!")


# ============================================================================
# MISTAKE 4: Not Handling Errors in gather()
# ============================================================================

async def task_that_fails(task_id: int):
    """A task that might fail"""
    await asyncio.sleep(0.1)
    if task_id == 2:
        raise ValueError(f"Task {task_id} failed!")
    return f"Task {task_id} succeeded"


async def mistake_no_error_handling():
    """❌ WRONG: Not handling errors in gather()"""
    print("\n" + "="*60)
    print("❌ MISTAKE 4: Not Handling Errors in gather()")
    print("="*60)
    
    print("\n🔴 Wrong way (no return_exceptions):")
    try:
        results = await asyncio.gather(
            task_that_fails(1),
            task_that_fails(2),  # This fails
            task_that_fails(3)
        )
    except ValueError as e:
        print(f"   ❌ Exception stopped everything: {e}")
        print("   ⚠️  Tasks 1 and 3 didn't get to report their results!")


async def correct_error_handling():
    """✅ CORRECT: Properly handling errors in gather()"""
    print("\n🟢 Correct way (with return_exceptions=True):")
    results = await asyncio.gather(
        task_that_fails(1),
        task_that_fails(2),  # This fails
        task_that_fails(3),
        return_exceptions=True
    )
    
    for i, result in enumerate(results, 1):
        if isinstance(result, Exception):
            print(f"   ❌ Task {i}: {result}")
        else:
            print(f"   ✅ Task {i}: {result}")
    
    print("   ✅ All tasks completed, errors handled gracefully!")


# ============================================================================
# MISTAKE 5: Not Closing Resources
# ============================================================================

class FakeConnection:
    """Simulates a connection that needs cleanup"""
    
    def __init__(self, name: str):
        self.name = name
        self.closed = False
        print(f"   🔌 {name} opened")
    
    async def query(self, sql: str):
        if self.closed:
            raise RuntimeError("Connection is closed")
        await asyncio.sleep(0.1)
        return f"Results for: {sql}"
    
    async def close(self):
        self.closed = True
        print(f"   🔌 {name} closed")


async def mistake_not_closing_resources():
    """❌ WRONG: Not properly closing resources"""
    print("\n" + "="*60)
    print("❌ MISTAKE 5: Not Closing Resources")
    print("="*60)
    
    print("\n🔴 Wrong way (resource not closed):")
    conn = FakeConnection("Database-1")
    result = await conn.query("SELECT * FROM users")
    print(f"   Query result: {result}")
    # WRONG! Forgot to close the connection
    print("   ⚠️  Connection left open (resource leak)!")


async def correct_resource_management():
    """✅ CORRECT: Properly managing resources"""
    print("\n🟢 Correct way (using async context manager):")
    
    # First, let's create a proper async context manager
    class ProperConnection:
        def __init__(self, name: str):
            self.name = name
            self.closed = False
        
        async def __aenter__(self):
            print(f"   🔌 {self.name} opened")
            return self
        
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            self.closed = True
            print(f"   🔌 {self.name} closed")
        
        async def query(self, sql: str):
            if self.closed:
                raise RuntimeError("Connection is closed")
            await asyncio.sleep(0.1)
            return f"Results for: {sql}"
    
    async with ProperConnection("Database-2") as conn:
        result = await conn.query("SELECT * FROM users")
        print(f"   Query result: {result}")
    
    print("   ✅ Connection automatically closed!")


# ============================================================================
# MISTAKE 6: Race Conditions with Shared State
# ============================================================================

counter = 0


async def mistake_race_condition():
    """❌ WRONG: Shared state without synchronization"""
    print("\n" + "="*60)
    print("❌ MISTAKE 6: Race Conditions with Shared State")
    print("="*60)
    
    global counter
    counter = 0
    
    async def increment():
        global counter
        temp = counter
        await asyncio.sleep(0.01)  # Simulate some work
        counter = temp + 1
    
    print("\n🔴 Wrong way (no synchronization):")
    await asyncio.gather(
        increment(),
        increment(),
        increment()
    )
    print(f"   Counter value: {counter}")
    print(f"   Expected: 3, Got: {counter}")
    print("   ⚠️  Race condition caused incorrect result!")


async def correct_synchronization():
    """✅ CORRECT: Using locks for shared state"""
    print("\n🟢 Correct way (using asyncio.Lock):")
    
    counter_safe = 0
    lock = asyncio.Lock()
    
    async def increment_safe():
        nonlocal counter_safe
        async with lock:
            temp = counter_safe
            await asyncio.sleep(0.01)
            counter_safe = temp + 1
    
    await asyncio.gather(
        increment_safe(),
        increment_safe(),
        increment_safe()
    )
    print(f"   Counter value: {counter_safe}")
    print(f"   Expected: 3, Got: {counter_safe}")
    print("   ✅ Lock prevented race condition!")


# ============================================================================
# MISTAKE 7: Not Using Timeouts
# ============================================================================

async def slow_api_call():
    """Simulates a slow API that might hang"""
    await asyncio.sleep(10)
    return "Data"


async def mistake_no_timeout():
    """❌ WRONG: No timeout on potentially slow operations"""
    print("\n" + "="*60)
    print("❌ MISTAKE 7: Not Using Timeouts")
    print("="*60)
    
    print("\n🔴 Wrong way (no timeout):")
    print("   Without timeout, this would wait 10 seconds!")
    print("   (Skipping actual execution)")


async def correct_with_timeout():
    """✅ CORRECT: Using timeout for slow operations"""
    print("\n🟢 Correct way (with timeout):")
    
    try:
        result = await asyncio.wait_for(slow_api_call(), timeout=1.0)
        print(f"   Result: {result}")
    except asyncio.TimeoutError:
        print("   ⏰ Operation timed out after 1 second")
        print("   ✅ Prevented hanging indefinitely!")


# ============================================================================
# MISTAKE 8: Not Limiting Concurrency
# ============================================================================

async def api_call(item_id: int):
    """Simulate an API call"""
    await asyncio.sleep(0.1)
    return f"Result for item {item_id}"


async def mistake_unlimited_concurrency():
    """❌ WRONG: Creating too many concurrent tasks"""
    print("\n" + "="*60)
    print("❌ MISTAKE 8: Not Limiting Concurrency")
    print("="*60)
    
    print("\n🔴 Wrong way (1000 concurrent tasks):")
    items = range(1000)
    tasks = [api_call(i) for i in items]
    # This creates 1000 concurrent connections!
    print("   Creating 1000 concurrent tasks...")
    print("   ⚠️  Could overwhelm server or exhaust resources!")
    print("   (Skipping execution)")


async def correct_limited_concurrency():
    """✅ CORRECT: Limiting concurrency with semaphore"""
    print("\n🟢 Correct way (limited to 10 concurrent):")
    
    semaphore = asyncio.Semaphore(10)
    
    async def limited_api_call(item_id: int):
        async with semaphore:
            return await api_call(item_id)
    
    items = range(50)
    tasks = [limited_api_call(i) for i in items]
    results = await asyncio.gather(*tasks)
    
    print(f"   Processed {len(results)} items")
    print("   ✅ Only 10 concurrent connections at a time!")


# ============================================================================
# MAIN
# ============================================================================

async def main():
    """Run all mistake demonstrations"""
    print("\n🔄 Common Async Mistakes and How to Fix Them\n")
    print("This example shows common pitfalls and correct patterns.")
    
    # Mistake 1: Not awaiting
    await mistake_not_awaiting()
    await correct_awaiting()
    
    # Mistake 2: Blocking event loop
    await mistake_blocking_event_loop()
    await correct_non_blocking()
    
    # Mistake 3: Nested event loops
    mistake_nested_event_loop()
    await correct_no_nested_loop()
    
    # Mistake 4: Error handling
    await mistake_no_error_handling()
    await correct_error_handling()
    
    # Mistake 5: Resource management
    await mistake_not_closing_resources()
    await correct_resource_management()
    
    # Mistake 6: Race conditions
    await mistake_race_condition()
    await correct_synchronization()
    
    # Mistake 7: Timeouts
    await mistake_no_timeout()
    await correct_with_timeout()
    
    # Mistake 8: Concurrency limits
    await mistake_unlimited_concurrency()
    await correct_limited_concurrency()
    
    print("\n" + "="*60)
    print("✅ All demonstrations completed!")
    print("="*60)
    print("\n💡 Key Takeaways:")
    print("1. Always await async functions")
    print("2. Use asyncio.sleep() not time.sleep()")
    print("3. Don't create nested event loops")
    print("4. Handle errors with return_exceptions=True")
    print("5. Use async context managers for resources")
    print("6. Use locks for shared state")
    print("7. Always add timeouts to external operations")
    print("8. Limit concurrency with semaphores")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
