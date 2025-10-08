# AI Integration Patterns: Sync and Async

## 📖 Overview

This guide covers specific patterns for integrating AI services (LLMs, embeddings, image generation, etc.) using both synchronous and asynchronous approaches. Learn when to use each approach and how to implement them effectively.

## 🎯 When to Use Sync vs Async for AI

### Use Synchronous AI Integration When:
- ✅ Building simple scripts or command-line tools
- ✅ Processing small datasets sequentially
- ✅ Working in environments that don't support async
- ✅ Prototyping and experimenting
- ✅ Educational or demo purposes

### Use Asynchronous AI Integration When:
- ✅ Building web applications or APIs
- ✅ Processing multiple requests concurrently
- ✅ Handling real-time user interactions
- ✅ Batch processing large datasets
- ✅ Integrating multiple AI services simultaneously

## 🔄 Pattern 1: Single AI Request

### Synchronous Implementation
```python
import requests
import os

class SyncAIClient:
    """Synchronous AI client for simple use cases"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1"
    
    def generate_text(self, prompt: str, model: str = "gpt-3.5-turbo") -> str:
        """Generate text synchronously"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

# Usage
if __name__ == "__main__":
    client = SyncAIClient(os.getenv("OPENAI_API_KEY"))
    result = client.generate_text("Explain quantum computing in simple terms")
    print(result)
```

### Asynchronous Implementation
```python
import aiohttp
import asyncio
import os

class AsyncAIClient:
    """Asynchronous AI client for concurrent use cases"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1"
    
    async def generate_text(
        self,
        prompt: str,
        model: str = "gpt-3.5-turbo"
    ) -> str:
        """Generate text asynchronously"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data["choices"][0]["message"]["content"]

# Usage
async def main():
    client = AsyncAIClient(os.getenv("OPENAI_API_KEY"))
    result = await client.generate_text("Explain quantum computing in simple terms")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

**When to Use**:
- **Sync**: Simple scripts, one-off queries, testing
- **Async**: Web servers, concurrent processing, multiple simultaneous requests

---

## 🔄 Pattern 2: Multiple Concurrent AI Requests

### Problem
Making multiple AI API calls sequentially wastes time and resources.

### Synchronous (Sequential)
```python
import time

def process_multiple_prompts_sync(prompts: list) -> list:
    """Process multiple prompts sequentially"""
    client = SyncAIClient(os.getenv("OPENAI_API_KEY"))
    results = []
    
    start = time.time()
    for prompt in prompts:
        result = client.generate_text(prompt)
        results.append(result)
    
    elapsed = time.time() - start
    print(f"Processed {len(prompts)} prompts in {elapsed:.2f}s")
    return results

# Usage
prompts = [
    "Explain AI in one sentence",
    "What is machine learning?",
    "Define neural networks",
]
results = process_multiple_prompts_sync(prompts)
# Time: ~9 seconds (3 seconds per request)
```

### Asynchronous (Concurrent)
```python
import asyncio
import time

async def process_multiple_prompts_async(prompts: list) -> list:
    """Process multiple prompts concurrently"""
    client = AsyncAIClient(os.getenv("OPENAI_API_KEY"))
    
    start = time.time()
    tasks = [client.generate_text(prompt) for prompt in prompts]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    elapsed = time.time() - start
    print(f"Processed {len(prompts)} prompts in {elapsed:.2f}s")
    return results

# Usage
async def main():
    prompts = [
        "Explain AI in one sentence",
        "What is machine learning?",
        "Define neural networks",
    ]
    results = await process_multiple_prompts_async(prompts)
    # Time: ~3 seconds (all concurrent)

asyncio.run(main())
```

**Performance Comparison**:
- Sync: 9 seconds (3 + 3 + 3)
- Async: 3 seconds (max of concurrent operations)
- **Speedup: 3x**

---

## 🔄 Pattern 3: Batch Processing with Rate Limiting

### Problem
Processing large datasets while respecting API rate limits.

### Implementation
```python
import asyncio
from typing import List, Dict
import time

class RateLimitedAIProcessor:
    """Process AI requests with rate limiting"""
    
    def __init__(
        self,
        api_key: str,
        requests_per_minute: int = 60,
        batch_size: int = 10
    ):
        self.client = AsyncAIClient(api_key)
        self.requests_per_minute = requests_per_minute
        self.batch_size = batch_size
        self.semaphore = asyncio.Semaphore(batch_size)
        self.request_times = []
    
    async def _rate_limit(self):
        """Implement rate limiting"""
        now = time.time()
        
        # Remove old requests (older than 1 minute)
        self.request_times = [
            t for t in self.request_times
            if now - t < 60
        ]
        
        # If at limit, wait
        if len(self.request_times) >= self.requests_per_minute:
            sleep_time = 60 - (now - self.request_times[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        self.request_times.append(time.time())
    
    async def process_single(self, prompt: str) -> Dict:
        """Process single prompt with rate limiting"""
        async with self.semaphore:
            await self._rate_limit()
            
            try:
                result = await self.client.generate_text(prompt)
                return {"prompt": prompt, "result": result, "error": None}
            except Exception as e:
                return {"prompt": prompt, "result": None, "error": str(e)}
    
    async def process_batch(self, prompts: List[str]) -> List[Dict]:
        """Process batch of prompts"""
        tasks = [self.process_single(prompt) for prompt in prompts]
        results = await asyncio.gather(*tasks)
        return results

# Usage
async def main():
    processor = RateLimitedAIProcessor(
        api_key=os.getenv("OPENAI_API_KEY"),
        requests_per_minute=60,
        batch_size=10
    )
    
    # Process 100 prompts with rate limiting
    prompts = [f"Summarize topic {i}" for i in range(100)]
    results = await processor.process_batch(prompts)
    
    # Analyze results
    successful = sum(1 for r in results if r["error"] is None)
    print(f"Processed {successful}/{len(prompts)} prompts successfully")

asyncio.run(main())
```

**Key Features**:
- Respects API rate limits automatically
- Processes items concurrently up to batch size
- Handles errors gracefully
- Returns detailed results

---

## 🔄 Pattern 4: Streaming AI Responses

### Problem
Long AI responses should stream to provide better UX.

### Synchronous Streaming
```python
import requests
import json

class SyncStreamingAIClient:
    """Sync AI client with streaming support"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1"
    
    def generate_stream(self, prompt: str):
        """Generate text with streaming"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "stream": True
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            stream=True
        )
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]
                    if data != '[DONE]':
                        try:
                            chunk = json.loads(data)
                            delta = chunk['choices'][0]['delta']
                            if 'content' in delta:
                                yield delta['content']
                        except json.JSONDecodeError:
                            continue

# Usage
client = SyncStreamingAIClient(os.getenv("OPENAI_API_KEY"))
for chunk in client.generate_stream("Write a short story"):
    print(chunk, end='', flush=True)
```

### Asynchronous Streaming
```python
import aiohttp
import asyncio
import json

class AsyncStreamingAIClient:
    """Async AI client with streaming support"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1"
    
    async def generate_stream(self, prompt: str):
        """Generate text with async streaming"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "stream": True
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        data = line[6:]
                        if data != '[DONE]':
                            try:
                                chunk = json.loads(data)
                                delta = chunk['choices'][0]['delta']
                                if 'content' in delta:
                                    yield delta['content']
                            except json.JSONDecodeError:
                                continue

# Usage
async def main():
    client = AsyncStreamingAIClient(os.getenv("OPENAI_API_KEY"))
    async for chunk in client.generate_stream("Write a short story"):
        print(chunk, end='', flush=True)

asyncio.run(main())
```

**Benefits**:
- Immediate feedback to users
- Better perceived performance
- Can display partial results
- Works great with async web frameworks

---

## 🔄 Pattern 5: Multi-Service AI Integration

### Problem
Using multiple AI services (embeddings, generation, analysis) concurrently.

### Implementation
```python
import asyncio
from typing import Dict, List

class MultiServiceAIClient:
    """Integrate multiple AI services"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1"
    
    async def get_embedding(self, text: str) -> List[float]:
        """Get text embedding"""
        # Simulated embedding call
        await asyncio.sleep(0.5)
        return [0.1] * 1536  # Mock embedding
    
    async def analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment"""
        # Simulated sentiment analysis
        await asyncio.sleep(0.3)
        return "positive"
    
    async def summarize(self, text: str) -> str:
        """Summarize text"""
        # Simulated summarization
        await asyncio.sleep(0.7)
        return f"Summary of: {text[:20]}..."
    
    async def extract_entities(self, text: str) -> List[str]:
        """Extract named entities"""
        # Simulated entity extraction
        await asyncio.sleep(0.4)
        return ["Entity1", "Entity2"]
    
    async def comprehensive_analysis(self, text: str) -> Dict:
        """Run all analyses concurrently"""
        results = await asyncio.gather(
            self.get_embedding(text),
            self.analyze_sentiment(text),
            self.summarize(text),
            self.extract_entities(text),
            return_exceptions=True
        )
        
        return {
            "embedding": results[0],
            "sentiment": results[1],
            "summary": results[2],
            "entities": results[3],
            "text": text
        }

# Usage
async def main():
    client = MultiServiceAIClient(os.getenv("OPENAI_API_KEY"))
    
    text = "Python is a high-level programming language..."
    analysis = await client.comprehensive_analysis(text)
    
    print(f"Sentiment: {analysis['sentiment']}")
    print(f"Summary: {analysis['summary']}")
    print(f"Entities: {', '.join(analysis['entities'])}")

asyncio.run(main())
```

**Performance**:
- Sequential: 0.5 + 0.3 + 0.7 + 0.4 = **1.9 seconds**
- Concurrent: max(0.5, 0.3, 0.7, 0.4) = **0.7 seconds**
- **Speedup: 2.7x**

---

## 🔄 Pattern 6: Caching AI Responses

### Problem
Repeated queries waste API calls and money.

### Implementation
```python
import asyncio
import hashlib
import json
from typing import Optional, Dict
import aioredis

class CachedAIClient:
    """AI client with caching support"""
    
    def __init__(self, api_key: str, redis_url: str = "redis://localhost"):
        self.client = AsyncAIClient(api_key)
        self.redis_url = redis_url
        self.cache_ttl = 3600  # 1 hour
    
    def _cache_key(self, prompt: str, model: str) -> str:
        """Generate cache key"""
        data = json.dumps({"prompt": prompt, "model": model}, sort_keys=True)
        return f"ai_cache:{hashlib.md5(data.encode()).hexdigest()}"
    
    async def generate_text_cached(
        self,
        prompt: str,
        model: str = "gpt-3.5-turbo"
    ) -> Dict:
        """Generate text with caching"""
        cache_key = self._cache_key(prompt, model)
        
        # Try to get from cache
        redis = await aioredis.create_redis_pool(self.redis_url)
        try:
            cached = await redis.get(cache_key)
            if cached:
                return {
                    "result": cached.decode('utf-8'),
                    "cached": True
                }
            
            # Generate if not cached
            result = await self.client.generate_text(prompt, model)
            
            # Store in cache
            await redis.setex(cache_key, self.cache_ttl, result)
            
            return {
                "result": result,
                "cached": False
            }
        finally:
            redis.close()
            await redis.wait_closed()

# Usage
async def main():
    client = CachedAIClient(os.getenv("OPENAI_API_KEY"))
    
    # First call - not cached
    result1 = await client.generate_text_cached("What is AI?")
    print(f"Result 1 - Cached: {result1['cached']}")  # False
    
    # Second call - cached
    result2 = await client.generate_text_cached("What is AI?")
    print(f"Result 2 - Cached: {result2['cached']}")  # True

asyncio.run(main())
```

**Benefits**:
- Reduces API costs
- Improves response time
- Handles repeated queries efficiently

---

## 🔄 Pattern 7: Retry with Exponential Backoff

### Problem
AI APIs can fail due to rate limits or temporary issues.

### Implementation
```python
import asyncio
import random
from typing import TypeVar, Callable

T = TypeVar('T')

async def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True
) -> T:
    """Retry async function with exponential backoff"""
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            last_exception = e
            
            if attempt == max_retries - 1:
                raise last_exception
            
            # Calculate delay with exponential backoff
            delay = min(base_delay * (exponential_base ** attempt), max_delay)
            
            # Add jitter to prevent thundering herd
            if jitter:
                delay *= (0.5 + random.random() * 0.5)
            
            print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s...")
            await asyncio.sleep(delay)
    
    raise last_exception

# Usage
async def unreliable_ai_call():
    """Simulated unreliable AI call"""
    if random.random() < 0.7:  # 70% failure rate
        raise Exception("Rate limit exceeded")
    return "Success!"

async def main():
    result = await retry_with_backoff(
        unreliable_ai_call,
        max_retries=5,
        base_delay=1.0
    )
    print(result)

asyncio.run(main())
```

**Retry Schedule**:
- Attempt 1: Immediate
- Attempt 2: Wait ~1 second
- Attempt 3: Wait ~2 seconds
- Attempt 4: Wait ~4 seconds
- Attempt 5: Wait ~8 seconds

---

## 📋 Pattern Selection Guide

| Use Case | Recommended Pattern | Sync/Async |
|----------|-------------------|------------|
| Single AI request in script | Pattern 1 | Sync |
| Single AI request in web app | Pattern 1 | Async |
| Multiple independent requests | Pattern 2 | Async |
| Large dataset processing | Pattern 3 | Async |
| Real-time chat interface | Pattern 4 | Async |
| Multiple AI services | Pattern 5 | Async |
| Repeated queries | Pattern 6 | Async |
| Unreliable API | Pattern 7 | Async |

## 🎓 Best Practices Summary

1. **Use Async for I/O**: AI API calls are I/O-bound, perfect for async
2. **Rate Limit**: Always implement rate limiting for API calls
3. **Cache Responses**: Cache when appropriate to save costs
4. **Handle Errors**: Use retry logic and proper error handling
5. **Stream When Possible**: Better UX for long-running operations
6. **Batch Process**: Group requests when API supports it
7. **Monitor Usage**: Track costs and performance metrics
8. **Test Thoroughly**: Test with various loads and error scenarios

## 🔗 Related Documentation

- [Best Practices](best-practices.md) - General async best practices
- [Common Pitfalls](common-pitfalls.md) - What to avoid
- Python examples in `python-examples/ai-integration/`
- C# examples in `csharp-examples/ai-integration/`
