# AI Development Best Practices

Production-ready patterns and practices for building robust AI applications.

## 🔐 Security Best Practices

### Input Validation and Sanitization

```python
import re
from typing import List

class InputValidator:
    """Secure input validation for AI applications"""
    
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script injection
        r'javascript:',                # JavaScript URLs
        r'eval\(',                     # Code evaluation
        r'exec\(',                     # Code execution
        r'import\s+',                  # Module imports
        r'__.*__',                     # Python dunder methods
    ]
    
    MAX_INPUT_LENGTH = 10000
    
    @classmethod
    def validate_user_input(cls, user_input: str) -> bool:
        """Validate user input for security"""
        
        # Length check
        if len(user_input) > cls.MAX_INPUT_LENGTH:
            return False
        
        # Pattern matching for dangerous content
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, user_input, re.IGNORECASE):
                return False
        
        return True
    
    @classmethod
    def sanitize_input(cls, user_input: str) -> str:
        """Sanitize user input"""
        # Remove potential HTML/script tags
        sanitized = re.sub(r'<[^>]+>', '', user_input)
        
        # Remove excessive whitespace
        sanitized = ' '.join(sanitized.split())
        
        # Truncate if too long
        if len(sanitized) > cls.MAX_INPUT_LENGTH:
            sanitized = sanitized[:cls.MAX_INPUT_LENGTH] + "..."
        
        return sanitized

# Usage example
user_input = "What is <script>alert('xss')</script> Python?"
if InputValidator.validate_user_input(user_input):
    processed_input = user_input
else:
    processed_input = InputValidator.sanitize_input(user_input)
```

### API Key Management

```python
import os
from typing import Optional
import logging

class SecureConfig:
    """Secure configuration management"""
    
    @staticmethod
    def get_api_key(service: str) -> Optional[str]:
        """Securely retrieve API keys"""
        key_name = f"{service.upper()}_API_KEY"
        api_key = os.getenv(key_name)
        
        if not api_key:
            logging.warning(f"API key not found for {service}")
            return None
        
        # Basic validation
        if len(api_key) < 10:
            logging.warning(f"API key for {service} seems too short")
            return None
        
        return api_key
    
    @staticmethod
    def validate_environment():
        """Validate required environment variables"""
        required_vars = ['OPENAI_API_KEY', 'DATABASE_URL']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise EnvironmentError(f"Missing required environment variables: {missing_vars}")
```

### Rate Limiting

```python
import time
import asyncio
from functools import wraps
from collections import defaultdict
from typing import Dict, Callable, Any

class RateLimiter:
    """Rate limiting for AI API calls"""
    
    def __init__(self, calls_per_minute: int = 60):
        self.calls_per_minute = calls_per_minute
        self.call_times: Dict[str, List[float]] = defaultdict(list)
    
    def is_allowed(self, user_id: str) -> bool:
        """Check if user is within rate limits"""
        now = time.time()
        user_calls = self.call_times[user_id]
        
        # Remove calls older than 1 minute
        user_calls[:] = [call_time for call_time in user_calls if now - call_time < 60]
        
        return len(user_calls) < self.calls_per_minute
    
    def record_call(self, user_id: str):
        """Record a new API call"""
        self.call_times[user_id].append(time.time())
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator for rate limiting"""
        @wraps(func)
        async def wrapper(*args, user_id: str = "default", **kwargs):
            if not self.is_allowed(user_id):
                raise Exception(f"Rate limit exceeded for user {user_id}")
            
            self.record_call(user_id)
            return await func(*args, **kwargs)
        
        return wrapper

# Usage
rate_limiter = RateLimiter(calls_per_minute=30)

@rate_limiter
async def ai_api_call(prompt: str, user_id: str = "default") -> str:
    # Your AI API call here
    return "AI response"
```

## 🚀 Performance Optimization

### Caching Strategies

```python
import hashlib
import json
import redis
from functools import wraps
from typing import Any, Callable, Optional

class AICache:
    """Intelligent caching for AI responses"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)
        self.default_ttl = 3600  # 1 hour
    
    def _generate_cache_key(self, prompt: str, model: str, params: dict) -> str:
        """Generate a unique cache key"""
        cache_data = {
            "prompt": prompt,
            "model": model,
            "params": params
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        return f"ai_cache:{hashlib.md5(cache_string.encode()).hexdigest()}"
    
    def get(self, prompt: str, model: str, params: dict) -> Optional[str]:
        """Get cached response"""
        cache_key = self._generate_cache_key(prompt, model, params)
        cached_response = self.redis_client.get(cache_key)
        
        if cached_response:
            return cached_response.decode('utf-8')
        return None
    
    def set(self, prompt: str, model: str, params: dict, response: str, ttl: int = None):
        """Cache AI response"""
        cache_key = self._generate_cache_key(prompt, model, params)
        self.redis_client.setex(
            cache_key, 
            ttl or self.default_ttl, 
            response
        )
    
    def cache_ai_call(self, ttl: int = None):
        """Decorator for caching AI calls"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(prompt: str, model: str = "default", **kwargs):
                # Try to get from cache
                cached_response = self.get(prompt, model, kwargs)
                if cached_response:
                    return cached_response
                
                # Call the actual function
                response = await func(prompt, model=model, **kwargs)
                
                # Cache the response
                self.set(prompt, model, kwargs, response, ttl)
                return response
            
            return wrapper
        return decorator

# Usage
cache = AICache()

@cache.cache_ai_call(ttl=1800)  # Cache for 30 minutes
async def cached_ai_call(prompt: str, model: str = "gpt-3.5-turbo", **kwargs) -> str:
    # Your expensive AI API call here
    return "AI response"
```

### Batch Processing

```python
import asyncio
from typing import List, Callable, Any, Dict
import logging

class BatchProcessor:
    """Efficient batch processing for AI operations"""
    
    def __init__(self, batch_size: int = 5, delay_between_batches: float = 0.1):
        self.batch_size = batch_size
        self.delay_between_batches = delay_between_batches
    
    async def process_batch(self, items: List[Any], processor: Callable) -> List[Any]:
        """Process items in batches to avoid overwhelming APIs"""
        results = []
        
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            
            # Process batch concurrently
            batch_tasks = [processor(item) for item in batch]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Handle results and exceptions
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    logging.error(f"Error processing item {i+j}: {result}")
                    results.append(None)
                else:
                    results.append(result)
            
            # Delay between batches
            if i + self.batch_size < len(items):
                await asyncio.sleep(self.delay_between_batches)
            
            logging.info(f"Processed batch {i//self.batch_size + 1}/{(len(items)-1)//self.batch_size + 1}")
        
        return results

# Usage example
async def process_document(doc: str) -> Dict[str, Any]:
    """Process a single document"""
    # Your document processing logic here
    await asyncio.sleep(0.5)  # Simulate processing time
    return {"processed": True, "length": len(doc)}

async def process_document_collection(documents: List[str]) -> List[Dict[str, Any]]:
    """Process a collection of documents efficiently"""
    processor = BatchProcessor(batch_size=3, delay_between_batches=0.2)
    return await processor.process_batch(documents, process_document)
```

## 📊 Monitoring and Observability

### Comprehensive Logging

```python
import logging
import time
import json
from functools import wraps
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class AIMetrics:
    """AI operation metrics"""
    operation_type: str
    model_name: str
    input_tokens: int
    output_tokens: int
    response_time: float
    success: bool
    error_message: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class AIMonitor:
    """Comprehensive AI monitoring and logging"""
    
    def __init__(self, log_level: int = logging.INFO):
        self.setup_logging(log_level)
        self.metrics_history: List[AIMetrics] = []
    
    def setup_logging(self, log_level: int):
        """Setup structured logging"""
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ai_application.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('AIApplication')
    
    def log_ai_operation(self, metrics: AIMetrics):
        """Log AI operation with structured data"""
        log_data = {
            'event_type': 'ai_operation',
            'metrics': asdict(metrics)
        }
        
        if metrics.success:
            self.logger.info(f"AI operation successful: {json.dumps(log_data)}")
        else:
            self.logger.error(f"AI operation failed: {json.dumps(log_data)}")
        
        # Store for analytics
        self.metrics_history.append(metrics)
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for the last N hours"""
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        recent_metrics = [
            m for m in self.metrics_history 
            if m.timestamp.timestamp() > cutoff_time
        ]
        
        if not recent_metrics:
            return {"message": "No recent metrics available"}
        
        successful_ops = [m for m in recent_metrics if m.success]
        failed_ops = [m for m in recent_metrics if not m.success]
        
        return {
            "total_operations": len(recent_metrics),
            "successful_operations": len(successful_ops),
            "failed_operations": len(failed_ops),
            "success_rate": len(successful_ops) / len(recent_metrics) if recent_metrics else 0,
            "average_response_time": sum(m.response_time for m in successful_ops) / len(successful_ops) if successful_ops else 0,
            "total_input_tokens": sum(m.input_tokens for m in recent_metrics),
            "total_output_tokens": sum(m.output_tokens for m in recent_metrics),
            "most_common_errors": self._get_common_errors(failed_ops)
        }
    
    def _get_common_errors(self, failed_ops: List[AIMetrics]) -> Dict[str, int]:
        """Get most common error types"""
        error_counts = {}
        for op in failed_ops:
            if op.error_message:
                error_type = op.error_message.split(':')[0]  # Get error type
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        return dict(sorted(error_counts.items(), key=lambda x: x[1], reverse=True))
    
    def monitor_ai_call(self, operation_type: str, model_name: str):
        """Decorator for monitoring AI calls"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    result = await func(*args, **kwargs)
                    response_time = time.time() - start_time
                    
                    # Estimate token usage (simplified)
                    input_tokens = self._estimate_tokens(str(args) + str(kwargs))
                    output_tokens = self._estimate_tokens(str(result))
                    
                    metrics = AIMetrics(
                        operation_type=operation_type,
                        model_name=model_name,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        response_time=response_time,
                        success=True
                    )
                    
                    self.log_ai_operation(metrics)
                    return result
                    
                except Exception as e:
                    response_time = time.time() - start_time
                    
                    metrics = AIMetrics(
                        operation_type=operation_type,
                        model_name=model_name,
                        input_tokens=0,
                        output_tokens=0,
                        response_time=response_time,
                        success=False,
                        error_message=str(e)
                    )
                    
                    self.log_ai_operation(metrics)
                    raise e
            
            return wrapper
        return decorator
    
    def _estimate_tokens(self, text: str) -> int:
        """Simple token estimation (roughly 4 characters per token)"""
        return len(text) // 4

# Usage
monitor = AIMonitor()

@monitor.monitor_ai_call("text_generation", "gpt-3.5-turbo")
async def generate_text(prompt: str) -> str:
    # Your AI call here
    return "Generated text response"
```

## 🔄 Error Handling and Resilience

### Retry Logic with Exponential Backoff

```python
import asyncio
import random
from functools import wraps
from typing import Callable, Any, List, Type
import logging

class RetryableError(Exception):
    """Base class for retryable errors"""
    pass

class RateLimitError(RetryableError):
    """Rate limit exceeded error"""
    pass

class TemporaryServiceError(RetryableError):
    """Temporary service unavailable error"""
    pass

def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: List[Type[Exception]] = None
):
    """Decorator for retry logic with exponential backoff"""
    
    if retryable_exceptions is None:
        retryable_exceptions = [RetryableError, ConnectionError, TimeoutError]
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                
                except Exception as e:
                    last_exception = e
                    
                    # Check if exception is retryable
                    if not any(isinstance(e, exc_type) for exc_type in retryable_exceptions):
                        logging.error(f"Non-retryable error in {func.__name__}: {e}")
                        raise e
                    
                    if attempt == max_retries:
                        logging.error(f"Max retries exceeded for {func.__name__}: {e}")
                        raise e
                    
                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (backoff_factor ** attempt), max_delay)
                    
                    # Add jitter to prevent thundering herd
                    if jitter:
                        delay *= (0.5 + random.random() * 0.5)
                    
                    logging.warning(f"Attempt {attempt + 1} failed for {func.__name__}, retrying in {delay:.2f}s: {e}")
                    await asyncio.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator

# Usage
@retry_with_backoff(
    max_retries=3,
    base_delay=1.0,
    retryable_exceptions=[RateLimitError, TemporaryServiceError]
)
async def unreliable_ai_call(prompt: str) -> str:
    # Your AI API call that might fail
    if random.random() < 0.3:  # 30% chance of failure
        raise RateLimitError("Rate limit exceeded")
    
    return "AI response"
```

### Circuit Breaker Pattern

```python
import time
from enum import Enum
from typing import Callable, Any
import asyncio

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit breaker triggered
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker:
    """Circuit breaker pattern for AI service calls"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        expected_exception: Type[Exception] = Exception
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN - service unavailable")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        return (
            self.last_failure_time and
            time.time() - self.last_failure_time >= self.timeout
        )
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Usage
ai_circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=30)

async def protected_ai_call(prompt: str) -> str:
    """AI call protected by circuit breaker"""
    
    async def actual_ai_call():
        # Your actual AI service call
        return "AI response"
    
    return await ai_circuit_breaker.call(actual_ai_call)
```

## 💰 Cost Management

### Token Usage Tracking

```python
import tiktoken
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    timestamp: datetime

class CostTracker:
    """Track and manage AI API costs"""
    
    # Pricing per 1K tokens (as of 2024)
    MODEL_PRICING = {
        "gpt-3.5-turbo": {"input": 0.001, "output": 0.002},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    }
    
    def __init__(self):
        self.usage_history: List[TokenUsage] = []
        self.encoders = {}
    
    def get_encoder(self, model: str):
        """Get or create token encoder for model"""
        if model not in self.encoders:
            try:
                self.encoders[model] = tiktoken.encoding_for_model(model)
            except KeyError:
                # Fallback to a generic encoder
                self.encoders[model] = tiktoken.get_encoding("cl100k_base")
        return self.encoders[model]
    
    def count_tokens(self, text: str, model: str = "gpt-3.5-turbo") -> int:
        """Count tokens in text for specific model"""
        encoder = self.get_encoder(model)
        return len(encoder.encode(text))
    
    def calculate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        """Calculate cost for token usage"""
        if model not in self.MODEL_PRICING:
            return 0.0  # Unknown model, can't calculate cost
        
        pricing = self.MODEL_PRICING[model]
        prompt_cost = (prompt_tokens / 1000) * pricing["input"]
        completion_cost = (completion_tokens / 1000) * pricing["output"]
        
        return prompt_cost + completion_cost
    
    def track_usage(self, prompt: str, completion: str, model: str):
        """Track token usage and cost"""
        prompt_tokens = self.count_tokens(prompt, model)
        completion_tokens = self.count_tokens(completion, model)
        total_tokens = prompt_tokens + completion_tokens
        cost = self.calculate_cost(prompt_tokens, completion_tokens, model)
        
        usage = TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost_usd=cost,
            timestamp=datetime.now()
        )
        
        self.usage_history.append(usage)
        return usage
    
    def get_usage_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get usage summary for the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_usage = [
            usage for usage in self.usage_history
            if usage.timestamp >= cutoff_date
        ]
        
        if not recent_usage:
            return {"message": f"No usage data for the last {days} days"}
        
        total_tokens = sum(usage.total_tokens for usage in recent_usage)
        total_cost = sum(usage.cost_usd for usage in recent_usage)
        
        return {
            "period_days": days,
            "total_requests": len(recent_usage),
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 4),
            "average_tokens_per_request": total_tokens // len(recent_usage),
            "average_cost_per_request": round(total_cost / len(recent_usage), 4),
            "daily_average_cost": round(total_cost / days, 4)
        }
    
    def set_budget_alert(self, daily_budget_usd: float) -> bool:
        """Check if daily budget is exceeded"""
        today = datetime.now().date()
        today_usage = [
            usage for usage in self.usage_history
            if usage.timestamp.date() == today
        ]
        
        today_cost = sum(usage.cost_usd for usage in today_usage)
        return today_cost >= daily_budget_usd

# Usage
cost_tracker = CostTracker()

async def cost_aware_ai_call(prompt: str, model: str = "gpt-3.5-turbo") -> str:
    """AI call with cost tracking"""
    
    # Check budget before call
    if cost_tracker.set_budget_alert(10.0):  # $10 daily budget
        raise Exception("Daily budget exceeded")
    
    # Make AI call (pseudo-code)
    completion = "AI response here"
    
    # Track usage
    usage = cost_tracker.track_usage(prompt, completion, model)
    print(f"Cost for this call: ${usage.cost_usd:.4f}")
    
    return completion
```

These best practices provide a solid foundation for building production-ready AI applications with proper security, performance, monitoring, and cost management. Always adapt these patterns to your specific use case and requirements.