class Employee:
    def __init__(self, hourly_rate):
        self.hourly_rate = hourly_rate

    def say(self):
        print(f"I am a {self.__class__.__name__} employee, and my hourly rate is {self.hourly_rate}.")

class FullTimeEmployee(Employee):
    def __init__(self, hourly_rate):
        super().__init__(hourly_rate)

class PartTimeEmployee(Employee):
    def __init__(self, hourly_rate):
        super().__init__(hourly_rate)

class TemporaryEmployee(Employee):
    def __init__(self, hourly_rate):
        super().__init__(hourly_rate)

class Contractor(Employee):
    def __init__(self, hourly_rate):
        super().__init__(hourly_rate)

class EmployeeFactory:
    @staticmethod
    def create_employee(employee_type, hourly_rate):
        """
        Factory method to create and return an employee instance based on the employee_type.
        
        Arguments:
        employee_type (str): Type of employee to create (fulltime, parttime, temporary, contractor).
        hourly_rate (float): The hourly rate for the employee.
        
        Returns:
        An instance of the specified Employee subclass.
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
