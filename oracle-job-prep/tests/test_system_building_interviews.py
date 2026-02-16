"""
Tests for System Building Interviews Module

Basic test coverage for all implementations to ensure correctness.
"""

import unittest
import time
import threading
import os
import tempfile
from src.system_building_interviews.web_crawler import WebCrawler
from src.system_building_interviews.rate_limiter import (
    TokenBucketLimiter, SlidingWindowLimiter, FixedWindowCounterLimiter
)
from src.system_building_interviews.chat_app import ChatServer, ChatClient
from src.system_building_interviews.banking_system import (
    BankingSystem, Account, TransactionType, TransactionStatus
)
from src.system_building_interviews.sql_engine import (
    SQLEngine, Table, Column, ColumnType
)
from src.system_building_interviews.kv_store import KeyValueStore
from src.system_building_interviews.k8s_scheduler import (
    KubernetesScheduler, Node, Pod, Resources
)
from src.system_building_interviews.file_system import FileSystem
from src.system_building_interviews.log_aggregator import (
    LogAggregator, LogEntry, LogLevel
)
from src.system_building_interviews.iterator_snapshot import (
    ImmutableDataStructure, SnapshotIterator, VersionedList
)
from src.system_building_interviews.functional_pipeline import (
    LazyPipeline, Pipeline
)


class TestWebCrawler(unittest.TestCase):
    """Test web crawler implementation."""
    
    def test_basic_crawl(self):
        """Test basic crawling functionality."""
        crawler = WebCrawler(max_depth=1, max_workers=2, delay=0.01)
        
        def fetch(url):
            return {
                'content': '<a href="/page1">Link</a>',
                'title': f'Page {url}'
            }
        
        results = crawler.crawl("https://example.com", fetch)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]['url'], "https://example.com")


class TestRateLimiter(unittest.TestCase):
    """Test rate limiter implementations."""
    
    def test_token_bucket_basic(self):
        """Test token bucket rate limiter."""
        limiter = TokenBucketLimiter(capacity=5, refill_rate=1)
        
        # First 5 requests should succeed
        for i in range(5):
            self.assertTrue(limiter.allow_request("user1"))
        
        # 6th request should fail
        self.assertFalse(limiter.allow_request("user1"))
    
    def test_sliding_window(self):
        """Test sliding window rate limiter."""
        limiter = SlidingWindowLimiter(max_requests=3, window_size=1.0)
        
        # First 3 requests succeed
        for i in range(3):
            self.assertTrue(limiter.allow_request("user1"))
        
        # 4th fails
        self.assertFalse(limiter.allow_request("user1"))
        
        # After window, should succeed
        time.sleep(1.1)
        self.assertTrue(limiter.allow_request("user1"))


class TestChatApp(unittest.TestCase):
    """Test chat application."""
    
    def test_message_exchange(self):
        """Test basic message exchange."""
        server = ChatServer()
        server.start()
        
        alice = ChatClient("Alice", server)
        bob = ChatClient("Bob", server)
        
        # Wait for system messages
        time.sleep(0.1)
        
        # Send message
        alice.send_message("Hello Bob!")
        time.sleep(0.1)
        
        # Bob should receive message
        messages = bob.get_messages()
        self.assertGreater(len(messages), 0)
        
        server.stop()


class TestBankingSystem(unittest.TestCase):
    """Test banking system."""
    
    def test_transfer(self):
        """Test money transfer between accounts."""
        bank = BankingSystem()
        
        alice = bank.create_account("Alice", initial_balance=1000.0)
        bob = bank.create_account("Bob", initial_balance=500.0)
        
        # Transfer
        tx = bank.transfer("Alice", "Bob", 200.0)
        
        # Check balances
        self.assertEqual(alice.get_balance(), 800.0)
        self.assertEqual(bob.get_balance(), 700.0)
        self.assertEqual(tx.status, TransactionStatus.COMPLETED)
    
    def test_insufficient_funds(self):
        """Test insufficient funds error."""
        bank = BankingSystem()
        alice = bank.create_account("Alice", initial_balance=100.0)
        bob = bank.create_account("Bob", initial_balance=0.0)
        
        # Should raise error
        with self.assertRaises(ValueError):
            bank.transfer("Alice", "Bob", 200.0)


class TestSQLEngine(unittest.TestCase):
    """Test SQL engine."""
    
    def test_table_operations(self):
        """Test basic table operations."""
        db = SQLEngine()
        
        # Create table
        users = db.create_table("users", [
            Column("id", ColumnType.INTEGER, primary_key=True),
            Column("name", ColumnType.TEXT)
        ])
        
        # Insert
        users.insert({"id": 1, "name": "Alice"})
        users.insert({"id": 2, "name": "Bob"})
        
        # Select all
        results = users.select()
        self.assertEqual(len(results), 2)
        
        # Select with filter
        filtered = users.select(where=lambda row: row["id"] == 1)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["name"], "Alice")


class TestKeyValueStore(unittest.TestCase):
    """Test key-value store with WAL."""
    
    def test_persistence(self):
        """Test WAL persistence and recovery."""
        # Create temp file safely
        fd, wal_file = tempfile.mkstemp()
        os.close(fd)  # Close the file descriptor
        
        try:
            # Create store and add data
            store = KeyValueStore(wal_file, auto_compact_threshold=100)
            store.set("key1", "value1")
            store.set("key2", "value2")
            
            # Delete store (simulate crash)
            del store
            
            # Recover
            recovered = KeyValueStore(wal_file)
            self.assertEqual(recovered.get("key1"), "value1")
            self.assertEqual(recovered.get("key2"), "value2")
            
        finally:
            if os.path.exists(wal_file):
                os.remove(wal_file)


class TestKubernetesScheduler(unittest.TestCase):
    """Test Kubernetes scheduler."""
    
    def test_pod_scheduling(self):
        """Test basic pod scheduling."""
        scheduler = KubernetesScheduler()
        
        # Add node
        scheduler.add_node(Node(
            name="node-1",
            total_resources=Resources(cpu_millicores=4000, memory_mb=8192)
        ))
        
        # Submit pod
        scheduler.submit_pod(Pod(
            name="pod-1",
            namespace="default",
            resource_requests=Resources(cpu_millicores=500, memory_mb=1024),
            resource_limits=Resources(cpu_millicores=1000, memory_mb=2048)
        ))
        
        # Schedule
        scheduled = scheduler.schedule_pending_pods()
        self.assertEqual(len(scheduled), 1)
        self.assertIn("pod-1", scheduled)


class TestFileSystem(unittest.TestCase):
    """Test file system implementation."""
    
    def test_file_operations(self):
        """Test basic file operations."""
        fs = FileSystem()
        
        # Create directory
        self.assertTrue(fs.mkdir("/home"))
        self.assertTrue(fs.mkdir("/home/user"))
        
        # Create file
        self.assertTrue(fs.create_file("/home/user/test.txt", "Hello"))
        
        # Read file
        content = fs.read_file("/home/user/test.txt")
        self.assertEqual(content, "Hello")
        
        # Write file
        fs.write_file("/home/user/test.txt", "World")
        content = fs.read_file("/home/user/test.txt")
        self.assertEqual(content, "World")
        
        # List directory
        files = fs.list_directory("/home/user")
        self.assertIn("test.txt", files)


class TestLogAggregator(unittest.TestCase):
    """Test log aggregator."""
    
    def test_log_ingestion(self):
        """Test log ingestion and querying."""
        aggregator = LogAggregator()
        
        # Ingest logs
        base_time = time.time()
        logs = [
            LogEntry(base_time, LogLevel.INFO, "app", "Started"),
            LogEntry(base_time + 1, LogLevel.ERROR, "app", "Error occurred"),
            LogEntry(base_time + 2, LogLevel.INFO, "app", "Recovered"),
        ]
        
        aggregator.ingest_batch(logs)
        
        # Query by time range
        results = aggregator.query_time_range(base_time, base_time + 1.5)
        self.assertEqual(len(results), 2)
        
        # Query by level
        errors = aggregator.query_recent(10, level=LogLevel.ERROR)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].message, "Error occurred")


class TestIteratorSnapshot(unittest.TestCase):
    """Test iterator and snapshot."""
    
    def test_versioning(self):
        """Test versioned data structure."""
        data = ImmutableDataStructure({"key1": "value1"})
        
        # Modify (creates new version)
        v1 = data.set("key2", "value2")
        v2 = data.set("key3", "value3")
        
        # Access different versions
        v0_snapshot = data.snapshot(0)
        self.assertEqual(len(v0_snapshot), 1)
        
        v2_snapshot = data.snapshot(2)
        self.assertEqual(len(v2_snapshot), 3)
    
    def test_snapshot_isolation(self):
        """Test snapshot iterator isolation."""
        data = ImmutableDataStructure({"a": 1, "b": 2})
        
        # Create iterator
        iterator = SnapshotIterator(data, version=0)
        
        # Modify data
        data.set("c", 3)
        
        # Iterator should still see old version
        items = list(iterator)
        self.assertEqual(len(items), 2)


class TestFunctionalPipeline(unittest.TestCase):
    """Test functional pipelines."""
    
    def test_lazy_pipeline(self):
        """Test lazy evaluation pipeline."""
        result = (LazyPipeline([1, 2, 3, 4, 5])
                  .filter(lambda x: x % 2 == 0)
                  .map(lambda x: x * 2)
                  .to_list())
        
        self.assertEqual(result, [4, 8])
    
    def test_eager_pipeline(self):
        """Test eager evaluation pipeline."""
        result = (Pipeline([1, 2, 3, 4, 5])
                  .filter(lambda x: x > 2)
                  .map(lambda x: x * 2)
                  .to_list())
        
        self.assertEqual(result, [6, 8, 10])
    
    def test_reduce(self):
        """Test reduce operation."""
        result = (LazyPipeline([1, 2, 3, 4, 5])
                  .reduce(lambda a, b: a + b, 0))
        
        self.assertEqual(result, 15)


if __name__ == '__main__':
    unittest.main()
