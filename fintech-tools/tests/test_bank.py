"""
Tests for Banking Module
"""

import pytest
from decimal import Decimal
from src.bank.services import BankingService
from src.bank.models import AccountCreate, AccountType, TransactionType


@pytest.fixture
def banking_service():
    """Create a banking service instance"""
    return BankingService()


def test_create_account(banking_service):
    """Test account creation"""
    account_data = AccountCreate(
        account_number="1234567890",
        account_type=AccountType.SAVINGS,
        customer_name="John Doe",
        initial_balance=Decimal("1000.00")
    )
    
    account = banking_service.create_account(account_data)
    
    assert account is not None
    assert account.account_number == "1234567890"
    assert account.customer_name == "John Doe"
    assert account.balance == Decimal("1000.00")


def test_deposit(banking_service):
    """Test deposit transaction"""
    # Create account
    account_data = AccountCreate(
        account_number="1234567890",
        account_type=AccountType.SAVINGS,
        customer_name="John Doe",
        initial_balance=Decimal("1000.00")
    )
    banking_service.create_account(account_data)
    
    # Make deposit
    transaction = banking_service.deposit("1234567890", Decimal("500.00"))
    
    assert transaction is not None
    assert transaction.transaction_type == TransactionType.DEPOSIT
    assert transaction.amount == Decimal("500.00")
    
    # Check balance
    balance = banking_service.get_balance("1234567890")
    assert balance.balance == Decimal("1500.00")


def test_withdraw(banking_service):
    """Test withdrawal transaction"""
    # Create account
    account_data = AccountCreate(
        account_number="1234567890",
        account_type=AccountType.SAVINGS,
        customer_name="John Doe",
        initial_balance=Decimal("1000.00")
    )
    banking_service.create_account(account_data)
    
    # Make withdrawal
    transaction = banking_service.withdraw("1234567890", Decimal("300.00"))
    
    assert transaction is not None
    assert transaction.transaction_type == TransactionType.WITHDRAWAL
    assert transaction.amount == Decimal("300.00")
    
    # Check balance
    balance = banking_service.get_balance("1234567890")
    assert balance.balance == Decimal("700.00")


def test_transfer(banking_service):
    """Test transfer between accounts"""
    # Create two accounts
    account1_data = AccountCreate(
        account_number="1234567890",
        account_type=AccountType.SAVINGS,
        customer_name="John Doe",
        initial_balance=Decimal("1000.00")
    )
    account2_data = AccountCreate(
        account_number="0987654321",
        account_type=AccountType.CHECKING,
        customer_name="Jane Smith",
        initial_balance=Decimal("500.00")
    )
    
    banking_service.create_account(account1_data)
    banking_service.create_account(account2_data)
    
    # Transfer from account1 to account2
    transaction = banking_service.transfer(
        "1234567890",
        "0987654321",
        Decimal("200.00")
    )
    
    assert transaction is not None
    assert transaction.transaction_type == TransactionType.TRANSFER
    assert transaction.amount == Decimal("200.00")
    
    # Check balances
    balance1 = banking_service.get_balance("1234567890")
    balance2 = banking_service.get_balance("0987654321")
    
    assert balance1.balance == Decimal("800.00")
    assert balance2.balance == Decimal("700.00")


def test_insufficient_balance(banking_service):
    """Test withdrawal with insufficient balance"""
    # Create account
    account_data = AccountCreate(
        account_number="1234567890",
        account_type=AccountType.SAVINGS,
        customer_name="John Doe",
        initial_balance=Decimal("100.00")
    )
    banking_service.create_account(account_data)
    
    # Try to withdraw more than balance
    with pytest.raises(ValueError, match="Insufficient balance"):
        banking_service.withdraw("1234567890", Decimal("200.00"))
