"""
Key-Value Store with Write-Ahead Logging (WAL)

Tests: Persistence, durability, recovery, crash consistency

A persistent key-value store demonstrating:
- Write-Ahead Logging for durability
- Crash recovery
- In-memory cache with disk persistence
- Snapshot and compaction
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import json
import os
import threading
import time


class OperationType(Enum):
    """WAL operation types."""
    SET = "SET"
    DELETE = "DELETE"
    CHECKPOINT = "CHECKPOINT"


@dataclass
class WALEntry:
    """Write-Ahead Log entry."""
    sequence_number: int
    operation: OperationType
    key: Optional[str]
    value: Optional[Any]
    timestamp: float
    
    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps({
            'seq': self.sequence_number,
            'op': self.operation.value,
            'key': self.key,
            'value': self.value,
            'ts': self.timestamp
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> 'WALEntry':
        """Deserialize from JSON."""
        data = json.loads(json_str)
        return cls(
            sequence_number=data['seq'],
            operation=OperationType(data['op']),
            key=data.get('key'),
            value=data.get('value'),
            timestamp=data['ts']
        )


class WriteAheadLog:
    """
    Write-Ahead Log for durability.
    
    Features:
    - Sequential log writing
    - Atomic append operations
    - Log replay for recovery
    - Compaction support
    """
    
    def __init__(self, log_file: str):
        """
        Initialize WAL.
        
        Args:
            log_file: Path to log file
        """
        self.log_file = log_file
        self.sequence_number = 0
        self.lock = threading.Lock()
        
        # Create log file if it doesn't exist
        if not os.path.exists(log_file):
            with open(log_file, 'w') as f:
                pass
        else:
            # Recover sequence number from existing log
            self.sequence_number = self._get_last_sequence_number()
    
    def append(
        self,
        operation: OperationType,
        key: Optional[str] = None,
        value: Optional[Any] = None
    ) -> int:
        """
        Append an entry to the WAL.
        
        Args:
            operation: Operation type
            key: Key (for SET/DELETE)
            value: Value (for SET)
            
        Returns:
            Sequence number of the entry
        """
        with self.lock:
            self.sequence_number += 1
            entry = WALEntry(
                sequence_number=self.sequence_number,
                operation=operation,
                key=key,
                value=value,
                timestamp=time.time()
            )
            
            # Append to log file
            with open(self.log_file, 'a') as f:
                f.write(entry.to_json() + '\n')
                f.flush()
                os.fsync(f.fileno())  # Force disk write
            
            return self.sequence_number
    
    def replay(self) -> List[WALEntry]:
        """
        Replay all entries from the log.
        
        Returns:
            List of WAL entries
        """
        entries = []
        
        if not os.path.exists(self.log_file):
            return entries
        
        with open(self.log_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entry = WALEntry.from_json(line)
                        entries.append(entry)
                    except Exception as e:
                        print(f"Error parsing WAL entry: {e}")
        
        return entries
    
    def compact(self, data: Dict[str, Any]):
        """
        Compact the WAL by creating a checkpoint.
        
        Args:
            data: Current state to checkpoint
        """
        with self.lock:
            # Write checkpoint to new file
            temp_file = self.log_file + '.tmp'
            
            with open(temp_file, 'w') as f:
                # Write checkpoint marker
                self.sequence_number += 1
                checkpoint = WALEntry(
                    sequence_number=self.sequence_number,
                    operation=OperationType.CHECKPOINT,
                    key=None,
                    value=None,
                    timestamp=time.time()
                )
                f.write(checkpoint.to_json() + '\n')
                
                # Write current state
                for key, value in data.items():
                    self.sequence_number += 1
                    entry = WALEntry(
                        sequence_number=self.sequence_number,
                        operation=OperationType.SET,
                        key=key,
                        value=value,
                        timestamp=time.time()
                    )
                    f.write(entry.to_json() + '\n')
                
                f.flush()
                os.fsync(f.fileno())
            
            # Atomic replacement
            os.replace(temp_file, self.log_file)
    
    def _get_last_sequence_number(self) -> int:
        """Get the last sequence number from the log."""
        last_seq = 0
        
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            entry = WALEntry.from_json(line)
                            last_seq = max(last_seq, entry.sequence_number)
                        except:
                            pass
        except:
            pass
        
        return last_seq


class KeyValueStore:
    """
    Persistent key-value store with WAL.
    
    Features:
    - In-memory data with disk persistence
    - Write-ahead logging for durability
    - Crash recovery
    - Automatic compaction
    - Thread-safe operations
    """
    
    def __init__(
        self,
        wal_file: str,
        auto_compact_threshold: int = 1000
    ):
        """
        Initialize key-value store.
        
        Args:
            wal_file: Path to WAL file
            auto_compact_threshold: Compact when WAL grows beyond this size
        """
        self.data: Dict[str, Any] = {}
        self.wal = WriteAheadLog(wal_file)
        self.auto_compact_threshold = auto_compact_threshold
        self.operation_count = 0
        self.lock = threading.Lock()
        
        # Recover from WAL
        self._recover()
    
    def _recover(self):
        """Recover state from WAL."""
        entries = self.wal.replay()
        
        for entry in entries:
            if entry.operation == OperationType.SET:
                self.data[entry.key] = entry.value
            elif entry.operation == OperationType.DELETE:
                self.data.pop(entry.key, None)
            elif entry.operation == OperationType.CHECKPOINT:
                # Checkpoint marker - data follows
                pass
        
        print(f"Recovered {len(self.data)} keys from WAL ({len(entries)} log entries)")
    
    def set(self, key: str, value: Any):
        """
        Set a key-value pair.
        
        Args:
            key: Key
            value: Value
        """
        # Write to WAL first (durability)
        self.wal.append(OperationType.SET, key, value)
        
        # Then update in-memory state
        with self.lock:
            self.data[key] = value
            self.operation_count += 1
        
        # Auto-compact if needed
        if self.operation_count >= self.auto_compact_threshold:
            self.compact()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value by key.
        
        Args:
            key: Key
            
        Returns:
            Value or None if not found
        """
        with self.lock:
            return self.data.get(key)
    
    def delete(self, key: str) -> bool:
        """
        Delete a key-value pair.
        
        Args:
            key: Key
            
        Returns:
            True if key existed, False otherwise
        """
        # Write to WAL first
        self.wal.append(OperationType.DELETE, key)
        
        # Then update in-memory state
        with self.lock:
            if key in self.data:
                del self.data[key]
                self.operation_count += 1
                return True
            return False
    
    def exists(self, key: str) -> bool:
        """Check if a key exists."""
        with self.lock:
            return key in self.data
    
    def keys(self) -> List[str]:
        """Get all keys."""
        with self.lock:
            return list(self.data.keys())
    
    def size(self) -> int:
        """Get number of keys."""
        with self.lock:
            return len(self.data)
    
    def compact(self):
        """Compact the WAL."""
        with self.lock:
            self.wal.compact(self.data)
            self.operation_count = 0
    
    def clear(self):
        """Clear all data."""
        with self.lock:
            for key in list(self.data.keys()):
                self.wal.append(OperationType.DELETE, key)
                del self.data[key]


if __name__ == "__main__":
    print("Key-Value Store with WAL Example")
    print("=" * 60)
    
    # Create temporary WAL file
    import tempfile
    wal_file = os.path.join(tempfile.gettempdir(), "kv_store.wal")
    
    # Clean up old WAL file if exists
    if os.path.exists(wal_file):
        os.remove(wal_file)
    
    print(f"\nUsing WAL file: {wal_file}")
    
    # Create store
    print("\nCreating new store...")
    store = KeyValueStore(wal_file, auto_compact_threshold=5)
    
    # Set values
    print("\nSetting values...")
    store.set("user:1", {"name": "Alice", "age": 30})
    store.set("user:2", {"name": "Bob", "age": 25})
    store.set("user:3", {"name": "Charlie", "age": 35})
    store.set("counter", 100)
    
    print(f"  Store size: {store.size()} keys")
    
    # Get values
    print("\nGetting values...")
    print(f"  user:1 = {store.get('user:1')}")
    print(f"  counter = {store.get('counter')}")
    
    # Update value
    print("\nUpdating counter...")
    store.set("counter", 101)
    print(f"  counter = {store.get('counter')}")
    
    # Delete value
    print("\nDeleting user:2...")
    store.delete("user:2")
    print(f"  Store size: {store.size()} keys")
    
    # Simulate crash and recovery
    print("\n" + "=" * 60)
    print("Simulating crash and recovery...")
    print("=" * 60)
    
    del store  # "Crash"
    
    # Recover
    print("\nRecovering from WAL...")
    recovered_store = KeyValueStore(wal_file)
    
    print(f"\nRecovered data:")
    for key in recovered_store.keys():
        print(f"  {key} = {recovered_store.get(key)}")
    
    print(f"\nStore size after recovery: {recovered_store.size()} keys")
    
    # Cleanup
    if os.path.exists(wal_file):
        os.remove(wal_file)
