class Employee:
    """Base class representing a generic employee.

    Attributes:
        hourly_rate (float): The hourly pay rate for the employee.
    """

    def __init__(self, hourly_rate):
        """Initialise an Employee with the given hourly rate.

        Args:
            hourly_rate (float): The employee's hourly pay rate.
        """
        self.hourly_rate = hourly_rate

    def say(self):
        """Print a description of this employee including their type and hourly rate."""
        print(f"I am a {self.__class__.__name__} employee, and my hourly rate is {self.hourly_rate}.")

class FullTimeEmployee(Employee):
    """Employee subclass representing a full-time worker."""

    def __init__(self, hourly_rate):
        """Initialise a FullTimeEmployee with the given hourly rate.

        Args:
            hourly_rate (float): The employee's hourly pay rate.
        """
        super().__init__(hourly_rate)

class PartTimeEmployee(Employee):
    """Employee subclass representing a part-time worker."""

    def __init__(self, hourly_rate):
        """Initialise a PartTimeEmployee with the given hourly rate.

        Args:
            hourly_rate (float): The employee's hourly pay rate.
        """
        super().__init__(hourly_rate)

class TemporaryEmployee(Employee):
    """Employee subclass representing a temporary/seasonal worker."""

    def __init__(self, hourly_rate):
        """Initialise a TemporaryEmployee with the given hourly rate.

        Args:
            hourly_rate (float): The employee's hourly pay rate.
        """
        super().__init__(hourly_rate)

class Contractor(Employee):
    """Employee subclass representing an independent contractor."""

    def __init__(self, hourly_rate):
        """Initialise a Contractor with the given hourly rate.

        Args:
            hourly_rate (float): The contractor's hourly pay rate.
        """
        super().__init__(hourly_rate)

class EmployeeFactory:
    """Factory for creating Employee instances of various types.

    Centralises object creation so that client code does not need to import
    or reference concrete Employee subclasses directly.

    Example:
        >>> factory = EmployeeFactory()
        >>> emp = factory.create_employee("fulltime", 25.0)
        >>> isinstance(emp, FullTimeEmployee)
        True
    """

    @staticmethod
    def create_employee(employee_type, hourly_rate):
        """Create and return an Employee instance for the given type.

        Args:
            employee_type (str): Type of employee to create. Accepted values
                (case-insensitive): ``"fulltime"``, ``"parttime"``,
                ``"temporary"``, ``"contractor"``.
            hourly_rate (float): The hourly rate for the employee.

        Returns:
            Employee: An instance of the appropriate Employee subclass.

        Raises:
            ValueError: If *employee_type* is not one of the recognised values.

        Example:
            >>> EmployeeFactory.create_employee("contractor", 50.0).hourly_rate
            50.0
        """
        employee_type = employee_type.lower()
        if employee_type == 'fulltime':
            return FullTimeEmployee(hourly_rate)
        elif employee_type == 'parttime':
            return PartTimeEmployee(hourly_rate)
        elif employee_type == 'temporary':
            return TemporaryEmployee(hourly_rate)
        elif employee_type == 'contractor':
            return Contractor(hourly_rate)
        else:
            raise ValueError("Invalid employee type provided.")

# Example Usage:
factory = EmployeeFactory()

full_time_emp = factory.create_employee("fulltime", 25)
part_time_emp = factory.create_employee("parttime", 20)
temporary_emp = factory.create_employee("temporary", 18)
contractor_emp = factory.create_employee("contractor", 30)

full_time_emp.say()  # Output might be "I am a FullTimeEmployee employee, and my hourly rate is 25."
part_time_emp.say()
temporary_emp.say()
contractor_emp.say()
