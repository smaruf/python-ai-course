# Algorithms and Data Structures Project

> **Part of [Python AI Course](../README.md)** - A comprehensive learning repository covering AI, algorithms, and real-world applications.  
> See also: [Sorting Algorithms](../sorting-algorithms-project/) | [Design Patterns](../design-patterns-project/)

A comprehensive collection of fundamental algorithms and data structure implementations.

## Overview

This project contains Python implementations of classic algorithms and data structures, complete with unit tests and detailed documentation. It's designed for educational purposes and provides both theoretical understanding and practical implementation examples.

## Project Structure

```
algorithms-and-data-structures/
├── src/                   # Core algorithm implementations
│   ├── dijkstra_search.py    # Dijkstra's shortest path algorithm
│   └── graph.py              # Graph data structure implementation
├── tests/                 # Unit tests
│   └── test_dijkstra.py      # Tests for Dijkstra algorithm
├── docs/                  # Documentation and LaTeX files
│   └── dijkstra_document.tex # Academic documentation
├── requirements.txt       # Dependencies
└── README.md             # This file
```

## Algorithms Included

### Graph Algorithms

#### Dijkstra's Shortest Path Algorithm (`src/dijkstra_search.py`)
- **Complexity**: O((V + E) log V) with priority queue
- **Use Cases**: GPS navigation, network routing, shortest path problems
- **Features**:
  - Finds shortest path from source to all vertices
  - Handles weighted graphs with non-negative edges
  - Returns distance array with shortest distances
- **Implementation**: Complete graph class with adjacency matrix representation

## Key Features

- **Educational Focus**: Clear, well-documented implementations
- **Comprehensive Testing**: Unit tests for all algorithms
- **Academic Documentation**: LaTeX documentation included
- **Modular Design**: Clean separation of concerns

## Installation

```bash
cd algorithms-and-data-structures
pip install -r requirements.txt
```

## Usage

### Dijkstra's Algorithm
```python
from src.dijkstra_search import Graph

# Create a graph with 9 vertices
g = Graph(9)

# Add edges (adjacency matrix representation)
g.graph = [
    [0, 4, 0, 0, 0, 0, 0, 8, 0],
    [4, 0, 8, 0, 0, 0, 0, 11, 0],
    [0, 8, 0, 7, 0, 4, 0, 0, 2],
    [0, 0, 7, 0, 9, 14, 0, 0, 0],
    [0, 0, 0, 9, 0, 10, 0, 0, 0],
    [0, 0, 4, 14, 10, 0, 2, 0, 0],
    [0, 0, 0, 0, 0, 2, 0, 1, 6],
    [8, 11, 0, 0, 0, 0, 1, 0, 7],
    [0, 0, 2, 0, 0, 0, 6, 7, 0]
]

# Find shortest distances from vertex 0
distances = g.dijkstra(0)
print("Shortest distances from vertex 0:", distances)
```

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_dijkstra.py -v

# Run with coverage
python -m pytest tests/ --cov=src
```

## Educational Value

This project is perfect for:
- **Algorithm Learning**: Understanding classic algorithms
- **Graph Theory**: Practical graph algorithm implementations
- **Computer Science Education**: Academic-level documentation
- **Interview Preparation**: Common algorithm questions
- **Research**: LaTeX documentation for academic use

## Documentation

### Academic Documentation
- `docs/dijkstra_document.tex` - Complete LaTeX documentation
- Theoretical analysis and complexity discussion
- Algorithm walkthrough with examples
- Suitable for academic submissions

### Code Documentation
- Comprehensive docstrings for all functions
- Clear variable naming and comments
- Step-by-step algorithm explanation

## Testing

The project includes comprehensive unit tests:
- **Correctness Testing**: Verify algorithm outputs
- **Edge Cases**: Empty graphs, single vertices, disconnected graphs
- **Performance Testing**: Large graph handling
- **Regression Testing**: Prevent breaking changes

## Requirements

- Python 3.7+
- pytest (for testing)
- LaTeX (optional, for document compilation)

## Algorithm Complexity

| Algorithm | Time Complexity | Space Complexity | Best For |
|-----------|----------------|------------------|----------|
| Dijkstra's | O((V + E) log V) | O(V) | Shortest paths, non-negative weights |

## Future Enhancements

Planned additions:
- A* Search Algorithm
- Bellman-Ford Algorithm
- Floyd-Warshall Algorithm
- Minimum Spanning Tree algorithms
- Tree data structures
- Hash table implementations

## Contributing

Feel free to add new algorithms, improve existing implementations, or enhance documentation!