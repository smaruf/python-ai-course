"""
System Building Interviews Module

This module addresses the modern trend in technical interviews where companies are
shifting from pure algorithm puzzles (LeetCode-style) to hands-on system implementation.

This reflects the industry preference for practical system building that tests:
- System design thinking
- Concurrency and multithreading
- State management
- Data modeling
- Real-world tradeoffs

The module contains 11 core system building challenges commonly asked in technical
interviews at companies like Oracle, Amazon, Google, and other tech giants.

Topics Covered:
1. Web Crawler - BFS, multithreading, synchronization
2. Rate Limiter - Sliding window, token bucket, time handling
3. Chat App - Client-server architecture, sockets, state management
4. Banking System - Transaction modeling, consistency
5. SQL Implementation - Data modeling, query execution
6. Key-Value Store with WAL - Persistence, durability, recovery
7. Kubernetes Scheduler - Resource allocation logic
8. File System - Tree structures, path resolution
9. Log Aggregator - Ordering, binary search, streaming
10. Iterator/Snapshot - Immutable data structures
11. Functional Pipelines - Lazy execution, functional composition

Each implementation is production-quality and demonstrates best practices for
backend/distributed systems engineering.
"""

__version__ = "1.0.0"

from .web_crawler import WebCrawler
from .rate_limiter import RateLimiter, TokenBucketLimiter, SlidingWindowLimiter
from .chat_app import ChatServer, ChatClient
from .banking_system import BankingSystem, Account, Transaction
from .sql_engine import SQLEngine, Table, Query
from .kv_store import KeyValueStore, WriteAheadLog
from .k8s_scheduler import KubernetesScheduler, Pod, Node
from .file_system import FileSystem, File, Directory
from .log_aggregator import LogAggregator, LogEntry
from .iterator_snapshot import SnapshotIterator, ImmutableDataStructure
from .functional_pipeline import Pipeline, LazyPipeline

__all__ = [
    # Web Crawler
    "WebCrawler",
    
    # Rate Limiter
    "RateLimiter",
    "TokenBucketLimiter",
    "SlidingWindowLimiter",
    
    # Chat App
    "ChatServer",
    "ChatClient",
    
    # Banking System
    "BankingSystem",
    "Account",
    "Transaction",
    
    # SQL Engine
    "SQLEngine",
    "Table",
    "Query",
    
    # Key-Value Store
    "KeyValueStore",
    "WriteAheadLog",
    
    # Kubernetes Scheduler
    "KubernetesScheduler",
    "Pod",
    "Node",
    
    # File System
    "FileSystem",
    "File",
    "Directory",
    
    # Log Aggregator
    "LogAggregator",
    "LogEntry",
    
    # Iterator/Snapshot
    "SnapshotIterator",
    "ImmutableDataStructure",
    
    # Functional Pipeline
    "Pipeline",
    "LazyPipeline",
]
