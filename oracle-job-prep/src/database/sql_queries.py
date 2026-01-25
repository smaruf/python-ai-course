"""
SQL Queries and Database Examples for Oracle Interview Preparation

This module contains complex SQL queries and database operations
commonly asked in Oracle technical interviews.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Employee:
    """Employee data model"""
    employee_id: int
    first_name: str
    last_name: str
    email: str
    phone_number: str
    hire_date: datetime
    job_id: str
    salary: float
    commission_pct: Optional[float]
    manager_id: Optional[int]
    department_id: int


@dataclass
class Department:
    """Department data model"""
    department_id: int
    department_name: str
    manager_id: Optional[int]
    location_id: int


# Complex SQL Queries for Oracle Interviews
# These are example queries that demonstrate advanced SQL concepts

SQL_QUERIES = {
    "second_highest_salary": """
        -- Find the second highest salary in the employees table
        SELECT MAX(salary) as second_highest_salary
        FROM employees
        WHERE salary < (SELECT MAX(salary) FROM employees);
        
        -- Alternative using DENSE_RANK (Oracle specific)
        SELECT DISTINCT salary as second_highest_salary
        FROM (
            SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) as rank
            FROM employees
        )
        WHERE rank = 2;
    """,
    
    "nth_highest_salary": """
        -- Find the Nth highest salary (N = 5 in this example)
        SELECT DISTINCT salary
        FROM (
            SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) as rank
            FROM employees
        )
        WHERE rank = :n;
        
        -- Using ROWNUM (Oracle specific)
        SELECT salary
        FROM (
            SELECT DISTINCT salary
            FROM employees
            ORDER BY salary DESC
        )
        WHERE ROWNUM <= :n
        MINUS
        SELECT salary
        FROM (
            SELECT DISTINCT salary
            FROM employees
            ORDER BY salary DESC
        )
        WHERE ROWNUM < :n;
    """,
    
    "employees_above_average": """
        -- Find employees earning more than the average salary
        SELECT employee_id, first_name, last_name, salary
        FROM employees
        WHERE salary > (SELECT AVG(salary) FROM employees)
        ORDER BY salary DESC;
    """,
    
    "department_wise_salary": """
        -- Department-wise average, min, max salary
        SELECT 
            d.department_name,
            COUNT(e.employee_id) as employee_count,
            ROUND(AVG(e.salary), 2) as avg_salary,
            MIN(e.salary) as min_salary,
            MAX(e.salary) as max_salary,
            ROUND(STDDEV(e.salary), 2) as salary_std_dev
        FROM departments d
        LEFT JOIN employees e ON d.department_id = e.department_id
        GROUP BY d.department_id, d.department_name
        HAVING COUNT(e.employee_id) > 0
        ORDER BY avg_salary DESC;
    """,
    
    "hierarchical_query": """
        -- Employee hierarchy using CONNECT BY (Oracle specific)
        SELECT 
            LEVEL as hierarchy_level,
            LPAD(' ', 2 * (LEVEL - 1)) || first_name || ' ' || last_name as employee_name,
            employee_id,
            manager_id,
            job_id
        FROM employees
        START WITH manager_id IS NULL
        CONNECT BY PRIOR employee_id = manager_id
        ORDER SIBLINGS BY first_name;
        
        -- Alternative using recursive CTE (SQL:1999 standard)
        WITH RECURSIVE emp_hierarchy AS (
            -- Base case: top-level managers
            SELECT 
                employee_id, 
                first_name, 
                last_name, 
                manager_id,
                1 as level,
                CAST(first_name || ' ' || last_name AS VARCHAR(1000)) as path
            FROM employees
            WHERE manager_id IS NULL
            
            UNION ALL
            
            -- Recursive case: employees with managers
            SELECT 
                e.employee_id,
                e.first_name,
                e.last_name,
                e.manager_id,
                eh.level + 1,
                CAST(eh.path || ' -> ' || e.first_name || ' ' || e.last_name AS VARCHAR(1000))
            FROM employees e
            INNER JOIN emp_hierarchy eh ON e.manager_id = eh.employee_id
        )
        SELECT * FROM emp_hierarchy
        ORDER BY level, first_name;
    """,
    
    "running_total": """
        -- Calculate running total of salaries by department
        SELECT 
            employee_id,
            first_name,
            last_name,
            department_id,
            salary,
            SUM(salary) OVER (
                PARTITION BY department_id 
                ORDER BY employee_id
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) as running_total,
            ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) as salary_rank
        FROM employees
        ORDER BY department_id, employee_id;
    """,
    
    "duplicate_emails": """
        -- Find duplicate email addresses
        SELECT email, COUNT(*) as occurrence
        FROM employees
        GROUP BY email
        HAVING COUNT(*) > 1;
        
        -- Delete duplicates keeping the one with lowest employee_id
        DELETE FROM employees
        WHERE employee_id NOT IN (
            SELECT MIN(employee_id)
            FROM employees
            GROUP BY email
        );
    """,
    
    "pivot_example": """
        -- Pivot table: Show employee count by department and job
        SELECT *
        FROM (
            SELECT department_id, job_id
            FROM employees
        )
        PIVOT (
            COUNT(*)
            FOR job_id IN ('IT_PROG' as IT, 'SA_REP' as Sales, 'FI_ACCOUNT' as Finance)
        )
        ORDER BY department_id;
    """,
    
    "moving_average": """
        -- Calculate 3-month moving average of salaries
        SELECT 
            employee_id,
            hire_date,
            salary,
            ROUND(AVG(salary) OVER (
                ORDER BY hire_date
                ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
            ), 2) as moving_avg_3_months
        FROM employees
        ORDER BY hire_date;
    """,
    
    "gap_and_island": """
        -- Find gaps in employee IDs (missing IDs)
        SELECT 
            prev_id + 1 as gap_start,
            curr_id - 1 as gap_end
        FROM (
            SELECT 
                employee_id as curr_id,
                LAG(employee_id) OVER (ORDER BY employee_id) as prev_id
            FROM employees
        )
        WHERE curr_id - prev_id > 1;
    """,
    
    "self_join": """
        -- Find employees who earn more than their manager
        SELECT 
            e.employee_id,
            e.first_name || ' ' || e.last_name as employee_name,
            e.salary as employee_salary,
            m.first_name || ' ' || m.last_name as manager_name,
            m.salary as manager_salary
        FROM employees e
        INNER JOIN employees m ON e.manager_id = m.employee_id
        WHERE e.salary > m.salary;
    """,
    
    "date_functions": """
        -- Various date operations in Oracle
        SELECT 
            employee_id,
            hire_date,
            SYSDATE as current_date,
            ROUND(MONTHS_BETWEEN(SYSDATE, hire_date) / 12, 1) as years_employed,
            ADD_MONTHS(hire_date, 12) as first_anniversary,
            NEXT_DAY(hire_date, 'MONDAY') as next_monday_after_hire,
            LAST_DAY(hire_date) as last_day_of_hire_month,
            TRUNC(hire_date, 'YEAR') as year_start,
            TO_CHAR(hire_date, 'Day, DD Month YYYY') as formatted_date
        FROM employees
        ORDER BY hire_date DESC;
    """,
    
    "string_functions": """
        -- String manipulation examples
        SELECT 
            employee_id,
            first_name,
            last_name,
            UPPER(first_name || ' ' || last_name) as full_name_upper,
            LOWER(email) as email_lower,
            INITCAP(job_id) as job_title,
            SUBSTR(phone_number, 1, 3) as area_code,
            REPLACE(phone_number, '.', '-') as phone_formatted,
            LPAD(employee_id, 6, '0') as padded_id,
            LENGTH(first_name || last_name) as name_length,
            INSTR(email, '@') as at_position
        FROM employees;
    """,
    
    "analytical_functions": """
        -- Advanced analytical functions
        SELECT 
            employee_id,
            department_id,
            salary,
            -- Ranking functions
            ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) as row_num,
            RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) as rank,
            DENSE_RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) as dense_rank,
            -- Distribution functions
            PERCENT_RANK() OVER (PARTITION BY department_id ORDER BY salary) as pct_rank,
            CUME_DIST() OVER (PARTITION BY department_id ORDER BY salary) as cumulative_dist,
            NTILE(4) OVER (PARTITION BY department_id ORDER BY salary) as quartile,
            -- Window functions
            FIRST_VALUE(salary) OVER (PARTITION BY department_id ORDER BY salary DESC) as highest_sal,
            LAST_VALUE(salary) OVER (
                PARTITION BY department_id 
                ORDER BY salary DESC
                ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
            ) as lowest_sal,
            LAG(salary, 1, 0) OVER (PARTITION BY department_id ORDER BY salary) as prev_salary,
            LEAD(salary, 1, 0) OVER (PARTITION BY department_id ORDER BY salary) as next_salary
        FROM employees
        ORDER BY department_id, salary DESC;
    """,
    
    "transaction_example": """
        -- Transaction management example
        BEGIN;
        
        -- Update employee salary
        UPDATE employees 
        SET salary = salary * 1.10 
        WHERE department_id = 50;
        
        -- Insert audit record
        INSERT INTO salary_audit (employee_id, old_salary, new_salary, change_date)
        SELECT 
            employee_id, 
            salary / 1.10 as old_salary, 
            salary as new_salary, 
            SYSDATE
        FROM employees 
        WHERE department_id = 50;
        
        COMMIT;
        -- Use ROLLBACK; to undo changes if needed
    """
}


# Database Design Patterns
DATABASE_DESIGN_PATTERNS = {
    "normalization_example": """
        -- First Normal Form (1NF): Eliminate repeating groups
        -- Before:
        CREATE TABLE orders_bad (
            order_id NUMBER PRIMARY KEY,
            customer_name VARCHAR2(100),
            products VARCHAR2(1000)  -- Contains comma-separated products (BAD)
        );
        
        -- After:
        CREATE TABLE orders (
            order_id NUMBER PRIMARY KEY,
            customer_id NUMBER,
            order_date DATE
        );
        
        CREATE TABLE order_items (
            order_id NUMBER,
            product_id NUMBER,
            quantity NUMBER,
            FOREIGN KEY (order_id) REFERENCES orders(order_id)
        );
    """,
    
    "indexes": """
        -- Index creation examples
        
        -- B-tree index (default)
        CREATE INDEX idx_emp_dept ON employees(department_id);
        
        -- Composite index
        CREATE INDEX idx_emp_dept_salary ON employees(department_id, salary);
        
        -- Unique index
        CREATE UNIQUE INDEX idx_emp_email ON employees(email);
        
        -- Function-based index
        CREATE INDEX idx_emp_upper_name ON employees(UPPER(last_name));
        
        -- Bitmap index (for low cardinality columns)
        CREATE BITMAP INDEX idx_emp_gender ON employees(gender);
    """,
    
    "partitioning": """
        -- Table partitioning for large tables
        
        -- Range partitioning by date
        CREATE TABLE sales (
            sale_id NUMBER,
            sale_date DATE,
            amount NUMBER
        )
        PARTITION BY RANGE (sale_date) (
            PARTITION sales_2023 VALUES LESS THAN (TO_DATE('2024-01-01', 'YYYY-MM-DD')),
            PARTITION sales_2024 VALUES LESS THAN (TO_DATE('2025-01-01', 'YYYY-MM-DD')),
            PARTITION sales_2025 VALUES LESS THAN (TO_DATE('2026-01-01', 'YYYY-MM-DD'))
        );
        
        -- List partitioning
        CREATE TABLE customers (
            customer_id NUMBER,
            country VARCHAR2(50)
        )
        PARTITION BY LIST (country) (
            PARTITION customers_usa VALUES ('USA'),
            PARTITION customers_uk VALUES ('UK'),
            PARTITION customers_others VALUES (DEFAULT)
        );
    """
}


def print_query_examples():
    """Print all SQL query examples with descriptions"""
    print("Oracle SQL Query Examples for Interview Preparation")
    print("=" * 80)
    
    for query_name, query in SQL_QUERIES.items():
        print(f"\n{query_name.upper().replace('_', ' ')}")
        print("-" * 80)
        print(query.strip())
        print()


if __name__ == "__main__":
    print_query_examples()
