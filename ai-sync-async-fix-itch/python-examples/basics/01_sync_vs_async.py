#!/usr/bin/env python3
"""
Synchronous vs Asynchronous Execution
======================================

This example demonstrates the fundamental difference between
synchronous and asynchronous code execution.
"""

import time
import asyncio


# ============================================================================
# SYNCHRONOUS APPROACH
# ============================================================================

def fetch_data_sync(source: str, delay: float) -> dict:
    """Simulate fetching data synchronously (blocking)"""
    print(f"[SYNC] Starting fetch from {source}...")
    time.sleep(delay)  # Blocking operation - simulates network I/O
    print(f"[SYNC] Completed fetch from {source}")
    return {"source": source, "data": f"Data from {source}"}


def process_sync():
    """Process multiple data sources synchronously"""
    print("\n" + "="*60)
    print("SYNCHRONOUS EXECUTION")
    print("="*60)
    
    start_time = time.time()
    
    # Each operation blocks until complete
    result1 = fetch_data_sync("API-1", 2.0)
    result2 = fetch_data_sync("API-2", 2.0)
    result3 = fetch_data_sync("API-3", 2.0)
    
    elapsed = time.time() - start_time
    
    print(f"\n✅ Completed in {elapsed:.2f} seconds")
    print(f"📊 Total wait time: 6.0 seconds (2 + 2 + 2)")
    return [result1, result2, result3]


# ============================================================================
# ASYNCHRONOUS APPROACH
# ============================================================================

async def fetch_data_async(source: str, delay: float) -> dict:
    """Simulate fetching data asynchronously (non-blocking)"""
    print(f"[ASYNC] Starting fetch from {source}...")
    await asyncio.sleep(delay)  # Non-blocking operation
    print(f"[ASYNC] Completed fetch from {source}")
    return {"source": source, "data": f"Data from {source}"}


async def process_async():
    """Process multiple data sources asynchronously"""
    print("\n" + "="*60)
    print("ASYNCHRONOUS EXECUTION")
    print("="*60)
    
    start_time = time.time()
    
    # All operations run concurrently
    results = await asyncio.gather(
        fetch_data_async("API-1", 2.0),
        fetch_data_async("API-2", 2.0),
        fetch_data_async("API-3", 2.0)
    )
    
    elapsed = time.time() - start_time
    
    print(f"\n✅ Completed in {elapsed:.2f} seconds")
    print(f"📊 Total wait time: ~2.0 seconds (max of concurrent operations)")
    return results


# ============================================================================
# COMPARISON
# ============================================================================

def compare_approaches():
    """Compare synchronous and asynchronous approaches"""
    print("\n" + "🔄 Comparing Synchronous vs Asynchronous Execution" + "\n")
    
    # Run synchronous version
    sync_start = time.time()
    sync_results = process_sync()
    sync_time = time.time() - sync_start
    
    # Run asynchronous version
    async_start = time.time()
    async_results = asyncio.run(process_async())
    async_time = time.time() - async_start
    
    # Display comparison
    print("\n" + "="*60)
    print("PERFORMANCE COMPARISON")
    print("="*60)
    print(f"Synchronous:  {sync_time:.2f}s  ⏳ (Sequential)")
    print(f"Asynchronous: {async_time:.2f}s  ⚡ (Concurrent)")
    print(f"Speedup:      {sync_time/async_time:.2f}x  🚀")
    print("="*60)
    
    # Visual representation
    print("\n📊 Visual Timeline:")
    print("\nSynchronous (Sequential):")
    print("API-1 ████████ (2s)")
    print("                API-2 ████████ (2s)")
    print("                                API-3 ████████ (2s)")
    print("Total: ~6 seconds")
    
    print("\nAsynchronous (Concurrent):")
    print("API-1 ████████ (2s)")
    print("API-2 ████████ (2s)")
    print("API-3 ████████ (2s)")
    print("Total: ~2 seconds")
    
    # Key takeaways
    print("\n💡 Key Takeaways:")
    print("1. Sync blocks execution - each operation waits for previous")
    print("2. Async allows concurrent execution - operations run together")
    print("3. For I/O-bound tasks, async can be significantly faster")
    print("4. Async is ideal for API calls, database queries, file I/O")


# ============================================================================
# DETAILED EXAMPLES
# ============================================================================

def example_cpu_bound():
    """Example showing sync is better for CPU-bound tasks"""
    print("\n" + "="*60)
    print("CPU-BOUND OPERATIONS (Better with Sync)")
    print("="*60)
    
    def fibonacci_sync(n):
        """Calculate fibonacci number (CPU-intensive)"""
        if n <= 1:
            return n
        return fibonacci_sync(n-1) + fibonacci_sync(n-2)
    
    start = time.time()
    result = fibonacci_sync(30)
    elapsed = time.time() - start
    
    print(f"Fibonacci(30) = {result}")
    print(f"Time: {elapsed:.2f}s")
    print("\n💡 CPU-bound tasks don't benefit from async")
    print("   because they're not waiting for I/O")


async def example_io_bound():
    """Example showing async is better for I/O-bound tasks"""
    print("\n" + "="*60)
    print("I/O-BOUND OPERATIONS (Better with Async)")
    print("="*60)
    
    async def simulated_api_call(api_id: int, delay: float):
        """Simulate an API call"""
        await asyncio.sleep(delay)
        return f"Response from API {api_id}"
    
    start = time.time()
    
    # Make 5 concurrent API calls
    results = await asyncio.gather(
        simulated_api_call(1, 1.0),
        simulated_api_call(2, 1.5),
        simulated_api_call(3, 0.8),
        simulated_api_call(4, 1.2),
        simulated_api_call(5, 0.9)
    )
    
    elapsed = time.time() - start
    
    print(f"Made 5 API calls in {elapsed:.2f}s")
    print("Sequential would take: 5.4s (1.0 + 1.5 + 0.8 + 1.2 + 0.9)")
    print(f"Async took: {elapsed:.2f}s (max = 1.5s)")
    print(f"Speedup: {5.4/elapsed:.2f}x")
    
    return results


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("🔄 Synchronous vs Asynchronous Programming Example\n")
    print("This example demonstrates the fundamental differences")
    print("between sync and async execution patterns.\n")
    
    # Main comparison
    compare_approaches()
    
    # Additional examples
    example_cpu_bound()
    asyncio.run(example_io_bound())
    
    print("\n" + "="*60)
    print("✅ Example completed!")
    print("="*60)
    print("\n📚 Learn More:")
    print("- Async is perfect for I/O-bound operations")
    print("- Sync is simpler for CPU-bound operations")
    print("- Choose based on your specific use case")
    print("="*60)
