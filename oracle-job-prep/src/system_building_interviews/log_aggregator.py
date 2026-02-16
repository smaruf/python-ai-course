"""
Log Aggregator Implementation

Tests: Ordering, binary search, streaming, time-series data

A log aggregation system demonstrating:
- Efficient log ingestion
- Time-based ordering and searching
- Binary search for time ranges
- Log streaming and filtering
- Aggregation and statistics
"""

from typing import List, Optional, Callable, Iterator
from dataclasses import dataclass
from datetime import datetime
import bisect
import threading
from enum import Enum


class LogLevel(Enum):
    """Log level enumeration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LogEntry:
    """Represents a log entry."""
    timestamp: float
    level: LogLevel
    source: str
    message: str
    metadata: dict = None
    
    def __post_init__(self):
        """Initialize metadata if None."""
        if self.metadata is None:
            self.metadata = {}
    
    def __lt__(self, other):
        """Compare by timestamp for sorting."""
        return self.timestamp < other.timestamp
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp,
            'level': self.level.value,
            'source': self.source,
            'message': self.message,
            'metadata': self.metadata
        }


class LogAggregator:
    """
    Log aggregation system with efficient querying.
    
    Features:
    - Time-ordered log storage
    - Binary search for time range queries
    - Real-time log streaming
    - Filtering by level and source
    - Log statistics and aggregation
    - Thread-safe operations
    """
    
    def __init__(self, max_size: int = 100000):
        """
        Initialize log aggregator.
        
        Args:
            max_size: Maximum number of logs to store
        """
        self.logs: List[LogEntry] = []
        self.max_size = max_size
        self.lock = threading.Lock()
        self.sources = set()
    
    def ingest(self, entry: LogEntry):
        """
        Ingest a log entry.
        
        Args:
            entry: Log entry to ingest
        """
        with self.lock:
            # Use binary search to find insertion point
            index = bisect.bisect_left(self.logs, entry)
            self.logs.insert(index, entry)
            
            # Track sources
            self.sources.add(entry.source)
            
            # Evict old logs if at capacity
            if len(self.logs) > self.max_size:
                self.logs.pop(0)
    
    def ingest_batch(self, entries: List[LogEntry]):
        """
        Ingest multiple log entries efficiently.
        
        Args:
            entries: List of log entries
        """
        with self.lock:
            # Add all entries
            self.logs.extend(entries)
            
            # Re-sort (more efficient than multiple inserts)
            self.logs.sort()
            
            # Update sources
            for entry in entries:
                self.sources.add(entry.source)
            
            # Trim if needed
            if len(self.logs) > self.max_size:
                self.logs = self.logs[-self.max_size:]
    
    def query_time_range(
        self,
        start_time: float,
        end_time: float,
        level: Optional[LogLevel] = None,
        source: Optional[str] = None
    ) -> List[LogEntry]:
        """
        Query logs within a time range using binary search.
        
        Args:
            start_time: Start timestamp
            end_time: End timestamp
            level: Optional log level filter
            source: Optional source filter
            
        Returns:
            List of matching log entries
        """
        with self.lock:
            # Use binary search to find range boundaries
            start_entry = LogEntry(start_time, LogLevel.DEBUG, "", "")
            end_entry = LogEntry(end_time, LogLevel.DEBUG, "", "")
            
            start_idx = bisect.bisect_left(self.logs, start_entry)
            end_idx = bisect.bisect_right(self.logs, end_entry)
            
            # Extract logs in range
            range_logs = self.logs[start_idx:end_idx]
            
            # Apply filters
            if level:
                range_logs = [log for log in range_logs if log.level == level]
            
            if source:
                range_logs = [log for log in range_logs if log.source == source]
            
            return range_logs
    
    def query_recent(
        self,
        count: int,
        level: Optional[LogLevel] = None,
        source: Optional[str] = None
    ) -> List[LogEntry]:
        """
        Query most recent logs.
        
        Args:
            count: Number of logs to return
            level: Optional log level filter
            source: Optional source filter
            
        Returns:
            List of recent log entries
        """
        with self.lock:
            logs = self.logs.copy()
            
            # Apply filters
            if level:
                logs = [log for log in logs if log.level == level]
            
            if source:
                logs = [log for log in logs if log.source == source]
            
            # Return most recent
            return logs[-count:]
    
    def stream(
        self,
        filter_fn: Optional[Callable[[LogEntry], bool]] = None
    ) -> Iterator[LogEntry]:
        """
        Stream logs (for real-time monitoring).
        
        Args:
            filter_fn: Optional filter function
            
        Yields:
            Log entries
        """
        with self.lock:
            for log in self.logs:
                if filter_fn is None or filter_fn(log):
                    yield log
    
    def count_by_level(self) -> dict:
        """
        Count logs by level.
        
        Returns:
            Dictionary of level -> count
        """
        with self.lock:
            counts = {level: 0 for level in LogLevel}
            
            for log in self.logs:
                counts[log.level] += 1
            
            return {level.value: count for level, count in counts.items()}
    
    def count_by_source(self) -> dict:
        """
        Count logs by source.
        
        Returns:
            Dictionary of source -> count
        """
        with self.lock:
            counts = {}
            
            for log in self.logs:
                counts[log.source] = counts.get(log.source, 0) + 1
            
            return counts
    
    def get_error_rate(self, time_window: float) -> float:
        """
        Calculate error rate in the last time window.
        
        Args:
            time_window: Time window in seconds
            
        Returns:
            Error rate (errors per second)
        """
        import time
        current_time = time.time()
        start_time = current_time - time_window
        
        logs = self.query_time_range(start_time, current_time)
        
        error_count = sum(
            1 for log in logs
            if log.level in [LogLevel.ERROR, LogLevel.CRITICAL]
        )
        
        return error_count / time_window if time_window > 0 else 0
    
    def search(self, keyword: str) -> List[LogEntry]:
        """
        Search logs by keyword in message.
        
        Args:
            keyword: Keyword to search for
            
        Returns:
            List of matching log entries
        """
        with self.lock:
            return [
                log for log in self.logs
                if keyword.lower() in log.message.lower()
            ]
    
    def clear(self):
        """Clear all logs."""
        with self.lock:
            self.logs.clear()
            self.sources.clear()
    
    def size(self) -> int:
        """Get number of stored logs."""
        with self.lock:
            return len(self.logs)


class LogBuffer:
    """
    Buffered log writer for batching.
    
    Buffers log entries and flushes to aggregator in batches
    for better performance.
    """
    
    def __init__(self, aggregator: LogAggregator, buffer_size: int = 100):
        """
        Initialize log buffer.
        
        Args:
            aggregator: LogAggregator to write to
            buffer_size: Buffer size before auto-flush
        """
        self.aggregator = aggregator
        self.buffer_size = buffer_size
        self.buffer: List[LogEntry] = []
        self.lock = threading.Lock()
    
    def write(self, entry: LogEntry):
        """
        Write a log entry to buffer.
        
        Args:
            entry: Log entry to write
        """
        with self.lock:
            self.buffer.append(entry)
            
            if len(self.buffer) >= self.buffer_size:
                self.flush()
    
    def flush(self):
        """Flush buffer to aggregator."""
        with self.lock:
            if self.buffer:
                self.aggregator.ingest_batch(self.buffer)
                self.buffer.clear()


if __name__ == "__main__":
    import time
    
    print("Log Aggregator Example")
    print("=" * 60)
    
    # Create aggregator
    aggregator = LogAggregator()
    
    # Generate sample logs
    print("\nGenerating sample logs...")
    base_time = time.time()
    
    logs = [
        LogEntry(base_time, LogLevel.INFO, "web-server", "Server started"),
        LogEntry(base_time + 1, LogLevel.DEBUG, "web-server", "Processing request"),
        LogEntry(base_time + 2, LogLevel.INFO, "database", "Connection established"),
        LogEntry(base_time + 3, LogLevel.WARNING, "web-server", "Slow query detected"),
        LogEntry(base_time + 4, LogLevel.ERROR, "database", "Connection timeout"),
        LogEntry(base_time + 5, LogLevel.INFO, "web-server", "Request completed"),
        LogEntry(base_time + 6, LogLevel.CRITICAL, "database", "Database crash"),
        LogEntry(base_time + 7, LogLevel.INFO, "web-server", "Retry initiated"),
    ]
    
    # Ingest logs
    aggregator.ingest_batch(logs)
    print(f"  Ingested {aggregator.size()} logs")
    
    # Query by time range
    print(f"\nLogs between t+2 and t+5:")
    range_logs = aggregator.query_time_range(base_time + 2, base_time + 5)
    for log in range_logs:
        print(f"  [{log.level.value}] {log.source}: {log.message}")
    
    # Query recent errors
    print("\nRecent ERROR logs:")
    errors = aggregator.query_recent(10, level=LogLevel.ERROR)
    for log in errors:
        print(f"  [{log.source}] {log.message}")
    
    # Count by level
    print("\nLog counts by level:")
    level_counts = aggregator.count_by_level()
    for level, count in level_counts.items():
        if count > 0:
            print(f"  {level}: {count}")
    
    # Count by source
    print("\nLog counts by source:")
    source_counts = aggregator.count_by_source()
    for source, count in source_counts.items():
        print(f"  {source}: {count}")
    
    # Search
    print("\nSearching for 'request':")
    search_results = aggregator.search("request")
    for log in search_results:
        print(f"  [{log.level.value}] {log.message}")
    
    # Error rate
    error_rate = aggregator.get_error_rate(10.0)
    print(f"\nError rate (last 10s): {error_rate:.2f} errors/sec")
