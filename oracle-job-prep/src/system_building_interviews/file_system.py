"""
File System Implementation

Tests: Tree structures, path resolution, directory traversal

A simplified file system demonstrating:
- Tree structure for files and directories
- Path resolution and navigation
- File operations (create, read, write, delete)
- Directory operations
- Path normalization
"""

from typing import Optional, List, Dict, Union
from dataclasses import dataclass, field
from datetime import datetime
import threading


class FileSystemNode:
    """Base class for file system nodes."""
    
    def __init__(self, name: str, parent: Optional['Directory'] = None):
        """
        Initialize file system node.
        
        Args:
            name: Node name
            parent: Parent directory
        """
        self.name = name
        self.parent = parent
        self.created_at = datetime.now()
        self.modified_at = datetime.now()
    
    def get_path(self) -> str:
        """Get absolute path of this node."""
        if self.parent is None:
            return "/"
        
        parent_path = self.parent.get_path()
        if parent_path == "/":
            return f"/{self.name}"
        return f"{parent_path}/{self.name}"
    
    def is_file(self) -> bool:
        """Check if this is a file."""
        return isinstance(self, File)
    
    def is_directory(self) -> bool:
        """Check if this is a directory."""
        return isinstance(self, Directory)


class File(FileSystemNode):
    """Represents a file in the file system."""
    
    def __init__(self, name: str, parent: Optional['Directory'] = None, content: str = ""):
        """
        Initialize file.
        
        Args:
            name: File name
            parent: Parent directory
            content: Initial file content
        """
        super().__init__(name, parent)
        self.content = content
    
    def read(self) -> str:
        """Read file content."""
        return self.content
    
    def write(self, content: str):
        """Write file content."""
        self.content = content
        self.modified_at = datetime.now()
    
    def append(self, content: str):
        """Append to file content."""
        self.content += content
        self.modified_at = datetime.now()
    
    def size(self) -> int:
        """Get file size in bytes."""
        return len(self.content.encode('utf-8'))


class Directory(FileSystemNode):
    """Represents a directory in the file system."""
    
    def __init__(self, name: str, parent: Optional['Directory'] = None):
        """
        Initialize directory.
        
        Args:
            name: Directory name
            parent: Parent directory
        """
        super().__init__(name, parent)
        self.children: Dict[str, FileSystemNode] = {}
    
    def add_child(self, child: FileSystemNode):
        """
        Add a child node to this directory.
        
        Args:
            child: Child node to add
            
        Raises:
            ValueError: If child already exists
        """
        if child.name in self.children:
            raise ValueError(f"'{child.name}' already exists")
        
        self.children[child.name] = child
        child.parent = self
        self.modified_at = datetime.now()
    
    def remove_child(self, name: str) -> bool:
        """
        Remove a child node.
        
        Args:
            name: Name of child to remove
            
        Returns:
            True if removed, False if not found
        """
        if name in self.children:
            del self.children[name]
            self.modified_at = datetime.now()
            return True
        return False
    
    def get_child(self, name: str) -> Optional[FileSystemNode]:
        """Get a child node by name."""
        return self.children.get(name)
    
    def list_children(self) -> List[str]:
        """List all child names."""
        return list(self.children.keys())
    
    def size(self) -> int:
        """Get total size of directory and all contents."""
        total = 0
        for child in self.children.values():
            total += child.size()
        return total


class FileSystem:
    """
    File system implementation with path resolution.
    
    Features:
    - Hierarchical file/directory structure
    - Absolute and relative path resolution
    - File and directory operations
    - Thread-safe operations
    - Path normalization
    """
    
    def __init__(self):
        """Initialize file system."""
        self.root = Directory("")
        self.lock = threading.Lock()
    
    def _normalize_path(self, path: str) -> str:
        """
        Normalize a file path.
        
        Args:
            path: Path to normalize
            
        Returns:
            Normalized path
        """
        # Remove trailing slashes
        path = path.rstrip('/')
        if not path:
            return "/"
        
        # Split path into components
        components = []
        for part in path.split('/'):
            if part == '' or part == '.':
                continue
            elif part == '..':
                if components:
                    components.pop()
            else:
                components.append(part)
        
        # Reconstruct path
        if not components:
            return "/"
        return "/" + "/".join(components)
    
    def _resolve_path(self, path: str) -> Optional[FileSystemNode]:
        """
        Resolve a path to a file system node.
        
        Args:
            path: Path to resolve
            
        Returns:
            FileSystemNode or None if not found
        """
        path = self._normalize_path(path)
        
        if path == "/":
            return self.root
        
        # Navigate from root
        current = self.root
        parts = path.split('/')[1:]  # Skip first empty part
        
        for part in parts:
            if not isinstance(current, Directory):
                return None
            
            current = current.get_child(part)
            if current is None:
                return None
        
        return current
    
    def mkdir(self, path: str) -> bool:
        """
        Create a directory.
        
        Args:
            path: Directory path
            
        Returns:
            True if created, False if already exists
        """
        with self.lock:
            path = self._normalize_path(path)
            
            # Check if already exists
            if self._resolve_path(path):
                return False
            
            # Get parent directory
            parent_path = "/".join(path.split('/')[:-1])
            if not parent_path:
                parent_path = "/"
            
            parent = self._resolve_path(parent_path)
            if not parent or not isinstance(parent, Directory):
                raise ValueError(f"Parent directory not found: {parent_path}")
            
            # Create directory
            name = path.split('/')[-1]
            directory = Directory(name, parent)
            parent.add_child(directory)
            
            return True
    
    def create_file(self, path: str, content: str = "") -> bool:
        """
        Create a file.
        
        Args:
            path: File path
            content: Initial file content
            
        Returns:
            True if created, False if already exists
        """
        with self.lock:
            path = self._normalize_path(path)
            
            # Check if already exists
            if self._resolve_path(path):
                return False
            
            # Get parent directory
            parent_path = "/".join(path.split('/')[:-1])
            if not parent_path:
                parent_path = "/"
            
            parent = self._resolve_path(parent_path)
            if not parent or not isinstance(parent, Directory):
                raise ValueError(f"Parent directory not found: {parent_path}")
            
            # Create file
            name = path.split('/')[-1]
            file = File(name, parent, content)
            parent.add_child(file)
            
            return True
    
    def read_file(self, path: str) -> Optional[str]:
        """
        Read file content.
        
        Args:
            path: File path
            
        Returns:
            File content or None if not found
        """
        with self.lock:
            node = self._resolve_path(path)
            if node and isinstance(node, File):
                return node.read()
            return None
    
    def write_file(self, path: str, content: str) -> bool:
        """
        Write file content.
        
        Args:
            path: File path
            content: Content to write
            
        Returns:
            True if successful, False if file not found
        """
        with self.lock:
            node = self._resolve_path(path)
            if node and isinstance(node, File):
                node.write(content)
                return True
            return False
    
    def delete(self, path: str) -> bool:
        """
        Delete a file or directory.
        
        Args:
            path: Path to delete
            
        Returns:
            True if deleted, False if not found
        """
        with self.lock:
            path = self._normalize_path(path)
            
            if path == "/":
                raise ValueError("Cannot delete root directory")
            
            node = self._resolve_path(path)
            if not node:
                return False
            
            # Remove from parent
            if node.parent:
                node.parent.remove_child(node.name)
                return True
            
            return False
    
    def list_directory(self, path: str) -> Optional[List[str]]:
        """
        List directory contents.
        
        Args:
            path: Directory path
            
        Returns:
            List of child names or None if not a directory
        """
        with self.lock:
            node = self._resolve_path(path)
            if node and isinstance(node, Directory):
                return node.list_children()
            return None
    
    def exists(self, path: str) -> bool:
        """Check if a path exists."""
        with self.lock:
            return self._resolve_path(path) is not None
    
    def is_file(self, path: str) -> bool:
        """Check if path is a file."""
        with self.lock:
            node = self._resolve_path(path)
            return node is not None and isinstance(node, File)
    
    def is_directory(self, path: str) -> bool:
        """Check if path is a directory."""
        with self.lock:
            node = self._resolve_path(path)
            return node is not None and isinstance(node, Directory)


if __name__ == "__main__":
    print("File System Example")
    print("=" * 60)
    
    # Create file system
    fs = FileSystem()
    
    # Create directories
    print("\nCreating directories...")
    fs.mkdir("/home")
    fs.mkdir("/home/user")
    fs.mkdir("/home/user/documents")
    fs.mkdir("/var")
    fs.mkdir("/var/log")
    
    # Create files
    print("\nCreating files...")
    fs.create_file("/home/user/readme.txt", "Hello, World!")
    fs.create_file("/home/user/documents/notes.txt", "My notes")
    fs.create_file("/var/log/system.log", "System started\n")
    
    # Read file
    print("\nReading /home/user/readme.txt:")
    content = fs.read_file("/home/user/readme.txt")
    print(f"  Content: {content}")
    
    # List directory
    print("\nListing /home/user:")
    files = fs.list_directory("/home/user")
    for file in files:
        print(f"  - {file}")
    
    # Write to file
    print("\nAppending to /var/log/system.log...")
    current = fs.read_file("/var/log/system.log")
    fs.write_file("/var/log/system.log", current + "Process started\n")
    
    # Read updated file
    print("\nReading updated /var/log/system.log:")
    print(f"  {fs.read_file('/var/log/system.log')}")
    
    # Test path normalization
    print("\nPath normalization:")
    print(f"  /home/user/../user/./readme.txt exists: {fs.exists('/home/user/../user/./readme.txt')}")
    
    # Delete file
    print("\nDeleting /home/user/readme.txt...")
    fs.delete("/home/user/readme.txt")
    print(f"  File exists: {fs.exists('/home/user/readme.txt')}")
