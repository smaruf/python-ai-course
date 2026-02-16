"""
Functional Pipeline Implementation

Tests: Lazy execution, functional composition, higher-order functions

Demonstrates:
- Functional programming patterns
- Lazy evaluation for efficiency
- Pipeline composition
- Functional transformations (map, filter, reduce)
"""

from typing import Callable, Iterator, Any, Optional, List, Iterable
from functools import reduce
import threading


class LazyPipeline:
    """
    Lazy evaluation pipeline for data transformation.
    
    Features:
    - Deferred execution (lazy evaluation)
    - Pipeline composition
    - Memory efficient (processes one item at a time)
    - Functional transformations
    """
    
    def __init__(self, source: Iterable):
        """
        Initialize lazy pipeline.
        
        Args:
            source: Source iterable
        """
        self.source = source
        self.operations = []
    
    def map(self, func: Callable[[Any], Any]) -> 'LazyPipeline':
        """
        Add a map operation to the pipeline.
        
        Args:
            func: Transformation function
            
        Returns:
            Self for chaining
        """
        self.operations.append(('map', func))
        return self
    
    def filter(self, predicate: Callable[[Any], bool]) -> 'LazyPipeline':
        """
        Add a filter operation to the pipeline.
        
        Args:
            predicate: Filter predicate
            
        Returns:
            Self for chaining
        """
        self.operations.append(('filter', predicate))
        return self
    
    def flat_map(self, func: Callable[[Any], Iterable]) -> 'LazyPipeline':
        """
        Add a flat_map operation to the pipeline.
        
        Args:
            func: Function that returns an iterable
            
        Returns:
            Self for chaining
        """
        self.operations.append(('flat_map', func))
        return self
    
    def take(self, n: int) -> 'LazyPipeline':
        """
        Take first n elements.
        
        Args:
            n: Number of elements to take
            
        Returns:
            Self for chaining
        """
        self.operations.append(('take', n))
        return self
    
    def skip(self, n: int) -> 'LazyPipeline':
        """
        Skip first n elements.
        
        Args:
            n: Number of elements to skip
            
        Returns:
            Self for chaining
        """
        self.operations.append(('skip', n))
        return self
    
    def distinct(self) -> 'LazyPipeline':
        """
        Keep only distinct elements.
        
        Returns:
            Self for chaining
        """
        self.operations.append(('distinct', None))
        return self
    
    def __iter__(self) -> Iterator:
        """
        Execute the pipeline lazily.
        
        Yields:
            Transformed elements
        """
        iterator = iter(self.source)
        seen = set()
        count = 0
        skip_count = 0
        take_count = float('inf')
        
        for item in iterator:
            # Apply operations in sequence
            current = item
            should_skip = False
            
            for op_type, op_arg in self.operations:
                if op_type == 'map':
                    current = op_arg(current)
                
                elif op_type == 'filter':
                    if not op_arg(current):
                        should_skip = True
                        break
                
                elif op_type == 'flat_map':
                    # Flatten the result
                    for sub_item in op_arg(current):
                        yield sub_item
                    should_skip = True
                    break
                
                elif op_type == 'skip':
                    if skip_count < op_arg:
                        skip_count += 1
                        should_skip = True
                        break
                
                elif op_type == 'take':
                    take_count = op_arg
                
                elif op_type == 'distinct':
                    if current in seen:
                        should_skip = True
                        break
                    seen.add(current)
            
            if not should_skip:
                if count >= take_count:
                    break
                yield current
                count += 1
    
    def to_list(self) -> List:
        """
        Execute pipeline and collect results into a list.
        
        Returns:
            List of results
        """
        return list(self)
    
    def reduce(self, func: Callable[[Any, Any], Any], initial: Optional[Any] = None) -> Any:
        """
        Reduce the pipeline to a single value.
        
        Args:
            func: Reduction function
            initial: Initial value
            
        Returns:
            Reduced value
        """
        if initial is None:
            return reduce(func, self)
        return reduce(func, self, initial)
    
    def for_each(self, action: Callable[[Any], None]):
        """
        Execute an action for each element.
        
        Args:
            action: Action to execute
        """
        for item in self:
            action(item)
    
    def count(self) -> int:
        """
        Count elements in the pipeline.
        
        Returns:
            Element count
        """
        return sum(1 for _ in self)
    
    def first(self, default: Optional[Any] = None) -> Any:
        """
        Get first element.
        
        Args:
            default: Default value if empty
            
        Returns:
            First element or default
        """
        for item in self:
            return item
        return default
    
    def any(self, predicate: Callable[[Any], bool]) -> bool:
        """
        Check if any element matches predicate.
        
        Args:
            predicate: Predicate function
            
        Returns:
            True if any element matches
        """
        for item in self:
            if predicate(item):
                return True
        return False
    
    def all(self, predicate: Callable[[Any], bool]) -> bool:
        """
        Check if all elements match predicate.
        
        Args:
            predicate: Predicate function
            
        Returns:
            True if all elements match
        """
        for item in self:
            if not predicate(item):
                return False
        return True


class Pipeline:
    """
    Eager evaluation pipeline for immediate execution.
    
    Features:
    - Immediate execution of transformations
    - Intermediate results stored
    - Method chaining
    """
    
    def __init__(self, data: List):
        """
        Initialize pipeline.
        
        Args:
            data: Initial data
        """
        self.data = data
    
    def map(self, func: Callable[[Any], Any]) -> 'Pipeline':
        """Apply transformation to all elements."""
        self.data = [func(item) for item in self.data]
        return self
    
    def filter(self, predicate: Callable[[Any], bool]) -> 'Pipeline':
        """Filter elements by predicate."""
        self.data = [item for item in self.data if predicate(item)]
        return self
    
    def flat_map(self, func: Callable[[Any], Iterable]) -> 'Pipeline':
        """Flat map transformation."""
        result = []
        for item in self.data:
            result.extend(func(item))
        self.data = result
        return self
    
    def sort(self, key: Optional[Callable] = None, reverse: bool = False) -> 'Pipeline':
        """Sort elements."""
        self.data = sorted(self.data, key=key, reverse=reverse)
        return self
    
    def distinct(self) -> 'Pipeline':
        """Keep only distinct elements."""
        seen = set()
        result = []
        for item in self.data:
            if item not in seen:
                seen.add(item)
                result.append(item)
        self.data = result
        return self
    
    def take(self, n: int) -> 'Pipeline':
        """Take first n elements."""
        self.data = self.data[:n]
        return self
    
    def skip(self, n: int) -> 'Pipeline':
        """Skip first n elements."""
        self.data = self.data[n:]
        return self
    
    def reduce(self, func: Callable[[Any, Any], Any], initial: Optional[Any] = None) -> Any:
        """Reduce to a single value."""
        if initial is None:
            return reduce(func, self.data)
        return reduce(func, self.data, initial)
    
    def to_list(self) -> List:
        """Get result as list."""
        return self.data.copy()
    
    def count(self) -> int:
        """Count elements."""
        return len(self.data)
    
    def first(self, default: Optional[Any] = None) -> Any:
        """Get first element."""
        return self.data[0] if self.data else default
    
    def group_by(self, key_func: Callable[[Any], Any]) -> dict:
        """
        Group elements by key function.
        
        Args:
            key_func: Function to extract grouping key
            
        Returns:
            Dictionary of key -> list of elements
        """
        groups = {}
        for item in self.data:
            key = key_func(item)
            if key not in groups:
                groups[key] = []
            groups[key].append(item)
        return groups


class ParallelPipeline:
    """
    Parallel execution pipeline for concurrent processing.
    
    Features:
    - Parallel map operations
    - Thread-based parallelism
    - Configurable worker count
    """
    
    def __init__(self, data: List, workers: int = 4):
        """
        Initialize parallel pipeline.
        
        Args:
            data: Initial data
            workers: Number of worker threads
        """
        self.data = data
        self.workers = workers
    
    def map(self, func: Callable[[Any], Any]) -> 'ParallelPipeline':
        """
        Apply transformation in parallel.
        
        Args:
            func: Transformation function
            
        Returns:
            Self for chaining
        """
        from concurrent.futures import ThreadPoolExecutor
        
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            self.data = list(executor.map(func, self.data))
        
        return self
    
    def filter(self, predicate: Callable[[Any], bool]) -> 'ParallelPipeline':
        """Filter elements (sequential)."""
        self.data = [item for item in self.data if predicate(item)]
        return self
    
    def to_list(self) -> List:
        """Get result as list."""
        return self.data.copy()


if __name__ == "__main__":
    print("Functional Pipeline Example")
    print("=" * 60)
    
    # Lazy pipeline example
    print("\n1. Lazy Pipeline (deferred execution)")
    print("-" * 60)
    
    # Source data
    numbers = range(1, 11)
    
    # Build pipeline (no execution yet)
    pipeline = (LazyPipeline(numbers)
                .filter(lambda x: x % 2 == 0)  # Keep even numbers
                .map(lambda x: x * x)           # Square them
                .map(lambda x: f"Square: {x}")) # Format
    
    print("Pipeline defined (not executed yet)")
    print("\nExecuting pipeline:")
    for result in pipeline:
        print(f"  {result}")
    
    # Eager pipeline example
    print("\n2. Eager Pipeline (immediate execution)")
    print("-" * 60)
    
    words = ["apple", "banana", "apricot", "cherry", "avocado"]
    
    result = (Pipeline(words)
              .filter(lambda w: w.startswith('a'))  # Start with 'a'
              .map(lambda w: w.upper())             # Uppercase
              .sort()                               # Sort
              .to_list())
    
    print(f"Result: {result}")
    
    # Complex transformation
    print("\n3. Complex Transformation")
    print("-" * 60)
    
    data = [1, 2, 3, 4, 5]
    
    # Flat map example
    result = (LazyPipeline(data)
              .flat_map(lambda x: [x, x * 10])  # Expand each number
              .filter(lambda x: x > 5)           # Filter
              .to_list())
    
    print(f"Flat map result: {result}")
    
    # Reduce example
    sum_result = (LazyPipeline(range(1, 6))
                  .map(lambda x: x * 2)
                  .reduce(lambda a, b: a + b, 0))
    
    print(f"Sum of doubled numbers 1-5: {sum_result}")
    
    # Group by example
    print("\n4. Grouping")
    print("-" * 60)
    
    people = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
        {"name": "Charlie", "age": 30},
        {"name": "Diana", "age": 25}
    ]
    
    grouped = Pipeline(people).group_by(lambda p: p["age"])
    
    print("People grouped by age:")
    for age, group in grouped.items():
        print(f"  Age {age}: {[p['name'] for p in group]}")
    
    # Parallel pipeline
    print("\n5. Parallel Processing")
    print("-" * 60)
    
    def slow_square(x):
        import time
        time.sleep(0.01)  # Simulate slow operation
        return x * x
    
    import time
    start = time.time()
    result = ParallelPipeline([1, 2, 3, 4, 5], workers=3).map(slow_square).to_list()
    elapsed = time.time() - start
    
    print(f"Parallel result: {result}")
    print(f"Elapsed time: {elapsed:.3f}s")
