"""
Banking Services

Core banking business logic and operations
"""

from typing import List, Optional, Dict
from datetime import datetime
from decimal import Decimal
import uuid
from .models import (
    Account, AccountCreate, AccountUpdate,
    Transaction, TransactionCreate,
    TransactionType, TransactionStatus,
    BalanceInquiry, TransactionHistory
)


class BankingService:
    """Banking service for account and transaction operations"""
    
    def __init__(self):
        # Mock database (replace with actual database in production)
        self.accounts: Dict[str, Account] = {}
        self.transactions: List[Transaction] = []
    
    def create_account(self, account_data: AccountCreate) -> Account:
        """
        Create a new bank account
        
        Args:
            account_data: Account creation data
            
        Returns:
            Account: Created account
            
        Raises:
            ValueError: If account already exists
        """
        if account_data.account_number in self.accounts:
            raise ValueError(f"Account {account_data.account_number} already exists")
        
        account = Account(
            id=len(self.accounts) + 1,
            account_number=account_data.account_number,
            account_type=account_data.account_type,
            customer_name=account_data.customer_name,
            balance=account_data.initial_balance,
            currency=account_data.currency,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.accounts[account_data.account_number] = account
        return account
    
    def get_account(self, account_number: str) -> Optional[Account]:
        """
        Get account by account number
        
        Args:
            account_number: Account number
            
        Returns:
            Account: Account object or None if not found
        """
        return self.accounts.get(account_number)
    
    def update_account(self, account_number: str, update_data: AccountUpdate) -> Optional[Account]:
        """
        Update account information
        
        Args:
            account_number: Account number
            update_data: Update data
            
        Returns:
            Account: Updated account or None if not found
        """
        account = self.accounts.get(account_number)
        if not account:
            return None
        
        if update_data.customer_name is not None:
            account.customer_name = update_data.customer_name
        if update_data.is_active is not None:
            account.is_active = update_data.is_active
        
        account.updated_at = datetime.utcnow()
        return account
    
    def get_balance(self, account_number: str) -> Optional[BalanceInquiry]:
        """
        Get account balance
        
        Args:
            account_number: Account number
            
        Returns:
            BalanceInquiry: Balance information or None if not found
        """
        account = self.accounts.get(account_number)
        if not account:
            return None
        
        return BalanceInquiry(
            account_number=account_number,
            balance=account.balance,
            currency=account.currency,
            available_balance=account.balance,  # Simplified - could subtract holds
            as_of_date=datetime.utcnow()
        )
    
    def deposit(self, account_number: str, amount: Decimal) -> Transaction:
        """
        Deposit money into an account
        
        Args:
            account_number: Account number
            amount: Amount to deposit
            
        Returns:
            Transaction: Deposit transaction
            
        Raises:
            ValueError: If account not found or invalid amount
        """
        account = self.accounts.get(account_number)
        if not account:
            raise ValueError(f"Account {account_number} not found")
        
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        # Update balance
        account.balance += amount
        account.updated_at = datetime.utcnow()
        
        # Create transaction
        transaction = Transaction(
            id=len(self.transactions) + 1,
            transaction_id=str(uuid.uuid4()),
            transaction_type=TransactionType.DEPOSIT,
            to_account=account_number,
            amount=amount,
            currency=account.currency,
            status=TransactionStatus.COMPLETED,
            description=f"Deposit to {account_number}",
            timestamp=datetime.utcnow()
        )
        
        self.transactions.append(transaction)
        return transaction
    
    def withdraw(self, account_number: str, amount: Decimal) -> Transaction:
        """
        Withdraw money from an account
        
        Args:
            account_number: Account number
            amount: Amount to withdraw
            
        Returns:
            Transaction: Withdrawal transaction
            
        Raises:
            ValueError: If account not found, insufficient balance, or invalid amount
        """
        account = self.accounts.get(account_number)
        if not account:
            raise ValueError(f"Account {account_number} not found")
        
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        
        if account.balance < amount:
            raise ValueError("Insufficient balance")
        
        # Update balance
        account.balance -= amount
        account.updated_at = datetime.utcnow()
        
        # Create transaction
        transaction = Transaction(
            id=len(self.transactions) + 1,
            transaction_id=str(uuid.uuid4()),
            transaction_type=TransactionType.WITHDRAWAL,
            from_account=account_number,
            amount=amount,
            currency=account.currency,
            status=TransactionStatus.COMPLETED,
            description=f"Withdrawal from {account_number}",
            timestamp=datetime.utcnow()
        )
        
        self.transactions.append(transaction)
        return transaction
    
    def transfer(self, from_account: str, to_account: str, amount: Decimal) -> Transaction:
        """
        Transfer money between accounts
        
        Args:
            from_account: Source account number
            to_account: Destination account number
            amount: Amount to transfer
            
        Returns:
            Transaction: Transfer transaction
            
        Raises:
            ValueError: If accounts not found, insufficient balance, or invalid amount
        """
        source = self.accounts.get(from_account)
        destination = self.accounts.get(to_account)
        
        if not source:
            raise ValueError(f"Source account {from_account} not found")
        if not destination:
            raise ValueError(f"Destination account {to_account} not found")
        
        if amount <= 0:
            raise ValueError("Transfer amount must be positive")
        
        if source.balance < amount:
            raise ValueError("Insufficient balance")
        
        # Update balances
        source.balance -= amount
        source.updated_at = datetime.utcnow()
        destination.balance += amount
        destination.updated_at = datetime.utcnow()
        
        # Create transaction
        transaction = Transaction(
            id=len(self.transactions) + 1,
            transaction_id=str(uuid.uuid4()),
            transaction_type=TransactionType.TRANSFER,
            from_account=from_account,
            to_account=to_account,
            amount=amount,
            currency=source.currency,
            status=TransactionStatus.COMPLETED,
            description=f"Transfer from {from_account} to {to_account}",
            timestamp=datetime.utcnow()
        )
        
        self.transactions.append(transaction)
        return transaction
    
    def get_transaction_history(
        self, 
        account_number: str, 
        page: int = 1, 
        page_size: int = 10
    ) -> Optional[TransactionHistory]:
        """
        Get transaction history for an account
        
        Args:
            account_number: Account number
            page: Page number (1-indexed)
            page_size: Number of transactions per page
            
        Returns:
            TransactionHistory: Transaction history or None if account not found
        """
        if account_number not in self.accounts:
            return None
        
        # Filter transactions for this account
        account_transactions = [
            t for t in self.transactions
            if t.from_account == account_number or t.to_account == account_number
        ]
        
        # Sort by timestamp (newest first)
        account_transactions.sort(key=lambda t: t.timestamp, reverse=True)
        
        # Paginate
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_transactions = account_transactions[start_idx:end_idx]
        
        return TransactionHistory(
            account_number=account_number,
            transactions=paginated_transactions,
            total_count=len(account_transactions),
            page=page,
            page_size=page_size
        )
