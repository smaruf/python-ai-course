"""
Rate Limiter Implementation

Tests: Sliding window, token bucket, time handling, concurrency

Common rate limiting algorithms for API throttling and resource protection.
Demonstrates understanding of time-based algorithms and concurrent access control.
"""

from abc import ABC, abstractmethod
from collections import deque
from typing import Optional
import threading
import time


class RateLimiter(ABC):
    """Abstract base class for rate limiters."""
    
    @abstractmethod
    def allow_request(self, user_id: str) -> bool:
        """
        Check if a request should be allowed.
        
        Args:
            user_id: Unique identifier for the user/client
            
        Returns:
            True if request is allowed, False if rate limited
        """
        pass
    
    @abstractmethod
    def reset(self, user_id: str):
        """Reset rate limit for a user."""
        pass


class TokenBucketLimiter(RateLimiter):
    """
    Token Bucket Rate Limiter.
    
    Algorithm:
    - Each user has a bucket with a maximum capacity
    - Tokens are added at a constant rate
    - Each request consumes one token
    - Request is allowed if bucket has tokens available
    
    Advantages:
    - Allows burst traffic up to bucket capacity
    - Smooth rate limiting over time
    - Memory efficient
    """
    
    def __init__(
        self,
        capacity: int,
        refill_rate: float,
        refill_interval: float = 1.0
    ):
        """
        Initialize token bucket limiter.
        
        Args:
            capacity: Maximum number of tokens in bucket
            refill_rate: Number of tokens to add per interval
            refill_interval: Time interval for refilling (seconds)
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.refill_interval = refill_interval
        
        # User buckets: {user_id: (tokens, last_refill_time)}
        self.buckets = {}
        self.lock = threading.Lock()
    
    def allow_request(self, user_id: str) -> bool:
        """Check if request is allowed using token bucket algorithm."""
        with self.lock:
            current_time = time.time()
            
            # Initialize bucket if new user
            if user_id not in self.buckets:
                self.buckets[user_id] = (self.capacity - 1, current_time)
                return True
            
            tokens, last_refill = self.buckets[user_id]
            
            # Refill tokens based on elapsed time
            elapsed = current_time - last_refill
            refills = int(elapsed / self.refill_interval)
            
            if refills > 0:
                tokens = min(
                    self.capacity,
                    tokens + (refills * self.refill_rate)
                )
                last_refill = current_time
            
            # Check if we have tokens available
            if tokens > 0:
                tokens -= 1
                self.buckets[user_id] = (tokens, last_refill)
                return True
            
            # Rate limited
            self.buckets[user_id] = (tokens, last_refill)
            return False
    
    def reset(self, user_id: str):
        """Reset bucket for a user."""
        with self.lock:
            if user_id in self.buckets:
                del self.buckets[user_id]
    
    def get_tokens(self, user_id: str) -> int:
        """Get current token count for debugging."""
        with self.lock:
            if user_id not in self.buckets:
                return self.capacity
            tokens, _ = self.buckets[user_id]
            return int(tokens)


class SlidingWindowLimiter(RateLimiter):
    """
    Sliding Window Rate Limiter.
    
    Algorithm:
    - Maintains a window of request timestamps
    - Only counts requests within the time window
    - Removes old requests that fall outside window
    
    Advantages:
    - Precise rate limiting
    - No burst allowance (more strict)
    - Easy to understand and reason about
    
    Disadvantages:
    - Higher memory usage (stores all timestamps)
    - More computationally expensive
    """
    
    def __init__(self, max_requests: int, window_size: float):
        """
        Initialize sliding window limiter.
        
        Args:
            max_requests: Maximum requests allowed in window
            window_size: Time window size in seconds
        """
        self.max_requests = max_requests
        self.window_size = window_size
        
        # User request logs: {user_id: deque of timestamps}
        self.request_logs = {}
        self.lock = threading.Lock()
    
    def allow_request(self, user_id: str) -> bool:
        """Check if request is allowed using sliding window algorithm."""
        with self.lock:
            current_time = time.time()
            
            # Initialize log if new user
            if user_id not in self.request_logs:
                self.request_logs[user_id] = deque()
            
            request_log = self.request_logs[user_id]
            
            # Remove requests outside the window
            window_start = current_time - self.window_size
            while request_log and request_log[0] < window_start:
                request_log.popleft()
            
            # Check if we're under the limit
            if len(request_log) < self.max_requests:
                request_log.append(current_time)
                return True
            
            # Rate limited
            return False
    
    def reset(self, user_id: str):
        """Reset request log for a user."""
        with self.lock:
            if user_id in self.request_logs:
                del self.request_logs[user_id]
    
    def get_request_count(self, user_id: str) -> int:
        """Get current request count in window."""
        with self.lock:
            if user_id not in self.request_logs:
                return 0
            
            current_time = time.time()
            window_start = current_time - self.window_size
            
            # Count requests in window
            count = 0
            for timestamp in self.request_logs[user_id]:
                if timestamp >= window_start:
                    count += 1
            
            return count


class FixedWindowCounterLimiter(RateLimiter):
    """
    Fixed Window Counter Rate Limiter.
    
    Algorithm:
    - Divide time into fixed windows
    - Count requests per window
    - Reset counter at window boundary
    
    Advantages:
    - Very memory efficient
    - Simple to implement
    - Fast lookups
    
    Disadvantages:
    - Burst at window boundaries (can exceed limit)
    """
    
    def __init__(self, max_requests: int, window_size: float):
        """
        Initialize fixed window counter limiter.
        
        Args:
            max_requests: Maximum requests per window
            window_size: Window size in seconds
        """
        self.max_requests = max_requests
        self.window_size = window_size
        
        # User counters: {user_id: (count, window_start)}
        self.counters = {}
        self.lock = threading.Lock()
    
    def allow_request(self, user_id: str) -> bool:
        """Check if request is allowed using fixed window algorithm."""
        with self.lock:
            current_time = time.time()
            current_window = int(current_time / self.window_size)
            
            # Initialize or reset counter if new window
            if user_id not in self.counters:
                self.counters[user_id] = (1, current_window)
                return True
            
            count, window = self.counters[user_id]
            
            # Check if we're in a new window
            if current_window > window:
                self.counters[user_id] = (1, current_window)
                return True
            
            # Same window - check limit
            if count < self.max_requests:
                self.counters[user_id] = (count + 1, window)
                return True
            
            # Rate limited
            return False
    
    def reset(self, user_id: str):
        """Reset counter for a user."""
        with self.lock:
            if user_id in self.counters:
                del self.counters[user_id]


class LeakyBucketLimiter(RateLimiter):
    """
    Leaky Bucket Rate Limiter.
    
    Algorithm:
    - Requests are added to a queue (bucket)
    - Requests are processed at a constant rate (leak)
    - If bucket is full, new requests are rejected
    
    Advantages:
    - Smooths out bursty traffic
    - Constant output rate
    
    Disadvantages:
    - Adds latency (requests are queued)
    - Complex to implement with async processing
    """
    
    def __init__(
        self,
        capacity: int,
        leak_rate: float,
        leak_interval: float = 1.0
    ):
        """
        Initialize leaky bucket limiter.
        
        Args:
            capacity: Maximum bucket capacity
            leak_rate: Rate at which requests leak out
            leak_interval: Time interval for leaking
        """
        self.capacity = capacity
        self.leak_rate = leak_rate
        self.leak_interval = leak_interval
        
        # User buckets: {user_id: (level, last_leak_time)}
        self.buckets = {}
        self.lock = threading.Lock()
    
    def allow_request(self, user_id: str) -> bool:
        """Check if request is allowed using leaky bucket algorithm."""
        with self.lock:
            current_time = time.time()
            
            # Initialize bucket if new user
            if user_id not in self.buckets:
                self.buckets[user_id] = (1, current_time)
                return True
            
            level, last_leak = self.buckets[user_id]
            
            # Leak water based on elapsed time
            elapsed = current_time - last_leak
            leaks = int(elapsed / self.leak_interval)
            
            if leaks > 0:
                level = max(0, level - (leaks * self.leak_rate))
                last_leak = current_time
            
            # Check if we have capacity
            if level < self.capacity:
                level += 1
                self.buckets[user_id] = (level, last_leak)
                return True
            
            # Bucket is full
            self.buckets[user_id] = (level, last_leak)
            return False
    
    def reset(self, user_id: str):
        """Reset bucket for a user."""
        with self.lock:
            if user_id in self.buckets:
                del self.buckets[user_id]


if __name__ == "__main__":
    print("Rate Limiter Examples")
    print("=" * 60)
    
    # Token Bucket Example
    print("\n1. Token Bucket (10 tokens, refill 2/sec)")
    limiter = TokenBucketLimiter(capacity=10, refill_rate=2)
    
    for i in range(15):
        allowed = limiter.allow_request("user1")
        tokens = limiter.get_tokens("user1")
        print(f"  Request {i+1}: {'ALLOWED' if allowed else 'DENIED'} (tokens: {tokens})")
        time.sleep(0.1)
    
    # Sliding Window Example
    print("\n2. Sliding Window (5 requests per 2 seconds)")
    limiter = SlidingWindowLimiter(max_requests=5, window_size=2.0)
    
    for i in range(8):
        allowed = limiter.allow_request("user2")
        count = limiter.get_request_count("user2")
        print(f"  Request {i+1}: {'ALLOWED' if allowed else 'DENIED'} (count: {count})")
        time.sleep(0.3)
