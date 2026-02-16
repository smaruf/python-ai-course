# System Building Interviews Module

## 🎯 Overview

This module addresses the **modern trend in technical interviews** where companies are shifting from pure algorithm puzzles (LeetCode-style) to **hands-on system implementation interviews**.

This format is much closer to real-world work and tests:
- ✅ System design thinking
- ✅ Concurrency and multithreading
- ✅ State management
- ✅ Data modeling
- ✅ Real-world tradeoffs

## 📊 The Industry Trend

Companies like **Oracle, Amazon, Google, Netflix, and Uber** are increasingly asking candidates to:

**Instead of:**
- Reverse a linked list
- Dynamic programming puzzles
- Array manipulation problems

**They now ask:**
- Build a web crawler
- Implement a rate limiter
- Design a mini database
- Build a scheduler
- Implement persistence with WAL

This tests engineers who have built **real systems** and understand **state, correctness, and concurrency**.

## 📚 Module Contents

This module contains **11 production-quality implementations** of system building challenges:

| Implementation | What It Tests | Key Concepts |
|----------------|--------------|--------------|
| **Web Crawler** | BFS, multithreading, synchronization | Thread-safe URL deduplication, concurrent crawling, respectful delays |
| **Rate Limiter** | Sliding window, token bucket, time handling | Token bucket, sliding window, fixed window, leaky bucket algorithms |
| **Chat App** | Client-server architecture, sockets, state | Message routing, room management, private messaging |
| **Banking System** | Transaction modeling, consistency | ACID properties, deadlock prevention, transaction isolation |
| **SQL Implementation** | Data modeling, query execution | Table schema, indexes, query filtering, data types |
| **Key-Value Store + WAL** | Persistence, durability, recovery | Write-ahead logging, crash recovery, compaction |
| **Kubernetes Scheduler** | Resource allocation logic | Pod scheduling, node selection, constraint satisfaction |
| **File System** | Tree structures, path resolution | Directory traversal, path normalization, operations |
| **Log Aggregator** | Ordering, binary search, streaming | Time-series data, efficient querying, log statistics |
| **Iterator/Snapshot** | Immutable data structures | Versioning, snapshot isolation, copy-on-write |
| **Functional Pipelines** | Lazy execution, functional composition | Map/filter/reduce, lazy evaluation, parallel processing |

## 🚀 Quick Start

### Installation

```bash
cd oracle-job-prep
pip install -r requirements.txt
```

### Usage Examples

#### 1. Web Crawler
```python
from src.system_building_interviews import WebCrawler

crawler = WebCrawler(max_depth=3, max_workers=5)
results = crawler.crawl("https://example.com")
print(f"Crawled {len(results)} pages")
```

#### 2. Rate Limiter
```python
from src.system_building_interviews import TokenBucketLimiter

limiter = TokenBucketLimiter(capacity=10, refill_rate=2)

for i in range(15):
    if limiter.allow_request("user123"):
        print(f"Request {i}: ALLOWED")
    else:
        print(f"Request {i}: RATE LIMITED")
```

#### 3. Chat Application
```python
from src.system_building_interviews import ChatServer, ChatClient

server = ChatServer()
server.start()

alice = ChatClient("Alice", server)
bob = ChatClient("Bob", server)

alice.send_message("Hello everyone!")
messages = bob.get_messages()
```

#### 4. Banking System
```python
from src.system_building_interviews import BankingSystem

bank = BankingSystem()

alice_account = bank.create_account("Alice", initial_balance=1000.0)
bob_account = bank.create_account("Bob", initial_balance=500.0)

# Transfer money (atomic operation)
bank.transfer("Alice", "Bob", 200.0, "Payment")

print(f"Alice balance: ${alice_account.get_balance()}")
print(f"Bob balance: ${bob_account.get_balance()}")
```

#### 5. SQL Engine
```python
from src.system_building_interviews import SQLEngine, Table, Column, ColumnType

db = SQLEngine()

# Create table
users = db.create_table("users", [
    Column("id", ColumnType.INTEGER, primary_key=True),
    Column("name", ColumnType.TEXT),
    Column("age", ColumnType.INTEGER)
])

# Insert data
users.insert({"id": 1, "name": "Alice", "age": 30})

# Query data
results = users.select(where=lambda row: row["age"] > 25)
```

#### 6. Key-Value Store with WAL
```python
from src.system_building_interviews import KeyValueStore

store = KeyValueStore("data.wal")

# Set values (persisted to disk)
store.set("user:1", {"name": "Alice", "age": 30})
store.set("counter", 100)

# Get values
user = store.get("user:1")

# Simulated crash and recovery
del store
recovered = KeyValueStore("data.wal")  # Recovers from WAL
```

#### 7. Kubernetes Scheduler
```python
from src.system_building_interviews import KubernetesScheduler, Node, Pod, Resources

scheduler = KubernetesScheduler()

# Add nodes
scheduler.add_node(Node(
    name="node-1",
    total_resources=Resources(cpu_millicores=4000, memory_mb=8192)
))

# Submit pod
scheduler.submit_pod(Pod(
    name="web-server",
    namespace="default",
    resource_requests=Resources(cpu_millicores=500, memory_mb=1024),
    resource_limits=Resources(cpu_millicores=1000, memory_mb=2048)
))

# Schedule pods
scheduled = scheduler.schedule_pending_pods()
```

#### 8. File System
```python
from src.system_building_interviews import FileSystem

fs = FileSystem()

# Create directories
fs.mkdir("/home/user")

# Create files
fs.create_file("/home/user/readme.txt", "Hello, World!")

# Read files
content = fs.read_file("/home/user/readme.txt")

# List directory
files = fs.list_directory("/home/user")
```

#### 9. Log Aggregator
```python
from src.system_building_interviews import LogAggregator, LogEntry, LogLevel
import time

aggregator = LogAggregator()

# Ingest logs
aggregator.ingest(LogEntry(
    timestamp=time.time(),
    level=LogLevel.INFO,
    source="web-server",
    message="Request processed"
))

# Query by time range
logs = aggregator.query_time_range(start_time, end_time)

# Get statistics
level_counts = aggregator.count_by_level()
```

#### 10. Iterator/Snapshot
```python
from src.system_building_interviews import ImmutableDataStructure, SnapshotIterator

data = ImmutableDataStructure({"name": "Alice", "age": 30})

# Modify (creates new version)
data.set("age", 31)
data.set("city", "NYC")

# Access old versions
original = data.snapshot(version=0)

# Iterate with snapshot isolation
iterator = SnapshotIterator(data, version=1)
for key, value in iterator:
    print(f"{key} = {value}")
```

#### 11. Functional Pipelines
```python
from src.system_building_interviews import LazyPipeline

# Lazy evaluation
result = (LazyPipeline(range(1, 100))
          .filter(lambda x: x % 2 == 0)
          .map(lambda x: x * x)
          .take(5)
          .to_list())
# [4, 16, 36, 64, 100]
```

## 💡 Why This Matters for Interviews

### For Backend/Distributed Systems Engineers

These problems **favor your experience** if you have:
- ✅ Built real production systems
- ✅ Worked with concurrency and state
- ✅ Designed for persistence and recovery
- ✅ Understood clean abstractions
- ✅ Reasoned about correctness

### What Companies Are Really Testing

| Traditional Algorithm Interview | Modern System Implementation |
|--------------------------------|------------------------------|
| Can you solve puzzles? | Can you build real systems? |
| Memorized patterns? | Understand tradeoffs? |
| Competitive programming? | Production experience? |
| Theoretical complexity? | Practical correctness? |

## 🎓 Interview Preparation Strategy

### 1. Master Core Concepts

For each implementation, understand:
- **Threading model**: How are race conditions prevented?
- **Data structures**: What structure is best and why?
- **Tradeoffs**: What are the performance characteristics?
- **Edge cases**: How are failures handled?
- **Testing**: How would you verify correctness?

### 2. Practice Implementation

Don't just read the code - implement from scratch:
1. Start with basic version
2. Add thread safety
3. Add persistence
4. Optimize performance
5. Handle edge cases

### 3. Discuss Design Decisions

Be prepared to explain:
- Why use this data structure?
- What are the time/space complexities?
- How does this scale?
- What are failure modes?
- How would you test this?

### 4. Know Common Patterns

| Pattern | Used In | Purpose |
|---------|---------|---------|
| Producer-Consumer | Chat App, Log Aggregator | Decouple components |
| Write-Ahead Log | KV Store, Banking | Durability |
| Thread-Safe Collections | Web Crawler, Rate Limiter | Concurrency |
| Copy-on-Write | Iterator/Snapshot | Immutability |
| Lazy Evaluation | Functional Pipeline | Performance |

## 🔧 Technical Deep Dives

### Concurrency Patterns

All implementations demonstrate thread-safe operations:

```python
# Example from Banking System
def transfer(self, from_account, to_account, amount):
    # Acquire locks in consistent order (prevent deadlock)
    first_lock = from_account.lock if from_account.id < to_account.id else to_account.lock
    second_lock = to_account.lock if from_account.id < to_account.id else from_account.lock
    
    with first_lock:
        with second_lock:
            # Atomic transfer
            from_account.balance -= amount
            to_account.balance += amount
```

### Persistence Patterns

Write-Ahead Logging ensures durability:

```python
# Example from KV Store
def set(self, key, value):
    # 1. Write to WAL first (durability)
    self.wal.append(OperationType.SET, key, value)
    
    # 2. Then update in-memory state
    self.data[key] = value
```

### Scheduling Algorithms

Resource-aware scheduling:

```python
# Example from K8s Scheduler
def _score_node(self, node, pod):
    # Score based on available resources
    available = node.available_resources()
    
    # Prefer less utilized nodes (load balancing)
    cpu_score = available.cpu / node.total.cpu
    mem_score = available.memory / node.total.memory
    
    return (cpu_score + mem_score) / 2
```

## 📖 Learning Path

### Week 1-2: Foundations
- [ ] Web Crawler - BFS and concurrency
- [ ] Rate Limiter - Time-based algorithms
- [ ] File System - Tree structures

### Week 3-4: State Management
- [ ] Banking System - ACID and transactions
- [ ] Chat App - Client-server architecture
- [ ] SQL Engine - Data modeling

### Week 5-6: Advanced Systems
- [ ] KV Store + WAL - Persistence and recovery
- [ ] K8s Scheduler - Resource allocation
- [ ] Log Aggregator - Time-series data

### Week 7-8: Advanced Patterns
- [ ] Iterator/Snapshot - Immutability
- [ ] Functional Pipelines - Lazy evaluation
- [ ] Integration and optimization

## 🧪 Testing

Each implementation includes example usage in `if __name__ == "__main__"` blocks.

Run individual examples:
```bash
python src/system_building_interviews/web_crawler.py
python src/system_building_interviews/rate_limiter.py
python src/system_building_interviews/banking_system.py
# ... etc
```

## 📝 Interview Tips

### During the Interview

1. **Clarify requirements** - Ask about scale, constraints, edge cases
2. **Start simple** - Basic working version first
3. **Iterate** - Add features incrementally
4. **Explain tradeoffs** - Discuss alternatives
5. **Test** - Think about edge cases and failures

### Common Questions to Expect

- "How would you make this thread-safe?"
- "What if the system crashes mid-operation?"
- "How would you scale this to millions of requests?"
- "What are the performance characteristics?"
- "How would you test this in production?"

## 🌟 Key Takeaways

This style of interview **rewards:**
- Engineers who have built real systems
- Understanding of state and consistency
- Knowledge of concurrency patterns
- Ability to reason about correctness
- Clean code and abstraction skills

**Not just:**
- Memorized algorithm patterns
- Competitive programming skills
- Theoretical CS knowledge

## 📚 Additional Resources

- **Books**:
  - *Designing Data-Intensive Applications* by Martin Kleppmann
  - *System Design Interview* by Alex Xu
  - *Database Internals* by Alex Petrov

- **Practice**:
  - Implement each system from scratch
  - Add your own features
  - Optimize for specific use cases
  - Write comprehensive tests

## 🤝 Contributing

Feel free to:
- Add new system implementations
- Improve existing code
- Add more test cases
- Share interview experiences

---

**Remember**: The goal is not to memorize implementations, but to **understand the patterns and principles** that make systems work in production.

Good luck with your interviews! 🚀
