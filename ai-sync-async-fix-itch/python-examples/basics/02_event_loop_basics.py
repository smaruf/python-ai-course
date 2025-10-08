#!/usr/bin/env python3
"""
Event Loop Basics
=================

Understanding how the async event loop works and manages tasks.
"""

import asyncio
import time
from typing import List


# ============================================================================
# BASIC EVENT LOOP CONCEPTS
# ============================================================================

async def simple_coroutine(name: str, duration: float):
    """A simple coroutine that sleeps for a duration"""
    print(f"[{name}] Starting...")
    await asyncio.sleep(duration)
    print(f"[{name}] Completed after {duration}s")
    return f"{name} result"


async def demo_event_loop_basics():
    """Demonstrate basic event loop concepts"""
    print("\n" + "="*60)
    print("EVENT LOOP BASICS")
    print("="*60)
    
    print("\n1️⃣  Running a single coroutine:")
    result = await simple_coroutine("Task-A", 1.0)
    print(f"   Result: {result}\n")
    
    print("2️⃣  Running multiple coroutines sequentially:")
    result1 = await simple_coroutine("Task-B", 0.5)
    result2 = await simple_coroutine("Task-C", 0.5)
    print(f"   Results: {result1}, {result2}\n")
    
    print("3️⃣  Running multiple coroutines concurrently:")
    results = await asyncio.gather(
        simple_coroutine("Task-D", 0.5),
        simple_coroutine("Task-E", 0.5),
        simple_coroutine("Task-F", 0.5)
    )
    print(f"   Results: {results}")


# ============================================================================
# TASK CREATION AND MANAGEMENT
# ============================================================================

async def worker(worker_id: int, work_time: float):
    """Simulate a worker doing some work"""
    print(f"  Worker {worker_id} starting work...")
    await asyncio.sleep(work_time)
    print(f"  Worker {worker_id} finished work")
    return f"Worker {worker_id} result"


async def demo_task_creation():
    """Demonstrate different ways to create and manage tasks"""
    print("\n" + "="*60)
    print("TASK CREATION AND MANAGEMENT")
    print("="*60)
    
    # Method 1: asyncio.gather()
    print("\n📋 Method 1: asyncio.gather() - Wait for all tasks")
    start = time.time()
    results = await asyncio.gather(
        worker(1, 1.0),
        worker(2, 0.5),
        worker(3, 0.8)
    )
    print(f"   Completed in {time.time() - start:.2f}s")
    print(f"   Results: {results}\n")
    
    # Method 2: create_task()
    print("📋 Method 2: create_task() - More control over tasks")
    start = time.time()
    task1 = asyncio.create_task(worker(4, 0.5))
    task2 = asyncio.create_task(worker(5, 0.5))
    task3 = asyncio.create_task(worker(6, 0.5))
    
    # Can do other work here while tasks run
    print("   Tasks created, doing other work...")
    await asyncio.sleep(0.2)
    print("   Other work done, now waiting for tasks...")
    
    # Wait for tasks to complete
    result1 = await task1
    result2 = await task2
    result3 = await task3
    print(f"   Completed in {time.time() - start:.2f}s")
    print(f"   Results: {result1}, {result2}, {result3}\n")
    
    # Method 3: TaskGroup (Python 3.11+)
    print("📋 Method 3: TaskGroup - Structured concurrency (Python 3.11+)")
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(worker(7, 0.3))
            tg.create_task(worker(8, 0.3))
            tg.create_task(worker(9, 0.3))
        print("   All tasks in group completed\n")
    except AttributeError:
        print("   TaskGroup not available (requires Python 3.11+)\n")


# ============================================================================
# TASK CANCELLATION
# ============================================================================

async def long_running_task(task_id: int):
    """A task that runs for a long time"""
    try:
        print(f"  Task {task_id} started (will run for 10s)")
        for i in range(10):
            await asyncio.sleep(1)
            print(f"  Task {task_id}: second {i+1}/10")
        print(f"  Task {task_id} completed naturally")
        return f"Task {task_id} success"
    except asyncio.CancelledError:
        print(f"  Task {task_id} was cancelled!")
        raise


async def demo_task_cancellation():
    """Demonstrate task cancellation"""
    print("\n" + "="*60)
    print("TASK CANCELLATION")
    print("="*60)
    
    print("\n⏹️  Creating a long-running task and cancelling it:")
    task = asyncio.create_task(long_running_task(1))
    
    # Let it run for 3 seconds
    await asyncio.sleep(3)
    
    # Cancel the task
    print("  Cancelling task...")
    task.cancel()
    
    # Wait for cancellation to complete
    try:
        await task
    except asyncio.CancelledError:
        print("  Task cancellation confirmed")


# ============================================================================
# TIMEOUTS
# ============================================================================

async def slow_operation(duration: float):
    """An operation that takes a long time"""
    print(f"  Starting slow operation ({duration}s)...")
    await asyncio.sleep(duration)
    print(f"  Slow operation completed")
    return "Operation result"


async def demo_timeouts():
    """Demonstrate timeout handling"""
    print("\n" + "="*60)
    print("TIMEOUT HANDLING")
    print("="*60)
    
    # Example 1: Operation completes within timeout
    print("\n⏱️  Example 1: Operation completes in time")
    try:
        result = await asyncio.wait_for(slow_operation(1.0), timeout=2.0)
        print(f"  ✅ Success: {result}\n")
    except asyncio.TimeoutError:
        print("  ❌ Operation timed out\n")
    
    # Example 2: Operation times out
    print("⏱️  Example 2: Operation times out")
    try:
        result = await asyncio.wait_for(slow_operation(3.0), timeout=1.0)
        print(f"  ✅ Success: {result}\n")
    except asyncio.TimeoutError:
        print("  ❌ Operation timed out after 1.0s\n")


# ============================================================================
# ERROR HANDLING IN ASYNC CODE
# ============================================================================

async def task_that_fails(task_id: int):
    """A task that might fail"""
    print(f"  Task {task_id} starting...")
    await asyncio.sleep(0.5)
    
    if task_id == 2:
        raise ValueError(f"Task {task_id} encountered an error!")
    
    print(f"  Task {task_id} completed")
    return f"Task {task_id} result"


async def demo_error_handling():
    """Demonstrate error handling in async code"""
    print("\n" + "="*60)
    print("ERROR HANDLING")
    print("="*60)
    
    # Example 1: gather with return_exceptions=False (default)
    print("\n🚨 Example 1: gather() without return_exceptions")
    print("   (First exception stops everything)")
    try:
        results = await asyncio.gather(
            task_that_fails(1),
            task_that_fails(2),  # This will fail
            task_that_fails(3)
        )
    except ValueError as e:
        print(f"   ❌ Caught exception: {e}\n")
    
    # Example 2: gather with return_exceptions=True
    print("🚨 Example 2: gather() with return_exceptions=True")
    print("   (All tasks complete, exceptions returned as results)")
    results = await asyncio.gather(
        task_that_fails(4),
        task_that_fails(5),  # This will fail
        task_that_fails(6),
        return_exceptions=True
    )
    
    for i, result in enumerate(results, start=4):
        if isinstance(result, Exception):
            print(f"   ❌ Task {i}: {result}")
        else:
            print(f"   ✅ Task {i}: {result}")


# ============================================================================
# EVENT LOOP INTROSPECTION
# ============================================================================

async def demo_event_loop_info():
    """Show information about the event loop"""
    print("\n" + "="*60)
    print("EVENT LOOP INTROSPECTION")
    print("="*60)
    
    loop = asyncio.get_event_loop()
    
    print(f"\n🔍 Event Loop Information:")
    print(f"   Running: {loop.is_running()}")
    print(f"   Closed: {loop.is_closed()}")
    
    # Create some tasks
    tasks = [
        asyncio.create_task(asyncio.sleep(0.1)),
        asyncio.create_task(asyncio.sleep(0.2)),
        asyncio.create_task(asyncio.sleep(0.3))
    ]
    
    print(f"\n📊 Current Tasks:")
    all_tasks = asyncio.all_tasks()
    print(f"   Total tasks: {len(all_tasks)}")
    
    # Wait for our tasks
    await asyncio.gather(*tasks)
    
    print("\n💡 Event Loop Concepts:")
    print("   - Event loop manages all async operations")
    print("   - Tasks are scheduled and executed by the loop")
    print("   - Loop switches between tasks during await points")
    print("   - Only one task runs at a time (cooperative multitasking)")


# ============================================================================
# PRACTICAL EXAMPLE: COORDINATED TASKS
# ============================================================================

async def producer(queue: asyncio.Queue, producer_id: int):
    """Produce items and put them in a queue"""
    for i in range(3):
        item = f"Producer-{producer_id}-Item-{i}"
        await queue.put(item)
        print(f"  📦 {item} produced")
        await asyncio.sleep(0.5)
    print(f"  ✅ Producer {producer_id} finished")


async def consumer(queue: asyncio.Queue, consumer_id: int):
    """Consume items from a queue"""
    while True:
        try:
            # Wait up to 2 seconds for an item
            item = await asyncio.wait_for(queue.get(), timeout=2.0)
            print(f"  🔧 Consumer-{consumer_id} processing {item}")
            await asyncio.sleep(0.3)
            queue.task_done()
        except asyncio.TimeoutError:
            print(f"  ⏹️  Consumer-{consumer_id} timed out, exiting")
            break


async def demo_coordinated_tasks():
    """Demonstrate coordinated async tasks with a queue"""
    print("\n" + "="*60)
    print("COORDINATED TASKS (Producer-Consumer)")
    print("="*60)
    
    queue = asyncio.Queue()
    
    # Create producers and consumers
    producers = [producer(queue, i) for i in range(2)]
    consumers = [consumer(queue, i) for i in range(3)]
    
    # Run all tasks
    print("\n🔄 Starting producers and consumers...")
    await asyncio.gather(
        *producers,
        *consumers,
        return_exceptions=True
    )
    
    print("\n✅ All producers and consumers finished")


# ============================================================================
# MAIN
# ============================================================================

async def main():
    """Run all demonstrations"""
    print("🔄 Event Loop Basics and Task Management\n")
    print("This example demonstrates core async concepts:")
    print("- How the event loop works")
    print("- Creating and managing tasks")
    print("- Cancellation and timeouts")
    print("- Error handling")
    
    await demo_event_loop_basics()
    await demo_task_creation()
    await demo_task_cancellation()
    await demo_timeouts()
    await demo_error_handling()
    await demo_event_loop_info()
    await demo_coordinated_tasks()
    
    print("\n" + "="*60)
    print("✅ All demonstrations completed!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
