"""
Banking System Implementation

Tests: Transaction modeling, consistency, ACID properties, concurrency

A simplified banking system demonstrating:
- Transaction processing with ACID properties
- Account management
- Concurrent transaction handling
- Balance consistency
- Transaction history
"""

from typing import List, Optional, Dict
from dataclasses import dataclass
from enum import Enum
import threading
import time
from datetime import datetime
import uuid


class TransactionStatus(Enum):
    """Transaction status enumeration."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class TransactionType(Enum):
    """Transaction type enumeration."""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"


@dataclass
class Transaction:
    """Represents a banking transaction."""
    transaction_id: str
    transaction_type: TransactionType
    amount: float
    from_account: Optional[str]
    to_account: Optional[str]
    timestamp: float
    status: TransactionStatus
    description: str = ""
    
    def to_dict(self) -> dict:
        """Convert transaction to dictionary."""
        return {
            'transaction_id': self.transaction_id,
            'type': self.transaction_type.value,
            'amount': self.amount,
            'from_account': self.from_account,
            'to_account': self.to_account,
            'timestamp': self.timestamp,
            'status': self.status.value,
            'description': self.description
        }


class Account:
    """
    Bank account with thread-safe operations.
    
    Features:
    - Thread-safe balance updates
    - Transaction history
    - Overdraft protection
    - Balance inquiries
    """
    
    def __init__(
        self,
        account_id: str,
        initial_balance: float = 0.0,
        allow_overdraft: bool = False,
        overdraft_limit: float = 0.0
    ):
        """
        Initialize bank account.
        
        Args:
            account_id: Unique account identifier
            initial_balance: Starting balance
            allow_overdraft: Whether to allow negative balance
            overdraft_limit: Maximum negative balance allowed
        """
        self.account_id = account_id
        self.balance = initial_balance
        self.allow_overdraft = allow_overdraft
        self.overdraft_limit = overdraft_limit
        self.transactions: List[Transaction] = []
        self.lock = threading.Lock()
    
    def deposit(self, amount: float, description: str = "") -> Transaction:
        """
        Deposit money into account.
        
        Args:
            amount: Amount to deposit
            description: Transaction description
            
        Returns:
            Transaction object
            
        Raises:
            ValueError: If amount is negative
        """
        if amount < 0:
            raise ValueError("Deposit amount must be positive")
        
        transaction = Transaction(
            transaction_id=str(uuid.uuid4()),
            transaction_type=TransactionType.DEPOSIT,
            amount=amount,
            from_account=None,
            to_account=self.account_id,
            timestamp=time.time(),
            status=TransactionStatus.PENDING,
            description=description
        )
        
        with self.lock:
            self.balance += amount
            transaction.status = TransactionStatus.COMPLETED
            self.transactions.append(transaction)
        
        return transaction
    
    def withdraw(self, amount: float, description: str = "") -> Transaction:
        """
        Withdraw money from account.
        
        Args:
            amount: Amount to withdraw
            description: Transaction description
            
        Returns:
            Transaction object
            
        Raises:
            ValueError: If amount is negative or insufficient funds
        """
        if amount < 0:
            raise ValueError("Withdrawal amount must be positive")
        
        transaction = Transaction(
            transaction_id=str(uuid.uuid4()),
            transaction_type=TransactionType.WITHDRAWAL,
            amount=amount,
            from_account=self.account_id,
            to_account=None,
            timestamp=time.time(),
            status=TransactionStatus.PENDING,
            description=description
        )
        
        with self.lock:
            new_balance = self.balance - amount
            
            # Check if withdrawal is allowed
            if not self.allow_overdraft and new_balance < 0:
                transaction.status = TransactionStatus.FAILED
                transaction.description += " (Insufficient funds)"
                self.transactions.append(transaction)
                raise ValueError("Insufficient funds")
            
            if self.allow_overdraft and new_balance < -self.overdraft_limit:
                transaction.status = TransactionStatus.FAILED
                transaction.description += " (Overdraft limit exceeded)"
                self.transactions.append(transaction)
                raise ValueError("Overdraft limit exceeded")
            
            self.balance = new_balance
            transaction.status = TransactionStatus.COMPLETED
            self.transactions.append(transaction)
        
        return transaction
    
    def get_balance(self) -> float:
        """Get current account balance."""
        with self.lock:
            return self.balance
    
    def get_transaction_history(
        self,
        limit: Optional[int] = None
    ) -> List[Transaction]:
        """
        Get transaction history.
        
        Args:
            limit: Maximum number of transactions to return
            
        Returns:
            List of transactions
        """
        with self.lock:
            if limit:
                return self.transactions[-limit:]
            return self.transactions.copy()


class BankingSystem:
    """
    Banking system managing multiple accounts and transactions.
    
    Features:
    - Account creation and management
    - Money transfers between accounts
    - Transaction atomicity
    - Deadlock prevention
    - Global transaction log
    """
    
    def __init__(self):
        """Initialize banking system."""
        self.accounts: Dict[str, Account] = {}
        self.global_transactions: List[Transaction] = []
        self.lock = threading.Lock()
    
    def create_account(
        self,
        account_id: str,
        initial_balance: float = 0.0,
        allow_overdraft: bool = False,
        overdraft_limit: float = 0.0
    ) -> Account:
        """
        Create a new bank account.
        
        Args:
            account_id: Unique account identifier
            initial_balance: Starting balance
            allow_overdraft: Whether to allow overdraft
            overdraft_limit: Maximum overdraft allowed
            
        Returns:
            Created Account object
            
        Raises:
            ValueError: If account already exists
        """
        with self.lock:
            if account_id in self.accounts:
                raise ValueError(f"Account {account_id} already exists")
            
            account = Account(
                account_id=account_id,
                initial_balance=initial_balance,
                allow_overdraft=allow_overdraft,
                overdraft_limit=overdraft_limit
            )
            self.accounts[account_id] = account
            return account
    
    def get_account(self, account_id: str) -> Optional[Account]:
        """Get account by ID."""
        with self.lock:
            return self.accounts.get(account_id)
    
    def transfer(
        self,
        from_account_id: str,
        to_account_id: str,
        amount: float,
        description: str = ""
    ) -> Transaction:
        """
        Transfer money between accounts (atomic operation).
        
        Args:
            from_account_id: Source account ID
            to_account_id: Destination account ID
            amount: Amount to transfer
            description: Transaction description
            
        Returns:
            Transaction object
            
        Raises:
            ValueError: If accounts don't exist or transfer fails
        """
        if amount <= 0:
            raise ValueError("Transfer amount must be positive")
        
        # Get accounts
        from_account = self.get_account(from_account_id)
        to_account = self.get_account(to_account_id)
        
        if not from_account:
            raise ValueError(f"Account {from_account_id} not found")
        if not to_account:
            raise ValueError(f"Account {to_account_id} not found")
        
        # Create transaction
        transaction = Transaction(
            transaction_id=str(uuid.uuid4()),
            transaction_type=TransactionType.TRANSFER,
            amount=amount,
            from_account=from_account_id,
            to_account=to_account_id,
            timestamp=time.time(),
            status=TransactionStatus.PENDING,
            description=description
        )
        
        # Acquire locks in consistent order to prevent deadlock
        # Always lock accounts in alphabetical order
        first_lock = from_account.lock if from_account_id < to_account_id else to_account.lock
        second_lock = to_account.lock if from_account_id < to_account_id else from_account.lock
        
        try:
            with first_lock:
                with second_lock:
                    # Check if withdrawal is possible
                    new_from_balance = from_account.balance - amount
                    
                    if not from_account.allow_overdraft and new_from_balance < 0:
                        transaction.status = TransactionStatus.FAILED
                        transaction.description += " (Insufficient funds)"
                        raise ValueError("Insufficient funds")
                    
                    if from_account.allow_overdraft and \
                       new_from_balance < -from_account.overdraft_limit:
                        transaction.status = TransactionStatus.FAILED
                        transaction.description += " (Overdraft limit exceeded)"
                        raise ValueError("Overdraft limit exceeded")
                    
                    # Perform transfer (atomic)
                    from_account.balance -= amount
                    to_account.balance += amount
                    
                    transaction.status = TransactionStatus.COMPLETED
                    
                    # Record in account histories
                    from_account.transactions.append(transaction)
                    to_account.transactions.append(transaction)
            
            # Record in global log
            with self.lock:
                self.global_transactions.append(transaction)
            
            return transaction
            
        except Exception as e:
            transaction.status = TransactionStatus.FAILED
            with self.lock:
                self.global_transactions.append(transaction)
            raise
    
    def get_total_balance(self) -> float:
        """Get total balance across all accounts."""
        with self.lock:
            return sum(account.get_balance() for account in self.accounts.values())
    
    def get_global_transaction_history(
        self,
        limit: Optional[int] = None
    ) -> List[Transaction]:
        """Get global transaction history."""
        with self.lock:
            if limit:
                return self.global_transactions[-limit:]
            return self.global_transactions.copy()


if __name__ == "__main__":
    print("Banking System Example")
    print("=" * 60)
    
    # Create banking system
    bank = BankingSystem()
    
    # Create accounts
    alice_account = bank.create_account("Alice", initial_balance=1000.0)
    bob_account = bank.create_account("Bob", initial_balance=500.0)
    charlie_account = bank.create_account("Charlie", initial_balance=0.0, 
                                         allow_overdraft=True, overdraft_limit=200.0)
    
    print(f"\nInitial balances:")
    print(f"  Alice: ${alice_account.get_balance():.2f}")
    print(f"  Bob: ${bob_account.get_balance():.2f}")
    print(f"  Charlie: ${charlie_account.get_balance():.2f}")
    
    # Perform transactions
    print("\nPerforming transactions...")
    
    # Deposit
    alice_account.deposit(500.0, "Salary")
    print(f"  Alice deposits $500")
    
    # Transfer
    bank.transfer("Alice", "Bob", 200.0, "Payment")
    print(f"  Alice transfers $200 to Bob")
    
    # Withdrawal
    bob_account.withdraw(100.0, "ATM withdrawal")
    print(f"  Bob withdraws $100")
    
    # Transfer with overdraft
    bank.transfer("Charlie", "Alice", 150.0, "Loan payment")
    print(f"  Charlie transfers $150 to Alice (using overdraft)")
    
    # Final balances
    print(f"\nFinal balances:")
    print(f"  Alice: ${alice_account.get_balance():.2f}")
    print(f"  Bob: ${bob_account.get_balance():.2f}")
    print(f"  Charlie: ${charlie_account.get_balance():.2f}")
    
    # Verify total balance conservation
    total = bank.get_total_balance()
    print(f"\nTotal balance in system: ${total:.2f}")
    
    # Show transaction history
    print("\nAlice's transaction history:")
    for tx in alice_account.get_transaction_history():
        print(f"  {tx.transaction_type.value}: ${tx.amount:.2f} - {tx.status.value}")
