# python-ai-course
### Completing AI task using python as on boarding training

-- run hash-tag `python app.py` 

-- apply curl script:
#### Hash-tag
```
curl -X POST http://localhost:5000/process \
-H 'Content-Type: application/json' \
-d '{"text": "Let us focus on eating more natural and artificial products."}'
```

#### Add more keyword
```
curl -X POST http://localhost:5000/keyword \
-H 'Content-Type: application/json' \
-d '{"keyword": "healthy"}'
```

#### Using elastic search
```
curl -X POST http://localhost:5000/process -H 'Content-Type: application/json' -d '{"text": "Explore natural solutions and artificial intelligence."}'
```
-- and
```
curl -X POST http://localhost:5000/keyword -H 'Content-Type: application/json' -d '{"keyword": "artificial"}'
```

# Basic Sorting Algorithms

This repository contains Python implementations of basic sorting algorithms including Bubble Sort, Selection Sort, Insertion Sort, Merge Sort, and Quick Sort, along with unit tests to verify the correctness of each algorithm.

## Overview

Sorting is a common operation in many applications. This project provides simple implementations of several fundamental sorting algorithms, making it a valuable resource for educational purposes and for developers needing to understand the mechanics of data sorting techniques.

### Sorting Algorithms Included

- **Bubble Sort**: A simple comparison-based algorithm that repeatedly steps through the list, compares adjacent elements, and swaps them if they are in the wrong order. 
- **Selection Sort**: This algorithm segments the list into two parts: sorted and unsorted. It continuously removes the smallest element of the unsorted segment and appends it to the sorted segment.
- **Insertion Sort**: Builds the final sorted array one item at a time by comparing each new item with the previously sorted items and inserting it into the correct position.
- **Merge Sort**: A divide-and-conquer algorithm that splits the list into equal halves, sorts them, and then merges them back together.
- **Quick Sort**: Utilizes a pivot element to partition the array into two parts, then sorts each part independently.

## Running the Tests

To run the unit tests and verify the correctness of the sorting algorithms, execute the following command:

```bash
python sorting_algorithms.py
