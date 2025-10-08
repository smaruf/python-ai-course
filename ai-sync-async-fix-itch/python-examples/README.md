# Python Async Examples

Comprehensive Python examples demonstrating synchronous vs asynchronous programming patterns with AI integration.

## 📋 Prerequisites

- Python 3.8 or later
- pip for package management

## 🚀 Quick Start

### Setup

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run Examples

```bash
# Basic examples
python basics/01_sync_vs_async.py
python basics/02_event_loop_basics.py

# Problem demonstrations
python problems/01_common_mistakes.py

# AI integration
python ai-integration/01_sync_ai_calls.py
python ai-integration/02_async_ai_calls.py
```

## 📁 Directory Structure

### `basics/`
Core async concepts and fundamentals

- **01_sync_vs_async.py** - Compare sync and async execution
- **02_event_loop_basics.py** - Understanding the event loop, tasks, and coroutines

### `problems/`
Common mistakes and how to avoid them

- **01_common_mistakes.py** - Demonstrates 8 common async pitfalls with solutions

### `best-practices/`
Recommended patterns and implementations

- Proper async patterns
- Error handling strategies
- Resource management
- Concurrency control

### `ai-integration/`
Real-world AI integration examples

- **01_sync_ai_calls.py** - Synchronous AI API calls
- **02_async_ai_calls.py** - Asynchronous AI API calls with concurrency

## 💡 Key Concepts Covered

### Basics
- `async` and `await` keywords
- Coroutines vs regular functions
- Event loop mechanics
- `asyncio.gather()` for concurrent execution
- `asyncio.create_task()` for task management

### Common Mistakes
1. Forgetting to await async functions
2. Blocking the event loop with `time.sleep()`
3. Creating nested event loops
4. Not handling errors in `gather()`
5. Not closing resources properly
6. Race conditions with shared state
7. Not using timeouts
8. Not limiting concurrency

### Best Practices
- Using async context managers
- Proper error handling with `return_exceptions=True`
- Timeout management with `asyncio.wait_for()`
- Concurrency control with `asyncio.Semaphore()`
- Task cancellation
- Rate limiting for API calls

### AI Integration
- Single and batch AI requests
- Concurrent processing for performance
- Rate limiting to respect API limits
- Error handling and retries
- Progress tracking
- Caching responses

## 🎓 Learning Path

1. **Start with Basics** (`basics/01_sync_vs_async.py`)
   - Understand the fundamental differences
   - See performance comparisons

2. **Deep Dive into Event Loop** (`basics/02_event_loop_basics.py`)
   - Learn how asyncio works under the hood
   - Practice with tasks and coroutines

3. **Study Common Mistakes** (`problems/01_common_mistakes.py`)
   - Learn what can go wrong
   - See correct patterns side-by-side

4. **Apply to AI** (`ai-integration/`)
   - Start with sync approach (01)
   - Move to async for better performance (02)
   - Compare results

## 📊 Performance Examples

### Sequential (Sync)
```python
# 3 requests taking 2s each = 6s total
result1 = api_call()  # 2s
result2 = api_call()  # 2s
result3 = api_call()  # 2s
```

### Concurrent (Async)
```python
# 3 requests running concurrently = 2s total
results = await asyncio.gather(
    api_call(),  # \
    api_call(),  #  } All run together
    api_call()   # /
)
```

**Result**: 3x faster! 🚀

## 🔧 Troubleshooting

### "RuntimeWarning: coroutine was never awaited"
**Problem**: You called an async function without `await`

**Solution**:
```python
# Wrong
result = async_function()

# Correct
result = await async_function()
```

### "RuntimeError: asyncio.run() cannot be called from a running event loop"
**Problem**: Trying to create nested event loops

**Solution**: Just use `await` directly if already in async context

### Event loop is blocked
**Problem**: Using blocking operations like `time.sleep()`

**Solution**: Use `asyncio.sleep()` instead

## 🌐 Working with External APIs

### Local AI (Ollama)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama
ollama serve

# Pull a model
ollama pull llama3.1:8b
```

### OpenAI API
```bash
# Set API key
export OPENAI_API_KEY="your-key-here"
```

## 📚 Additional Resources

- [Python asyncio documentation](https://docs.python.org/3/library/asyncio.html)
- [Real Python async tutorial](https://realpython.com/async-io-python/)
- [aiohttp documentation](https://docs.aiohttp.org/)
- Main documentation in `../docs/`

## 🤝 Contributing

Examples should be:
- Self-contained and runnable
- Well-commented with explanations
- Demonstrate clear concepts
- Include both wrong and right patterns where applicable

## ⚡ Quick Tips

1. **Use async for I/O**: Network calls, file operations, database queries
2. **Use sync for CPU**: Heavy computations, data processing
3. **Always await**: Don't forget to await async functions
4. **Use asyncio.sleep()**: Never use `time.sleep()` in async code
5. **Handle errors**: Use `return_exceptions=True` in `gather()`
6. **Add timeouts**: Protect against hanging operations
7. **Limit concurrency**: Use semaphores to control concurrent operations
8. **Close resources**: Use async context managers (`async with`)

---

Happy async programming! 🚀
