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
```

## AI Development Guidelines

This repository includes comprehensive guidelines for implementing AI features in software development projects.

### 📚 [AI Feature Guidelines](ai_feature_guidelines.md)

Complete guide covering:
- **LLMs, Prompt Engineering, RAG, Vector Databases, AI Agents**
- **Practical Python examples** based on real implementations
- **Progressive learning paths** from beginner to expert
- **Working code samples** you can run immediately
- **Best practices** and security considerations

**Example projects in this repository:**
- [Flight Tracker AI](ai-flight-tracker/) - Simple LLM integration with real-time data
- [Trading Simulator](nasdaq-cse/) - Advanced AI assistant with ML predictions  
- [Go Implementation](nasdaq-cse-go/) - Performance-optimized AI features

**Quick start:**
```bash
# Install dependencies
pip install -r requirements.txt

# Try the flight tracker AI
cd ai-flight-tracker
python flight_tracker.py

# Or run the trading simulator
cd nasdaq-cse  
python main.py
