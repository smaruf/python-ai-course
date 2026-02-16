# System Building Interview Keywords - Quick Reference

## Alphabetically Sorted Keywords by Category

### A
- **ACID** (Banking, SQL): Atomicity, Consistency, Isolation, Durability
- **Affinity** (K8s Scheduler): Pod placement preferences
- **Aggregation** (Log Aggregator): Combining data from multiple sources
- **Atomic operations** (General): Indivisible operations
- **Atomicity** (Banking): All-or-nothing transaction execution
- **At-least-once delivery** (Chat): Message delivery guarantee
- **Availability** (Distributed): System uptime guarantee

### B
- **B-tree** (SQL): Balanced tree for indexing
- **Backoff, Exponential** (Web Crawler): Retry delay strategy
- **BFS (Breadth-First Search)** (Web Crawler): Level-by-level traversal
- **Binary search** (Log Aggregator): O(log n) search algorithm
- **Bin packing** (K8s Scheduler): Resource allocation problem
- **Bloom filter** (General): Probabilistic data structure
- **Broadcast** (Chat): Send to all recipients
- **Buffering** (Log Aggregator): Temporary storage

### C
- **CAP theorem** (Distributed): Consistency, Availability, Partition tolerance
- **Caching** (General): Fast temporary storage
- **Checkpoint** (KV Store): Point-in-time snapshot
- **Client-server** (Chat): Communication architecture
- **Compaction** (KV Store): Log size reduction
- **Composition** (Functional): Combining operations
- **Concurrency** (General): Parallel execution
- **Condition variable** (Threading): Synchronization primitive
- **Consensus** (Distributed): Agreement protocol
- **Consistency** (Banking): Data validity guarantee
- **Constraint satisfaction** (K8s): Meeting requirements
- **Copy-on-write** (Iterator): Immutable update strategy
- **Crash recovery** (KV Store): Restoring state after failure

### D
- **Deadlock** (Banking): Circular wait condition
- **Deduplication** (Web Crawler): Removing duplicates
- **Deferred execution** (Functional): Lazy evaluation
- **DFS (Depth-First Search)** (General): Deep-first traversal
- **Directory traversal** (File System): Walking directory tree
- **Distributed systems** (General): Multi-node systems
- **Durability** (KV Store): Persistence guarantee
- **Dynamic programming** (Algorithms): Optimization technique

### E
- **Early termination** (Functional): Stop processing early
- **Error handling** (General): Dealing with failures
- **Event loop** (General): Asynchronous execution
- **Eventual consistency** (Distributed): Delayed convergence
- **Exponential backoff** (Web Crawler): Retry delay

### F
- **Fair scheduling** (K8s): Equitable resource distribution
- **Fault tolerance** (General): Handling failures
- **Filter** (Functional): Selecting elements
- **Fixed window** (Rate Limiter): Time-based counter
- **Flat map** (Functional): Transform and flatten
- **Fsync** (KV Store): Force disk write

### G
- **Gang scheduling** (K8s): Scheduling related pods together
- **Garbage collection** (Iterator): Removing unused data
- **Generator** (Functional): Lazy sequence producer

### H
- **Hash index** (SQL): O(1) lookup structure
- **Hash map** (General): Key-value data structure
- **Heartbeat** (Chat): Connection health check
- **Higher-order functions** (Functional): Functions on functions
- **HNSW** (Vector search): Hierarchical Navigable Small World

### I
- **Idempotency** (General): Same result on repeat
- **Immutability** (Iterator): Unchangeable data
- **Index** (SQL): Fast lookup structure
- **Inode** (File System): File metadata structure
- **Isolation** (Banking): Transaction independence
- **Iterator** (Functional): Sequential access pattern
- **IVF** (Vector search): Inverted file index

### J
- **JOIN** (SQL): Combining tables

### K
- **Key-value store** (General): Simple database

### L
- **Lazy evaluation** (Functional): Deferred computation
- **Leaky bucket** (Rate Limiter): Constant rate output
- **Load balancing** (Distributed): Distributing work
- **Lock** (Threading): Mutual exclusion primitive
- **Log compaction** (KV Store): Reducing log size

### M
- **Map** (Functional): Transform operation
- **Memory-mapped files** (KV Store): Efficient I/O
- **Message queue** (Chat): Buffered communication
- **Multi-version concurrency control (MVCC)** (Iterator): Version-based isolation
- **Mutex** (Threading): Mutual exclusion lock
- **Multithreading** (Web Crawler): Concurrent execution

### N
- **Node selector** (K8s): Node filtering criterion
- **Normalization** (Web Crawler): URL standardization

### O
- **Ordered locking** (Banking): Deadlock prevention
- **Out-of-order** (Log Aggregator): Unordered arrival
- **Overdraft** (Banking): Negative balance allowance

### P
- **Parallel execution** (Functional): Concurrent processing
- **Partitioning** (Distributed): Data division
- **Path resolution** (File System): Converting path to node
- **Persistence** (KV Store): Durable storage
- **Predicate pushdown** (SQL): Early filtering
- **Preemption** (K8s): Evicting lower priority
- **Primary key** (SQL): Unique identifier
- **Priority queue** (K8s): Ordered task queue
- **Producer-consumer** (General): Async pattern
- **Publish-subscribe** (Chat): Messaging pattern

### Q
- **Query execution** (SQL): Running queries
- **Query planning** (SQL): Optimization strategy
- **Queue** (General): FIFO data structure

### R
- **Race condition** (Threading): Uncontrolled concurrent access
- **Rate limiting** (Rate Limiter): Request throttling
- **Read-write lock** (File System): Concurrent read lock
- **Recovery** (KV Store): Restoring state
- **Reduce** (Functional): Aggregation operation
- **Redo log** (KV Store): Replay log
- **Refill rate** (Rate Limiter): Token generation rate
- **Replication** (Distributed): Data copying
- **Resilience** (General): Fault recovery
- **Resource allocation** (K8s): Assigning resources
- **Retry logic** (Web Crawler): Failure recovery
- **Robots.txt** (Web Crawler): Crawling rules
- **Rollback** (Banking): Transaction undo
- **Round-robin** (K8s): Fair distribution

### S
- **Scalability** (General): Growth handling
- **Scheduling** (K8s): Resource assignment
- **Schema** (SQL): Data structure definition
- **Scoring** (K8s): Node ranking
- **Semaphore** (Threading): Counting lock
- **Serializable isolation** (Banking): Strictest isolation
- **Sharding** (Distributed): Horizontal partitioning
- **Sliding window** (Rate Limiter): Moving time window
- **Snapshot** (Iterator): Point-in-time copy
- **Snapshot isolation** (Iterator): Version-based reads
- **State management** (Chat): Tracking state
- **Streaming** (Log Aggregator): Continuous processing
- **Structural sharing** (Iterator): Shared data structures
- **Synchronization** (Web Crawler): Coordinating threads
- **Symbolic link** (File System): Reference to another file

### T
- **Taints/Tolerations** (K8s): Node restrictions
- **Thread pool** (Web Crawler): Reusable threads
- **Thread-safe** (General): Safe concurrent access
- **Time-series data** (Log Aggregator): Timestamped data
- **Token bucket** (Rate Limiter): Rate limiting algorithm
- **Transaction** (Banking): Atomic operation group
- **Transaction log** (Banking): Audit trail
- **Tree structure** (File System): Hierarchical organization
- **Two-phase locking** (Banking): Locking protocol

### U
- **URL normalization** (Web Crawler): Standardizing URLs

### V
- **Versioning** (Iterator): Multiple versions
- **Virtual file system** (File System): Abstract filesystem

### W
- **WAL (Write-Ahead Logging)** (KV Store): Durability pattern
- **WebSocket** (Chat): Persistent connection
- **WHERE clause** (SQL): Filter condition
- **Worker thread** (Web Crawler): Processing thread
- **Write-ahead log** (KV Store): Persistence mechanism

---

## Keywords by System Building Topic

### 1. Web Crawler (20 keywords)
BFS, Breadth-First Search, concurrent data structures, deduplication, distributed systems, DNS, error handling, exponential backoff, multithreading, producer-consumer, race condition, resilience, retry logic, robots.txt, synchronization, thread pool, thread-safe, timeout, URL normalization, worker thread

### 2. Rate Limiter (18 keywords)
atomic operations, distributed systems, eventual consistency, fixed window, leaky bucket, rate limiting, Redis, refill rate, sliding window, time-based algorithms, token bucket, concurrency, consensus, clock skew, fairness, throttling, backpressure, quota

### 3. Chat Application (17 keywords)
at-least-once delivery, broadcast, client-server, connection management, event loop, heartbeat, message queue, persistence, private messaging, publish-subscribe, real-time communication, session affinity, state management, WebSocket, message routing, inbox, room management

### 4. Banking System (22 keywords)
ACID, atomicity, audit trail, consistency, deadlock, deadlock prevention, durability, isolation, ordered locking, overdraft, rollback, serializable isolation, transaction, transaction log, two-phase locking, balance invariant, concurrent access, financial systems, idempotency, mutex, race condition, thread-safe

### 5. SQL Engine (19 keywords)
B-tree, column-oriented, constraint satisfaction, data modeling, hash index, index, inode, JOIN, predicate pushdown, primary key, query execution, query planning, row-oriented, schema, schema design, table scan, unique constraint, WHERE clause, indexing

### 6. Key-Value Store with WAL (21 keywords)
append-only, checkpoint, compaction, crash recovery, durability, fsync, log compaction, memory-mapped files, persistence, redo log, recovery, snapshot, storage tiers, transaction log, WAL, write-ahead logging, atomic writes, batch writes, consistency guarantees, log replay, ordering

### 7. Kubernetes Scheduler (20 keywords)
affinity, bin packing, constraint satisfaction, fair scheduling, gang scheduling, load balancing, multi-dimensional optimization, node selector, preemption, priority queue, resource allocation, round-robin, scheduling algorithms, scoring, taints, tolerations, pod distribution, resource fragmentation, overcommitment, eviction

### 8. File System (18 keywords)
directory traversal, hard link, inode, path normalization, path resolution, permissions, quotas, read-write lock, symbolic link, tree structure, virtual file system, atomic operations, metadata, file operations, concurrent access, cache, lazy loading, reference counting

### 9. Log Aggregator (20 keywords)
aggregation, binary search, bloom filter, buffering, compression, indexing, out-of-order, partitioning, sharding, storage tiers, streaming, time-series data, fan-out, full-text search, hot/warm/cold storage, ingestion rate, log retention, query latency, real-time alerting, windowing

### 10. Iterator/Snapshot (17 keywords)
copy-on-write, garbage collection, immutability, MVCC, multi-version concurrency control, optimistic locking, pessimistic locking, snapshot, snapshot isolation, structural sharing, time-travel, versioning, concurrent access, reference counting, version control, undo/redo, consistent view

### 11. Functional Pipelines (18 keywords)
composition, deferred execution, early termination, filter, flat map, functional programming, generator, higher-order functions, infinite sequences, iterator, lazy evaluation, map, parallel execution, pipeline, reduce, streaming, eager evaluation, method chaining

---

## Must-Know Keywords for All Topics

### Concurrency (8 keywords)
- **atomicity**: Indivisible operations
- **concurrency**: Parallel execution
- **deadlock**: Circular wait condition
- **lock**: Mutual exclusion primitive
- **mutex**: Mutual exclusion lock
- **race condition**: Uncontrolled concurrent access
- **synchronization**: Coordinating threads
- **thread-safe**: Safe concurrent access

### Distributed Systems (7 keywords)
- **availability**: System uptime
- **CAP theorem**: Consistency/Availability/Partition tolerance
- **consensus**: Agreement protocol
- **consistency**: Data validity
- **eventual consistency**: Delayed convergence
- **partition tolerance**: Network failure handling
- **replication**: Data copying

### Performance (6 keywords)
- **caching**: Fast temporary storage
- **indexing**: Fast lookup structure
- **load balancing**: Distributing work
- **partitioning**: Data division
- **scalability**: Growth handling
- **sharding**: Horizontal partitioning

### Data Structures (8 keywords)
- **B-tree**: Balanced tree for indexing
- **hash map**: Key-value structure
- **heap**: Priority queue structure
- **queue**: FIFO structure
- **stack**: LIFO structure
- **tree**: Hierarchical structure
- **trie**: Prefix tree
- **bloom filter**: Probabilistic structure

### Algorithms (6 keywords)
- **BFS**: Breadth-first search
- **binary search**: O(log n) search
- **DFS**: Depth-first search
- **dynamic programming**: Optimization
- **hashing**: Key mapping
- **sorting**: Ordering elements

---

## Interview Response Template

When answering, structure your response:

1. **Define the problem** (use keywords)
   - "This is about [CONCURRENCY/PERSISTENCE/DISTRIBUTION]"
   - "Key challenges are [KEYWORD1, KEYWORD2, KEYWORD3]"

2. **Explain your approach** (use keywords)
   - "I'll use [ALGORITHM/DATA STRUCTURE]"
   - "To handle [CONCURRENCY], I'll use [LOCKS/ATOMICS]"

3. **Discuss tradeoffs** (compare keywords)
   - "[APPROACH1] vs [APPROACH2]"
   - "Trade [CONSISTENCY] for [AVAILABILITY]"

4. **Handle edge cases** (use keywords)
   - "For [RACE CONDITIONS], I'll use [SYNCHRONIZATION]"
   - "For [FAILURES], I'll implement [RETRY LOGIC]"

---

## Keyword Frequency

**Most Important Keywords** (mentioned 5+ times):
- **Concurrency** (11 topics)
- **Thread-safe** (10 topics)
- **Distributed systems** (9 topics)
- **Persistence** (7 topics)
- **Indexing** (6 topics)
- **Consistency** (6 topics)
- **Atomicity** (6 topics)

**High-Value Keywords** (3-4 topics):
- Lock, Race condition, Transaction
- Partitioning, Sharding, Replication
- Binary search, Hash map, Tree

**Specialized Keywords** (1-2 topics):
- WAL, MVCC, BFS
- Token bucket, Sliding window
- Snapshot isolation

---

## Quick Lookup by Scenario

**"How do you ensure thread safety?"**
→ locks, mutex, atomic operations, synchronization, thread-safe collections, race condition prevention

**"How do you handle failures?"**
→ retry logic, exponential backoff, error handling, fault tolerance, resilience, rollback

**"How do you persist data?"**
→ WAL, fsync, durability, persistence, checkpoint, crash recovery

**"How do you scale the system?"**
→ sharding, partitioning, replication, distributed systems, load balancing, horizontal scaling

**"How do you optimize performance?"**
→ indexing, caching, binary search, lazy evaluation, parallel execution, buffering

**"How do you ensure correctness?"**
→ ACID, atomicity, consistency, isolation, serializable, transaction, invariants

---

**Use this guide for quick reference during interview preparation!** 🎯
