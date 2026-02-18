# Sorting Algorithms Project

> **Part of [Python AI Course](../README.md)** - A comprehensive learning repository covering AI, algorithms, and real-world applications.  
> See also: [Algorithms & Data Structures](../algorithms-and-data-structures/) | [Design Patterns](../design-patterns-project/)

A comprehensive collection of sorting algorithm implementations with visualizations and animations.

## Overview

This project contains Python implementations of fundamental sorting algorithms, complete with unit tests and interactive animations. It's designed for educational purposes and provides both theoretical understanding and visual representation of how different sorting algorithms work.

## Project Structure

```
sorting-algorithms-project/
├── src/                    # Core algorithm implementations
│   ├── basic_sorting.py    # Basic sorting algorithms (bubble, selection, insertion, merge, quick)
│   └── radix_sort.py      # Radix sort implementation
├── animations/            # Interactive visualizations
│   ├── quicksort_animation.py
│   ├── radix_sort_animation.py
│   └── *_random.py        # Randomized data versions
├── tests/                 # Unit tests
├── requirements.txt       # Dependencies
└── README.md             # This file
```

## Algorithms Included

### Basic Sorting Algorithms (`src/basic_sorting.py`)
- **Bubble Sort**: O(n²) - Simple comparison-based algorithm
- **Selection Sort**: O(n²) - Finds minimum element and places it at beginning
- **Insertion Sort**: O(n²) - Builds sorted array one item at a time
- **Merge Sort**: O(n log n) - Divide-and-conquer approach
- **Quick Sort**: O(n log n) average - Partition-based sorting

### Advanced Algorithms
- **Radix Sort**: O(d × (n + k)) - Non-comparison based sorting for integers

## Interactive Animations

The project includes matplotlib-based animations that visualize how each algorithm works:

- `quicksort_animation.py` - Watch quicksort partition and sort data
- `radix_sort_animation.py` - See how radix sort processes digits
- Random data variants for testing with different inputs

## Installation

```bash
cd sorting-algorithms-project
pip install -r requirements.txt
```

## Usage

### Running Basic Algorithms
```bash
python src/basic_sorting.py
```

### Running Animations
```bash
# Quicksort animation
python animations/quicksort_animation.py

# Radix sort animation
python animations/radix_sort_animation.py
```

### Running Tests
```bash
python -m pytest tests/
```

## Educational Value

This project is perfect for:
- Learning sorting algorithm concepts
- Understanding time complexity differences
- Visualizing algorithm behavior
- Comparing algorithm performance
- Educational demonstrations

## Requirements

- Python 3.7+
- matplotlib (for animations)
- numpy (for data handling)
- pytest (for testing)

## Contributing

Feel free to add new sorting algorithms, improve animations, or enhance test coverage!