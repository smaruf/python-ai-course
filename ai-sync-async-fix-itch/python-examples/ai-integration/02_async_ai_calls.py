#!/usr/bin/env python3
"""
Asynchronous AI API Calls
==========================

This example demonstrates asynchronous AI API calls for concurrent processing.
Ideal for web applications, batch processing, and high-throughput scenarios.
"""

import os
import asyncio
import aiohttp
import time
from typing import List, Dict, Optional


class AsyncAIClient:
    """Asynchronous AI client for concurrent operations"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "http://localhost:11434"):
        """
        Initialize async AI client
        
        Args:
            api_key: API key (not needed for Ollama)
            base_url: Base URL for API (default: Ollama local)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url
        self.is_ollama = "11434" in base_url or "ollama" in base_url.lower()
    
    async def generate_text(
        self,
        prompt: str,
        model: str = "llama3.1:8b",
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> Dict:
        """
        Generate text asynchronously
        
        Args:
            prompt: Input prompt
            model: Model name
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Dictionary with response and metadata
        """
        start_time = time.time()
        
        try:
            if self.is_ollama:
                response = await self._call_ollama(prompt, model)
            else:
                response = await self._call_openai(prompt, model, max_tokens, temperature)
            
            elapsed = time.time() - start_time
            
            return {
                "success": True,
                "response": response,
                "elapsed_time": elapsed,
                "model": model
            }
        
        except Exception as e:
            elapsed = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "elapsed_time": elapsed,
                "model": model
            }
    
    async def _call_ollama(self, prompt: str, model: str) -> str:
        """Call Ollama API asynchronously"""
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload) as response:
                response.raise_for_status()
                data = await response.json()
                return data["response"]
    
    async def _call_openai(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Call OpenAI API asynchronously"""
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                return data["choices"][0]["message"]["content"]


# ============================================================================
# EXAMPLE 1: Single Async Request
# ============================================================================

async def example_single_request():
    """Example: Single async AI request"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Single Asynchronous Request")
    print("="*60)
    
    client = AsyncAIClient()
    
    prompt = "Explain what an async function is in one sentence."
    print(f"\n📝 Prompt: {prompt}")
    
    result = await client.generate_text(prompt)
    
    if result["success"]:
        print(f"\n✅ Response: {result['response']}")
        print(f"⏱️  Time: {result['elapsed_time']:.2f}s")
    else:
        print(f"\n❌ Error: {result['error']}")


# ============================================================================
# EXAMPLE 2: Multiple Concurrent Requests
# ============================================================================

async def example_concurrent_requests():
    """Example: Multiple requests processed concurrently"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Multiple Concurrent Requests")
    print("="*60)
    
    client = AsyncAIClient()
    
    prompts = [
        "What is Python?",
        "What is async programming?",
        "What is an event loop?",
        "What is asyncio?",
        "What are coroutines?"
    ]
    
    print(f"\n📝 Processing {len(prompts)} prompts concurrently...")
    
    start_time = time.time()
    
    # Create all tasks
    tasks = [client.generate_text(prompt) for prompt in prompts]
    
    # Execute all concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    total_time = time.time() - start_time
    
    # Display results
    for i, (prompt, result) in enumerate(zip(prompts, results), 1):
        print(f"\n🔄 Request {i}/{len(prompts)}: {prompt}")
        
        if isinstance(result, Exception):
            print(f"   ❌ Error: {result}")
        elif result["success"]:
            response = result["response"][:100] + "..." if len(result["response"]) > 100 else result["response"]
            print(f"   ✅ {response}")
            print(f"   ⏱️  {result['elapsed_time']:.2f}s")
        else:
            print(f"   ❌ Failed: {result['error']}")
    
    print(f"\n📊 Summary:")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Average time per request: {total_time/len(prompts):.2f}s")
    successful = sum(1 for r in results if not isinstance(r, Exception) and r.get('success', False))
    print(f"   Successful: {successful}/{len(results)}")
    
    print(f"\n💡 Performance comparison:")
    print(f"   Sequential would take: ~{sum(r['elapsed_time'] for r in results if isinstance(r, dict) and r.get('success')):.2f}s")
    print(f"   Concurrent took: {total_time:.2f}s")
    speedup = sum(r['elapsed_time'] for r in results if isinstance(r, dict) and r.get('success', False)) / total_time if total_time > 0 else 0
    print(f"   Speedup: {speedup:.2f}x faster! 🚀")


# ============================================================================
# EXAMPLE 3: Batch Processing with Concurrency Limit
# ============================================================================

async def example_batch_with_limit():
    """Example: Batch processing with concurrency control"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Batch Processing with Concurrency Limit")
    print("="*60)
    
    client = AsyncAIClient()
    semaphore = asyncio.Semaphore(3)  # Max 3 concurrent requests
    
    topics = [
        "artificial intelligence",
        "machine learning",
        "neural networks",
        "deep learning",
        "natural language processing",
        "computer vision",
        "reinforcement learning",
        "transfer learning"
    ]
    
    async def process_with_limit(topic: str, index: int) -> Dict:
        """Process single topic with concurrency limit"""
        async with semaphore:
            prompt = f"Define {topic} in one sentence."
            print(f"[{index+1}/{len(topics)}] Processing: {topic}")
            return await client.generate_text(prompt)
    
    print(f"\n📝 Processing {len(topics)} topics with max 3 concurrent...")
    
    start_time = time.time()
    
    tasks = [process_with_limit(topic, i) for i, topic in enumerate(topics)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    total_time = time.time() - start_time
    
    successful = sum(1 for r in results if not isinstance(r, Exception) and r.get('success', False))
    
    print(f"\n📊 Batch Processing Summary:")
    print(f"   Total items: {len(topics)}")
    print(f"   Successful: {successful}")
    print(f"   Failed: {len(topics) - successful}")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Average per item: {total_time/len(topics):.2f}s")


# ============================================================================
# EXAMPLE 4: Error Handling with gather()
# ============================================================================

async def example_error_handling():
    """Example: Proper error handling in async operations"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Error Handling")
    print("="*60)
    
    client = AsyncAIClient()
    
    # Mix of valid and potentially failing requests
    prompts = [
        "What is Python?",
        "What is async?",
        "What is an event loop?"
    ]
    
    print("\n🔄 Processing requests with error handling...")
    
    tasks = [client.generate_text(prompt) for prompt in prompts]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    print("\n📊 Results:")
    for i, (prompt, result) in enumerate(zip(prompts, results), 1):
        if isinstance(result, Exception):
            print(f"   ❌ Request {i}: Exception - {result}")
        elif result.get("success"):
            print(f"   ✅ Request {i}: Success")
        else:
            print(f"   ❌ Request {i}: Failed - {result.get('error')}")


# ============================================================================
# EXAMPLE 5: Timeout Handling
# ============================================================================

async def example_timeout_handling():
    """Example: Adding timeouts to prevent hanging"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Timeout Handling")
    print("="*60)
    
    client = AsyncAIClient()
    
    async def fetch_with_timeout(prompt: str, timeout: float) -> Dict:
        """Fetch data with timeout"""
        try:
            result = await asyncio.wait_for(
                client.generate_text(prompt),
                timeout=timeout
            )
            return result
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": f"Request timed out after {timeout}s",
                "elapsed_time": timeout
            }
    
    # Test with different timeouts
    tests = [
        ("Quick response expected", 10.0),
        ("Another quick one", 10.0),
    ]
    
    print("\n🔄 Making requests with 10s timeout...")
    
    for prompt, timeout in tests:
        result = await fetch_with_timeout(prompt, timeout)
        
        if result["success"]:
            print(f"   ✅ Success: {prompt[:30]}...")
        else:
            print(f"   ❌ {result['error']}")


# ============================================================================
# EXAMPLE 6: Rate Limiting
# ============================================================================

async def example_rate_limiting():
    """Example: Rate limiting to respect API limits"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Rate Limiting")
    print("="*60)
    
    class RateLimitedClient:
        """Client with built-in rate limiting"""
        
        def __init__(self, client: AsyncAIClient, requests_per_minute: int = 10):
            self.client = client
            self.requests_per_minute = requests_per_minute
            self.request_times = []
        
        async def generate_text(self, prompt: str) -> Dict:
            """Generate text with rate limiting"""
            await self._wait_if_needed()
            return await self.client.generate_text(prompt)
        
        async def _wait_if_needed(self):
            """Wait if rate limit would be exceeded"""
            now = time.time()
            
            # Remove requests older than 1 minute
            self.request_times = [
                t for t in self.request_times
                if now - t < 60
            ]
            
            # If at limit, wait
            if len(self.request_times) >= self.requests_per_minute:
                sleep_time = 60 - (now - self.request_times[0])
                if sleep_time > 0:
                    print(f"   ⏳ Rate limit reached, waiting {sleep_time:.2f}s...")
                    await asyncio.sleep(sleep_time)
                    # Clean up again after sleep
                    now = time.time()
                    self.request_times = [
                        t for t in self.request_times
                        if now - t < 60
                    ]
            
            self.request_times.append(time.time())
    
    client = AsyncAIClient()
    rate_limited = RateLimitedClient(client, requests_per_minute=5)
    
    prompts = [f"Question {i}" for i in range(7)]
    
    print(f"\n📝 Making {len(prompts)} requests with rate limit of 5/minute...")
    
    start_time = time.time()
    tasks = [rate_limited.generate_text(f"What is {prompt}?") for prompt in prompts]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    total_time = time.time() - start_time
    
    successful = sum(1 for r in results if not isinstance(r, Exception) and r.get('success', False))
    print(f"\n   ✅ Completed {successful} requests in {total_time:.2f}s")


# ============================================================================
# EXAMPLE 7: Progress Tracking
# ============================================================================

async def example_progress_tracking():
    """Example: Track progress of multiple async operations"""
    print("\n" + "="*60)
    print("EXAMPLE 7: Progress Tracking")
    print("="*60)
    
    client = AsyncAIClient()
    
    topics = [f"topic_{i}" for i in range(10)]
    completed = 0
    
    async def process_with_progress(topic: str, index: int) -> Dict:
        """Process with progress updates"""
        nonlocal completed
        result = await client.generate_text(f"Explain {topic}")
        completed += 1
        progress = (completed / len(topics)) * 100
        print(f"   Progress: {completed}/{len(topics)} ({progress:.0f}%) - {topic}")
        return result
    
    print(f"\n📝 Processing {len(topics)} items with progress tracking...")
    
    tasks = [process_with_progress(topic, i) for i, topic in enumerate(topics)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    print(f"\n   ✅ All items processed!")


# ============================================================================
# PERFORMANCE COMPARISON
# ============================================================================

async def performance_comparison():
    """Compare sync vs async performance"""
    print("\n" + "="*60)
    print("PERFORMANCE COMPARISON: Async vs Sync")
    print("="*60)
    
    # Simulate the comparison
    num_requests = 5
    avg_request_time = 2.0
    
    print(f"\n📊 Scenario: {num_requests} AI API calls")
    print(f"   Average request time: {avg_request_time}s")
    
    print("\n⏱️  Synchronous (Sequential):")
    sync_time = num_requests * avg_request_time
    print(f"   Request 1: {'█' * 10} {avg_request_time}s")
    print(f"   Request 2: {'█' * 10} {avg_request_time}s")
    print(f"   Request 3: {'█' * 10} {avg_request_time}s")
    print(f"   Request 4: {'█' * 10} {avg_request_time}s")
    print(f"   Request 5: {'█' * 10} {avg_request_time}s")
    print(f"   Total: {sync_time}s")
    
    print("\n⚡ Asynchronous (Concurrent):")
    async_time = avg_request_time
    print("   Requests 1-5 (concurrent):")
    for i in range(1, 6):
        print(f"   Request {i}: {'█' * 10} {avg_request_time}s")
    print(f"   Total: ~{async_time}s")
    
    print(f"\n🚀 Performance Gain:")
    print(f"   Speedup: {sync_time/async_time:.1f}x faster")
    print(f"   Time saved: {sync_time - async_time:.1f}s ({((sync_time - async_time)/sync_time)*100:.0f}%)")


# ============================================================================
# MAIN
# ============================================================================

async def main():
    """Run all examples"""
    print("🔄 Asynchronous AI API Calls Examples\n")
    print("This demonstrates async AI integration patterns.")
    print("Async is ideal for: concurrent requests, web apps, high throughput")
    
    try:
        await example_single_request()
        await example_concurrent_requests()
        await example_batch_with_limit()
        await example_error_handling()
        await example_timeout_handling()
        await example_rate_limiting()
        await example_progress_tracking()
        await performance_comparison()
        
        print("\n" + "="*60)
        print("✅ All examples completed!")
        print("="*60)
        
        print("\n💡 Benefits of async AI calls:")
        print("   ✅ Process multiple requests concurrently")
        print("   ✅ Significant performance improvements")
        print("   ✅ Better resource utilization")
        print("   ✅ Ideal for web applications")
        print("   ✅ Handles high throughput efficiently")
        
        print("\n🎯 Best practices demonstrated:")
        print("   ✅ Concurrency control with semaphores")
        print("   ✅ Proper error handling with gather()")
        print("   ✅ Timeout management")
        print("   ✅ Rate limiting")
        print("   ✅ Progress tracking")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
