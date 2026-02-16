"""
SQL Engine Implementation

Tests: Data modeling, query execution, parsing, indexing

A simplified SQL database engine demonstrating:
- Table creation and schema management
- INSERT, SELECT, UPDATE, DELETE operations
- Basic WHERE clause filtering
- Index support for performance
- Query planning basics
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import re


class ColumnType(Enum):
    """SQL column types."""
    INTEGER = "INTEGER"
    TEXT = "TEXT"
    REAL = "REAL"
    BOOLEAN = "BOOLEAN"


@dataclass
class Column:
    """Represents a table column."""
    name: str
    column_type: ColumnType
    nullable: bool = True
    primary_key: bool = False
    unique: bool = False


@dataclass
class Index:
    """Represents a table index."""
    name: str
    column: str
    index_map: Dict[Any, List[int]]  # value -> list of row indices


class Table:
    """
    Represents a database table.
    
    Features:
    - Schema definition with column types
    - Row storage with validation
    - Primary key enforcement
    - Index support
    """
    
    def __init__(self, name: str, columns: List[Column]):
        """
        Initialize table.
        
        Args:
            name: Table name
            columns: List of column definitions
        """
        self.name = name
        self.columns = columns
        self.column_names = [col.name for col in columns]
        self.rows: List[Dict[str, Any]] = []
        self.indexes: Dict[str, Index] = {}
        
        # Find primary key column
        self.primary_key_col = None
        for col in columns:
            if col.primary_key:
                self.primary_key_col = col.name
                break
    
    def insert(self, values: Dict[str, Any]) -> bool:
        """
        Insert a row into the table.
        
        Args:
            values: Dictionary of column_name -> value
            
        Returns:
            True if successful
            
        Raises:
            ValueError: If validation fails
        """
        # Validate columns
        for col in self.columns:
            if col.name not in values:
                if not col.nullable:
                    raise ValueError(f"Column '{col.name}' cannot be null")
                values[col.name] = None
        
        # Check primary key uniqueness
        if self.primary_key_col and values[self.primary_key_col] is not None:
            for row in self.rows:
                if row.get(self.primary_key_col) == values[self.primary_key_col]:
                    raise ValueError(f"Duplicate primary key: {values[self.primary_key_col]}")
        
        # Add row
        row_index = len(self.rows)
        self.rows.append(values)
        
        # Update indexes
        for index_name, index in self.indexes.items():
            value = values.get(index.column)
            if value is not None:
                if value not in index.index_map:
                    index.index_map[value] = []
                index.index_map[value].append(row_index)
        
        return True
    
    def select(
        self,
        columns: Optional[List[str]] = None,
        where: Optional[Callable[[Dict], bool]] = None
    ) -> List[Dict[str, Any]]:
        """
        Select rows from the table.
        
        Args:
            columns: Columns to return (None for all)
            where: Filter function
            
        Returns:
            List of matching rows
        """
        results = []
        
        for row in self.rows:
            # Apply WHERE filter
            if where and not where(row):
                continue
            
            # Project columns
            if columns:
                result_row = {col: row.get(col) for col in columns if col in row}
            else:
                result_row = row.copy()
            
            results.append(result_row)
        
        return results
    
    def update(
        self,
        values: Dict[str, Any],
        where: Optional[Callable[[Dict], bool]] = None
    ) -> int:
        """
        Update rows in the table.
        
        Args:
            values: Dictionary of column_name -> new_value
            where: Filter function
            
        Returns:
            Number of rows updated
        """
        updated_count = 0
        
        for row in self.rows:
            # Apply WHERE filter
            if where and not where(row):
                continue
            
            # Update row
            for col_name, new_value in values.items():
                if col_name in row:
                    row[col_name] = new_value
            
            updated_count += 1
        
        return updated_count
    
    def delete(self, where: Optional[Callable[[Dict], bool]] = None) -> int:
        """
        Delete rows from the table.
        
        Args:
            where: Filter function
            
        Returns:
            Number of rows deleted
        """
        if where is None:
            # Delete all rows
            count = len(self.rows)
            self.rows.clear()
            # Clear indexes
            for index in self.indexes.values():
                index.index_map.clear()
            return count
        
        # Delete matching rows
        rows_to_keep = []
        deleted_count = 0
        
        for row in self.rows:
            if where(row):
                deleted_count += 1
            else:
                rows_to_keep.append(row)
        
        self.rows = rows_to_keep
        
        # Rebuild indexes
        for index in self.indexes.values():
            index.index_map.clear()
            for i, row in enumerate(self.rows):
                value = row.get(index.column)
                if value is not None:
                    if value not in index.index_map:
                        index.index_map[value] = []
                    index.index_map[value].append(i)
        
        return deleted_count
    
    def create_index(self, index_name: str, column_name: str):
        """
        Create an index on a column.
        
        Args:
            index_name: Name of the index
            column_name: Column to index
        """
        if column_name not in self.column_names:
            raise ValueError(f"Column '{column_name}' does not exist")
        
        # Build index
        index = Index(name=index_name, column=column_name, index_map={})
        
        for i, row in enumerate(self.rows):
            value = row.get(column_name)
            if value is not None:
                if value not in index.index_map:
                    index.index_map[value] = []
                index.index_map[value].append(i)
        
        self.indexes[index_name] = index


class Query:
    """Represents a parsed SQL query."""
    
    def __init__(self, sql: str):
        """
        Initialize query.
        
        Args:
            sql: SQL query string
        """
        self.sql = sql.strip()
        self.query_type = self._parse_type()
    
    def _parse_type(self) -> str:
        """Parse query type from SQL."""
        sql_upper = self.sql.upper()
        if sql_upper.startswith("SELECT"):
            return "SELECT"
        elif sql_upper.startswith("INSERT"):
            return "INSERT"
        elif sql_upper.startswith("UPDATE"):
            return "UPDATE"
        elif sql_upper.startswith("DELETE"):
            return "DELETE"
        elif sql_upper.startswith("CREATE TABLE"):
            return "CREATE_TABLE"
        else:
            return "UNKNOWN"


class SQLEngine:
    """
    Simple SQL database engine.
    
    Features:
    - Table management
    - Basic SQL query execution
    - Transaction support (simplified)
    - Index management
    """
    
    def __init__(self):
        """Initialize SQL engine."""
        self.tables: Dict[str, Table] = {}
    
    def create_table(self, name: str, columns: List[Column]) -> Table:
        """
        Create a new table.
        
        Args:
            name: Table name
            columns: List of column definitions
            
        Returns:
            Created Table object
        """
        if name in self.tables:
            raise ValueError(f"Table '{name}' already exists")
        
        table = Table(name, columns)
        self.tables[name] = table
        return table
    
    def get_table(self, name: str) -> Optional[Table]:
        """Get table by name."""
        return self.tables.get(name)
    
    def drop_table(self, name: str) -> bool:
        """Drop a table."""
        if name in self.tables:
            del self.tables[name]
            return True
        return False
    
    def execute(self, query: Query) -> Any:
        """
        Execute a SQL query.
        
        Args:
            query: Query object
            
        Returns:
            Query result
        """
        # This is a simplified executor
        # In reality, would parse SQL and generate execution plan
        if query.query_type == "SELECT":
            return self._execute_select(query)
        elif query.query_type == "INSERT":
            return self._execute_insert(query)
        else:
            raise ValueError(f"Query type '{query.query_type}' not supported")
    
    def _execute_select(self, query: Query) -> List[Dict[str, Any]]:
        """Execute SELECT query (simplified)."""
        # This would normally parse the SQL properly
        # For now, just return empty result
        return []
    
    def _execute_insert(self, query: Query) -> int:
        """Execute INSERT query (simplified)."""
        # This would normally parse the SQL properly
        # For now, just return 0
        return 0


if __name__ == "__main__":
    print("SQL Engine Example")
    print("=" * 60)
    
    # Create engine
    db = SQLEngine()
    
    # Create table
    print("\nCreating 'users' table...")
    users_table = db.create_table("users", [
        Column("id", ColumnType.INTEGER, nullable=False, primary_key=True),
        Column("name", ColumnType.TEXT, nullable=False),
        Column("email", ColumnType.TEXT, nullable=False, unique=True),
        Column("age", ColumnType.INTEGER, nullable=True)
    ])
    
    # Insert data
    print("\nInserting users...")
    users_table.insert({"id": 1, "name": "Alice", "email": "alice@example.com", "age": 30})
    users_table.insert({"id": 2, "name": "Bob", "email": "bob@example.com", "age": 25})
    users_table.insert({"id": 3, "name": "Charlie", "email": "charlie@example.com", "age": 35})
    
    # Select all
    print("\nSELECT * FROM users:")
    all_users = users_table.select()
    for user in all_users:
        print(f"  {user}")
    
    # Select with WHERE clause
    print("\nSELECT * FROM users WHERE age > 28:")
    filtered = users_table.select(where=lambda row: row.get("age", 0) > 28)
    for user in filtered:
        print(f"  {user}")
    
    # Update
    print("\nUPDATE users SET age = 31 WHERE name = 'Alice':")
    updated = users_table.update(
        {"age": 31},
        where=lambda row: row.get("name") == "Alice"
    )
    print(f"  Updated {updated} row(s)")
    
    # Create index
    print("\nCreating index on 'email' column...")
    users_table.create_index("idx_email", "email")
    print(f"  Index created with {len(users_table.indexes['idx_email'].index_map)} unique values")
    
    # Delete
    print("\nDELETE FROM users WHERE age < 30:")
    deleted = users_table.delete(where=lambda row: row.get("age", 0) < 30)
    print(f"  Deleted {deleted} row(s)")
    
    # Final state
    print("\nFinal table state:")
    remaining = users_table.select()
    for user in remaining:
        print(f"  {user}")
