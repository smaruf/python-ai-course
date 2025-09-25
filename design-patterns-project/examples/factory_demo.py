"""
Factory Pattern Demo

This script demonstrates the Factory pattern using the employee management system.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.factory.employee_factory import EmployeeFactory

def main():
    """Demonstrate the Factory pattern with different employee types."""
    print("=== Factory Pattern Demo ===\n")
    
    factory = EmployeeFactory()
    
    # Create different types of employees
    employees = [
        ("fulltime", 25.0),
        ("parttime", 15.0),
        ("temporary", 20.0),
        ("contractor", 50.0)
    ]
    
    print("Creating employees using the Factory pattern:\n")
    
    for employee_type, hourly_rate in employees:
        try:
            employee = factory.create_employee(employee_type, hourly_rate)
            employee.say()
        except ValueError as e:
            print(f"Error creating {employee_type} employee: {e}")
    
    print("\n=== Testing invalid employee type ===")
    try:
        invalid_employee = factory.create_employee("invalid-type", 30.0)
    except ValueError as e:
        print(f"Expected error: {e}")
    
    print("\n=== Demo completed ===")

if __name__ == "__main__":
    main()