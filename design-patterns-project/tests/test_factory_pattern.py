"""
Unit tests for the Factory pattern implementation.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from src.factory.employee_factory import (
    EmployeeFactory, Employee, FullTimeEmployee, 
    PartTimeEmployee, TemporaryEmployee, Contractor
)

class TestEmployeeFactory:
    """Test cases for the EmployeeFactory class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.factory = EmployeeFactory()
    
    def test_create_full_time_employee(self):
        """Test creating a full-time employee."""
        employee = self.factory.create_employee("full-time", 25.0)
        assert isinstance(employee, FullTimeEmployee)
        assert employee.hourly_rate == 25.0
    
    def test_create_part_time_employee(self):
        """Test creating a part-time employee."""
        employee = self.factory.create_employee("part-time", 15.0)
        assert isinstance(employee, PartTimeEmployee)
        assert employee.hourly_rate == 15.0
    
    def test_create_temporary_employee(self):
        """Test creating a temporary employee."""
        employee = self.factory.create_employee("temporary", 20.0)
        assert isinstance(employee, TemporaryEmployee)
        assert employee.hourly_rate == 20.0
    
    def test_create_contractor(self):
        """Test creating a contractor."""
        employee = self.factory.create_employee("contractor", 50.0)
        assert isinstance(employee, Contractor)
        assert employee.hourly_rate == 50.0
    
    def test_invalid_employee_type(self):
        """Test that invalid employee types raise ValueError."""
        with pytest.raises(ValueError, match="Unknown employee type"):
            self.factory.create_employee("invalid-type", 30.0)
    
    def test_all_employees_inherit_from_employee(self):
        """Test that all created employees inherit from Employee base class."""
        employee_types = ["full-time", "part-time", "temporary", "contractor"]
        
        for emp_type in employee_types:
            employee = self.factory.create_employee(emp_type, 25.0)
            assert isinstance(employee, Employee)
    
    def test_employee_say_method(self):
        """Test that all employees have the say method."""
        employee_types = ["full-time", "part-time", "temporary", "contractor"]
        
        for emp_type in employee_types:
            employee = self.factory.create_employee(emp_type, 25.0)
            # Should not raise any exception
            employee.say()
    
    def test_hourly_rate_assignment(self):
        """Test that hourly rates are correctly assigned."""
        rates = [10.0, 15.5, 20.25, 50.75]
        
        for rate in rates:
            employee = self.factory.create_employee("full-time", rate)
            assert employee.hourly_rate == rate

if __name__ == "__main__":
    pytest.main([__file__])