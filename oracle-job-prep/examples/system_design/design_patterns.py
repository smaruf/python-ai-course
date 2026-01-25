"""
System Design Examples for Oracle Interview Preparation

This module demonstrates common system design patterns and solutions
frequently discussed in Oracle technical interviews.
"""

from typing import Dict, List, Optional, Any
from collections import OrderedDict
from datetime import datetime, timedelta
import time


class LRUCache:
    """
    Least Recently Used (LRU) Cache implementation.
    
    A cache that removes the least recently used items when capacity is reached.
    Used in: Database query caching, web browsers, CDNs
    
    Time Complexity: O(1) for get and put operations
    Space Complexity: O(capacity)
    """
    
    def __init__(self, capacity: int):
        """
        Initialize LRU cache with given capacity.
        
        Args:
            capacity: Maximum number of items in cache
        """
        self.cache = OrderedDict()
        self.capacity = capacity
    
    def get(self, key: int) -> int:
        """
        Get value from cache. Returns -1 if key doesn't exist.
        Marks key as recently used.
        """
        if key not in self.cache:
            return -1
        
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def put(self, key: int, value: int) -> None:
        """
        Put key-value pair in cache.
        Evicts least recently used item if at capacity.
        """
        if key in self.cache:
            # Update existing key
            self.cache.move_to_end(key)
        
        self.cache[key] = value
        
        if len(self.cache) > self.capacity:
            # Remove least recently used (first item)
            self.cache.popitem(last=False)


class RateLimiter:
    """
    Token Bucket Rate Limiter implementation.
    
    Limits the number of requests a user can make in a time window.
    Used in: API rate limiting, DDoS protection
    
    Algorithm: Token Bucket
    - Tokens are added to bucket at fixed rate
    - Each request consumes one token
    - Request denied if no tokens available
    """
    
    def __init__(self, max_tokens: int, refill_rate: float):
        """
        Initialize rate limiter.
        
        Args:
            max_tokens: Maximum number of tokens in bucket
            refill_rate: Tokens added per second
        """
        self.max_tokens = max_tokens
        self.refill_rate = refill_rate
        self.tokens = max_tokens
        self.last_refill = time.time()
    
    def _refill(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate
        
        self.tokens = min(self.max_tokens, self.tokens + tokens_to_add)
        self.last_refill = now
    
    def allow_request(self) -> bool:
        """
        Check if request is allowed.
        
        Returns:
            True if request allowed, False if rate limited
        """
        self._refill()
        
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        
        return False


class URLShortener:
    """
    URL Shortening Service (like bit.ly or tinyurl).
    
    Design considerations:
    - Generate unique short codes
    - Map short codes to long URLs
    - Handle collisions
    - Scale to billions of URLs
    
    This is a simplified in-memory version.
    Production would use distributed database (Redis, DynamoDB, etc.)
    """
    
    def __init__(self):
        self.url_to_code: Dict[str, str] = {}
        self.code_to_url: Dict[str, str] = {}
        self.counter = 0
        self.base62_chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    def _encode_base62(self, num: int) -> str:
        """Convert number to base62 string"""
        if num == 0:
            return self.base62_chars[0]
        
        result = []
        while num > 0:
            result.append(self.base62_chars[num % 62])
            num //= 62
        
        return ''.join(reversed(result))
    
    def shorten(self, long_url: str) -> str:
        """
        Shorten a long URL.
        
        Args:
            long_url: Original URL to shorten
            
        Returns:
            Short code for the URL
        """
        # Check if URL already shortened
        if long_url in self.url_to_code:
            return self.url_to_code[long_url]
        
        # Generate short code
        self.counter += 1
        short_code = self._encode_base62(self.counter)
        
        # Store mappings
        self.url_to_code[long_url] = short_code
        self.code_to_url[short_code] = long_url
        
        return short_code
    
    def expand(self, short_code: str) -> Optional[str]:
        """
        Expand short code to original URL.
        
        Args:
            short_code: Shortened URL code
            
        Returns:
            Original long URL or None if not found
        """
        return self.code_to_url.get(short_code)


class ConsistentHashing:
    """
    Consistent Hashing for distributed systems.
    
    Used for:
    - Load balancing across servers
    - Distributed caching (Redis, Memcached)
    - Database sharding
    
    Benefits:
    - Minimal data movement when nodes added/removed
    - Even distribution of keys
    """
    
    def __init__(self, nodes: List[str], virtual_nodes: int = 150):
        """
        Initialize consistent hashing ring.
        
        Args:
            nodes: List of node identifiers
            virtual_nodes: Number of virtual nodes per physical node
        """
        self.virtual_nodes = virtual_nodes
        self.ring: Dict[int, str] = {}
        self.sorted_keys: List[int] = []
        
        for node in nodes:
            self.add_node(node)
    
    def _hash(self, key: str) -> int:
        """Simple hash function (in production, use MD5/SHA1)"""
        return hash(key) % (2**32)
    
    def add_node(self, node: str) -> None:
        """Add a node to the hash ring"""
        for i in range(self.virtual_nodes):
            virtual_key = f"{node}:{i}"
            hash_value = self._hash(virtual_key)
            self.ring[hash_value] = node
        
        self.sorted_keys = sorted(self.ring.keys())
    
    def remove_node(self, node: str) -> None:
        """Remove a node from the hash ring"""
        for i in range(self.virtual_nodes):
            virtual_key = f"{node}:{i}"
            hash_value = self._hash(virtual_key)
            if hash_value in self.ring:
                del self.ring[hash_value]
        
        self.sorted_keys = sorted(self.ring.keys())
    
    def get_node(self, key: str) -> Optional[str]:
        """
        Get the node responsible for a given key.
        
        Args:
            key: Key to find node for
            
        Returns:
            Node identifier
        """
        if not self.ring:
            return None
        
        hash_value = self._hash(key)
        
        # Find first node with hash >= key's hash
        for ring_hash in self.sorted_keys:
            if ring_hash >= hash_value:
                return self.ring[ring_hash]
        
        # Wrap around to first node
        return self.ring[self.sorted_keys[0]]


class LoadBalancer:
    """
    Load Balancer with multiple strategies.
    
    Distributes incoming requests across multiple servers.
    
    Strategies:
    - Round Robin: Cycle through servers sequentially
    - Least Connections: Send to server with fewest active connections
    - Weighted Round Robin: Distribute based on server capacity
    """
    
    def __init__(self, servers: List[str]):
        self.servers = servers
        self.round_robin_index = 0
        self.connections: Dict[str, int] = {server: 0 for server in servers}
        self.weights: Dict[str, int] = {server: 1 for server in servers}
    
    def round_robin(self) -> str:
        """
        Round Robin strategy.
        Simple and fair distribution.
        """
        server = self.servers[self.round_robin_index]
        self.round_robin_index = (self.round_robin_index + 1) % len(self.servers)
        return server
    
    def least_connections(self) -> str:
        """
        Least Connections strategy.
        Send request to server with fewest active connections.
        """
        return min(self.connections.items(), key=lambda x: x[1])[0]
    
    def weighted_round_robin(self) -> str:
        """
        Weighted Round Robin strategy.
        Servers with higher weights receive more requests.
        """
        # Simple implementation: repeat servers based on weight
        weighted_servers = []
        for server in self.servers:
            weighted_servers.extend([server] * self.weights[server])
        
        server = weighted_servers[self.round_robin_index % len(weighted_servers)]
        self.round_robin_index += 1
        return server
    
    def set_weight(self, server: str, weight: int):
        """Set weight for a server (for weighted strategies)"""
        if server in self.weights:
            self.weights[server] = weight
    
    def increment_connections(self, server: str):
        """Increment connection count for a server"""
        if server in self.connections:
            self.connections[server] += 1
    
    def decrement_connections(self, server: str):
        """Decrement connection count for a server"""
        if server in self.connections and self.connections[server] > 0:
            self.connections[server] -= 1


class CircuitBreaker:
    """
    Circuit Breaker pattern for fault tolerance.
    
    Prevents cascading failures in distributed systems.
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Service unavailable, requests fail immediately
    - HALF_OPEN: Testing if service recovered
    
    Used in: Microservices, API calls, database connections
    """
    
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds before attempting to close circuit
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.state = self.CLOSED
        self.last_failure_time = None
    
    def call(self, func, *args, **kwargs):
        """
        Execute function through circuit breaker.
        
        Args:
            func: Function to execute
            *args, **kwargs: Function arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open
        """
        if self.state == self.OPEN:
            if self._should_attempt_reset():
                self.state = self.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        return (datetime.now() - self.last_failure_time).seconds >= self.timeout
    
    def _on_success(self):
        """Handle successful call"""
        self.failures = 0
        self.state = self.CLOSED
    
    def _on_failure(self):
        """Handle failed call"""
        self.failures += 1
        self.last_failure_time = datetime.now()
        
        if self.failures >= self.failure_threshold:
            self.state = self.OPEN


def demonstrate_system_designs():
    """Demonstrate all system design patterns"""
    
    print("System Design Patterns Demonstration")
    print("=" * 80)
    
    # LRU Cache
    print("\n1. LRU Cache")
    print("-" * 80)
    cache = LRUCache(3)
    cache.put(1, 1)
    cache.put(2, 2)
    cache.put(3, 3)
    print(f"   Added: 1->1, 2->2, 3->3")
    cache.put(4, 4)  # Evicts key 1
    print(f"   Added: 4->4 (evicts 1)")
    print(f"   Get key 2: {cache.get(2)}")
    print(f"   Get key 1: {cache.get(1)}")  # Returns -1 (not found)
    
    # Rate Limiter
    print("\n2. Rate Limiter (Token Bucket)")
    print("-" * 80)
    limiter = RateLimiter(max_tokens=3, refill_rate=1.0)  # 3 tokens, refill 1/sec
    print(f"   Request 1: {'Allowed' if limiter.allow_request() else 'Denied'}")
    print(f"   Request 2: {'Allowed' if limiter.allow_request() else 'Denied'}")
    print(f"   Request 3: {'Allowed' if limiter.allow_request() else 'Denied'}")
    print(f"   Request 4: {'Allowed' if limiter.allow_request() else 'Denied'}")
    
    # URL Shortener
    print("\n3. URL Shortener")
    print("-" * 80)
    shortener = URLShortener()
    short1 = shortener.shorten("https://www.oracle.com/careers")
    short2 = shortener.shorten("https://docs.oracle.com/database")
    print(f"   Shortened: https://www.oracle.com/careers -> {short1}")
    print(f"   Shortened: https://docs.oracle.com/database -> {short2}")
    print(f"   Expanded {short1}: {shortener.expand(short1)}")
    
    # Consistent Hashing
    print("\n4. Consistent Hashing")
    print("-" * 80)
    nodes = ["server1", "server2", "server3"]
    ch = ConsistentHashing(nodes)
    print(f"   Nodes: {nodes}")
    for key in ["user:1001", "user:1002", "user:1003"]:
        print(f"   Key '{key}' -> {ch.get_node(key)}")
    
    # Load Balancer
    print("\n5. Load Balancer")
    print("-" * 80)
    lb = LoadBalancer(["server1", "server2", "server3"])
    print("   Round Robin:")
    for i in range(5):
        print(f"      Request {i+1} -> {lb.round_robin()}")
    
    # Circuit Breaker
    print("\n6. Circuit Breaker")
    print("-" * 80)
    cb = CircuitBreaker(failure_threshold=3, timeout=5)
    print(f"   Initial state: {cb.state}")
    
    def failing_service():
        raise Exception("Service unavailable")
    
    # Simulate failures
    for i in range(3):
        try:
            cb.call(failing_service)
        except Exception:
            print(f"   Failure {i+1}, State: {cb.state}")
    
    print(f"   Final state: {cb.state}")


if __name__ == "__main__":
    demonstrate_system_designs()
