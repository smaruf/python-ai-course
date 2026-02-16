"""
Iterator and Snapshot Implementation

Tests: Immutable data structures, versioning, snapshot isolation

Demonstrates:
- Immutable data structures with versioning
- Snapshot isolation for concurrent access
- Iterator pattern with snapshots
- Copy-on-write for efficiency
"""

from typing import Any, List, Optional, Iterator, Dict
from dataclasses import dataclass, field
from copy import deepcopy
import threading
import time


@dataclass
class Version:
    """Represents a version of the data structure."""
    version_id: int
    timestamp: float
    data: Any


class ImmutableDataStructure:
    """
    Immutable data structure with versioning.
    
    Features:
    - Multiple versions maintained
    - Copy-on-write semantics
    - Point-in-time snapshots
    - Version history
    """
    
    def __init__(self, initial_data: Optional[Dict] = None):
        """
        Initialize immutable data structure.
        
        Args:
            initial_data: Initial data dictionary
        """
        self.versions: List[Version] = []
        self.current_version = 0
        self.lock = threading.Lock()
        
        # Create initial version
        data = initial_data.copy() if initial_data else {}
        self._create_version(data)
    
    def _create_version(self, data: Dict) -> int:
        """
        Create a new version.
        
        Args:
            data: Data for the new version
            
        Returns:
            Version ID
        """
        version = Version(
            version_id=self.current_version,
            timestamp=time.time(),
            data=deepcopy(data)
        )
        self.versions.append(version)
        self.current_version += 1
        return version.version_id
    
    def get(self, key: str, version: Optional[int] = None) -> Any:
        """
        Get value at a specific version.
        
        Args:
            key: Key to get
            version: Version ID (None for latest)
            
        Returns:
            Value or None if not found
        """
        with self.lock:
            if version is None:
                version = self.current_version - 1
            
            if 0 <= version < len(self.versions):
                return self.versions[version].data.get(key)
            
            return None
    
    def set(self, key: str, value: Any) -> int:
        """
        Set a value (creates a new version).
        
        Args:
            key: Key to set
            value: Value to set
            
        Returns:
            New version ID
        """
        with self.lock:
            # Copy current data
            current_data = self.versions[-1].data.copy()
            
            # Modify copy
            current_data[key] = value
            
            # Create new version
            return self._create_version(current_data)
    
    def delete(self, key: str) -> int:
        """
        Delete a key (creates a new version).
        
        Args:
            key: Key to delete
            
        Returns:
            New version ID
        """
        with self.lock:
            # Copy current data
            current_data = self.versions[-1].data.copy()
            
            # Modify copy
            current_data.pop(key, None)
            
            # Create new version
            return self._create_version(current_data)
    
    def snapshot(self, version: Optional[int] = None) -> Dict:
        """
        Get a snapshot of data at a specific version.
        
        Args:
            version: Version ID (None for latest)
            
        Returns:
            Snapshot of data
        """
        with self.lock:
            if version is None:
                version = self.current_version - 1
            
            if 0 <= version < len(self.versions):
                return deepcopy(self.versions[version].data)
            
            return {}
    
    def get_version_count(self) -> int:
        """Get total number of versions."""
        with self.lock:
            return len(self.versions)
    
    def get_latest_version(self) -> int:
        """Get latest version ID."""
        with self.lock:
            return self.current_version - 1
    
    def compact(self, keep_versions: int = 10):
        """
        Compact version history.
        
        Args:
            keep_versions: Number of recent versions to keep
        """
        with self.lock:
            if len(self.versions) > keep_versions:
                self.versions = self.versions[-keep_versions:]


class SnapshotIterator:
    """
    Iterator that operates on a snapshot of data.
    
    Guarantees:
    - Consistent view during iteration
    - Isolated from concurrent modifications
    - No blocking of writers
    """
    
    def __init__(self, data_structure: ImmutableDataStructure, version: Optional[int] = None):
        """
        Initialize snapshot iterator.
        
        Args:
            data_structure: ImmutableDataStructure to iterate over
            version: Version to iterate (None for latest)
        """
        self.snapshot = data_structure.snapshot(version)
        self.keys = list(self.snapshot.keys())
        self.index = 0
    
    def __iter__(self) -> 'SnapshotIterator':
        """Return self as iterator."""
        return self
    
    def __next__(self) -> tuple:
        """
        Get next item.
        
        Returns:
            Tuple of (key, value)
            
        Raises:
            StopIteration: When iteration is complete
        """
        if self.index >= len(self.keys):
            raise StopIteration
        
        key = self.keys[self.index]
        value = self.snapshot[key]
        self.index += 1
        
        return (key, value)
    
    def reset(self):
        """Reset iterator to beginning."""
        self.index = 0


class VersionedList:
    """
    Versioned list implementation with snapshot support.
    
    Features:
    - Append-only operations create new versions
    - Point-in-time snapshots
    - Efficient storage with structural sharing
    """
    
    def __init__(self):
        """Initialize versioned list."""
        self.versions: List[List[Any]] = [[]]
        self.current_version = 0
        self.lock = threading.Lock()
    
    def append(self, value: Any) -> int:
        """
        Append a value (creates new version).
        
        Args:
            value: Value to append
            
        Returns:
            New version ID
        """
        with self.lock:
            # Copy current version
            new_list = self.versions[-1].copy()
            new_list.append(value)
            
            # Create new version
            self.versions.append(new_list)
            self.current_version += 1
            
            return self.current_version
    
    def get(self, index: int, version: Optional[int] = None) -> Any:
        """
        Get value at index for a specific version.
        
        Args:
            index: List index
            version: Version ID (None for latest)
            
        Returns:
            Value at index
            
        Raises:
            IndexError: If index out of range
        """
        with self.lock:
            if version is None:
                version = self.current_version
            
            if 0 <= version < len(self.versions):
                return self.versions[version][index]
            
            raise IndexError("Version out of range")
    
    def snapshot(self, version: Optional[int] = None) -> List[Any]:
        """
        Get snapshot of list at version.
        
        Args:
            version: Version ID (None for latest)
            
        Returns:
            Snapshot list
        """
        with self.lock:
            if version is None:
                version = self.current_version
            
            if 0 <= version < len(self.versions):
                return self.versions[version].copy()
            
            return []
    
    def iterate(self, version: Optional[int] = None) -> Iterator[Any]:
        """
        Iterate over list at specific version.
        
        Args:
            version: Version ID (None for latest)
            
        Yields:
            List elements
        """
        snapshot = self.snapshot(version)
        for item in snapshot:
            yield item


if __name__ == "__main__":
    print("Iterator and Snapshot Example")
    print("=" * 60)
    
    # Immutable data structure example
    print("\n1. Immutable Data Structure")
    print("-" * 60)
    
    data = ImmutableDataStructure({"name": "Alice", "age": 30})
    print(f"Initial version {data.get_latest_version()}: {data.snapshot()}")
    
    # Modify data (creates new version)
    v1 = data.set("age", 31)
    print(f"After update, version {v1}: {data.snapshot()}")
    
    v2 = data.set("city", "New York")
    print(f"After adding city, version {v2}: {data.snapshot()}")
    
    # Access old versions
    print(f"\nVersion 0 (original): {data.snapshot(0)}")
    print(f"Version 1: {data.snapshot(1)}")
    print(f"Version 2 (latest): {data.snapshot(2)}")
    
    # Snapshot iterator
    print("\n2. Snapshot Iterator")
    print("-" * 60)
    
    # Create iterator on version 1
    print("Iterating over version 1:")
    iterator = SnapshotIterator(data, version=1)
    for key, value in iterator:
        print(f"  {key} = {value}")
    
    # Modify data while iterating
    data.set("country", "USA")
    
    # Iterator still sees old snapshot
    print("\nAfter modification, iterator still sees version 1:")
    iterator.reset()
    for key, value in iterator:
        print(f"  {key} = {value}")
    
    print(f"\nLatest version {data.get_latest_version()}: {data.snapshot()}")
    
    # Versioned list example
    print("\n3. Versioned List")
    print("-" * 60)
    
    vlist = VersionedList()
    
    print("Building list with versions...")
    vlist.append("apple")
    vlist.append("banana")
    vlist.append("cherry")
    
    print(f"Version 0: {vlist.snapshot(0)}")
    print(f"Version 1: {vlist.snapshot(1)}")
    print(f"Version 2: {vlist.snapshot(2)}")
    print(f"Version 3 (latest): {vlist.snapshot(3)}")
    
    # Iterate over specific version
    print("\nIterating over version 2:")
    for item in vlist.iterate(version=2):
        print(f"  - {item}")
    
    print(f"\nTotal versions: {data.get_version_count()}")
