# Design Patterns Project

A collection of classic design pattern implementations in Python.

## Overview

This project demonstrates fundamental design patterns using practical Python examples. Each pattern is implemented with clear documentation, examples, and test cases to help understand when and how to use different design patterns.

## Project Structure

```
design-patterns-project/
├── src/                   # Pattern implementations
│   ├── factory/              # Factory pattern examples
│   │   └── employee_factory.py
│   ├── singleton/            # Singleton pattern
│   ├── observer/             # Observer pattern
│   └── strategy/             # Strategy pattern
├── tests/                 # Unit tests for all patterns
├── examples/              # Usage examples and demos
├── requirements.txt       # Dependencies
└── README.md             # This file
```

## Patterns Included

### Creational Patterns

#### Factory Pattern (`src/factory/employee_factory.py`)
- **Purpose**: Create objects without specifying exact classes
- **Use Case**: Employee management system with different employee types
- **Implementation**: 
  - Base `Employee` class with common interface
  - Specialized classes: `FullTimeEmployee`, `PartTimeEmployee`, `TemporaryEmployee`, `Contractor`
  - `EmployeeFactory` for object creation
- **Benefits**: 
  - Centralized object creation
  - Easy to add new employee types
  - Loose coupling between client and concrete classes

## Key Features

- **Clear Examples**: Real-world scenarios for each pattern
- **Comprehensive Documentation**: Detailed explanations and use cases
- **Unit Testing**: Verify pattern implementations work correctly
- **Educational Focus**: Learn when and why to use each pattern

## Installation

```bash
cd design-patterns-project
pip install -r requirements.txt
```

## Usage

### Factory Pattern Example
```python
from src.factory.employee_factory import EmployeeFactory

# Create different types of employees
factory = EmployeeFactory()

# Create a full-time employee
full_time = factory.create_employee("fulltime", 25.0)
full_time.say()  # Output: I am a FullTimeEmployee employee, and my hourly rate is 25.0.

# Create a contractor
contractor = factory.create_employee("contractor", 50.0)
contractor.say()  # Output: I am a Contractor employee, and my hourly rate is 50.0.

# Create a part-time employee
part_time = factory.create_employee("parttime", 15.0)
part_time.say()  # Output: I am a PartTimeEmployee employee, and my hourly rate is 15.0.
```

### Running Examples
```bash
# Run factory pattern demo
python examples/factory_demo.py

# Run all pattern demos
python examples/run_all_demos.py
```

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific pattern tests
python -m pytest tests/test_factory_pattern.py -v

# Run with coverage
python -m pytest tests/ --cov=src
```

## Pattern Benefits

### Factory Pattern
- **Flexibility**: Easy to add new employee types without changing existing code
- **Maintainability**: Centralized creation logic
- **Testability**: Easy to mock and test different employee types
- **Separation of Concerns**: Client code doesn't need to know about concrete classes

## Educational Value

This project demonstrates:
- **Object-Oriented Design**: Proper use of inheritance and polymorphism
- **SOLID Principles**: Single Responsibility, Open/Closed principles
- **Code Reusability**: How patterns promote code reuse
- **Real-World Applications**: Practical scenarios where patterns are useful

## Employee Types

The factory pattern example includes:

| Employee Type | Description | Typical Use Case |
|---------------|-------------|------------------|
| **FullTimeEmployee** | Regular full-time staff | Permanent positions with benefits |
| **PartTimeEmployee** | Part-time workers | Flexible scheduling, students |
| **TemporaryEmployee** | Short-term workers | Seasonal work, temporary projects |
| **Contractor** | Independent contractors | Specialized skills, project-based work |

## Testing

Comprehensive tests cover:
- **Pattern Correctness**: Verify patterns work as expected
- **Edge Cases**: Invalid inputs, error handling
- **Type Safety**: Ensure correct object types are created
- **Interface Compliance**: All objects follow expected interfaces

## Future Enhancements

Planned pattern additions:
- **Singleton Pattern**: Database connections, logging
- **Observer Pattern**: Event handling systems
- **Strategy Pattern**: Different algorithm implementations
- **Decorator Pattern**: Adding functionality dynamically
- **Command Pattern**: Undo/redo functionality
- **Builder Pattern**: Complex object construction

## Best Practices Demonstrated

- **Clear Interface Definition**: All employees follow the same interface
- **Error Handling**: Graceful handling of invalid employee types
- **Documentation**: Comprehensive docstrings and comments
- **Type Hints**: Modern Python typing for better code clarity
- **Testing**: Unit tests for all functionality

## Requirements

- Python 3.7+
- pytest (for testing)
- typing (for type hints - built-in for Python 3.5+)

## Contributing

Feel free to add new design patterns, improve existing implementations, or enhance documentation and examples!