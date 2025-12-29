"""
Basic Banking Example

Demonstrates core banking operations
"""

from decimal import Decimal
from src.bank.services import BankingService
from src.bank.models import AccountCreate, AccountType


def main():
    """Run banking examples"""
    print("=" * 60)
    print("FINTECH TOOLS - BANKING MODULE EXAMPLE")
    print("=" * 60)
    print()
    
    # Initialize banking service
    service = BankingService()
    
    # Example 1: Create accounts
    print("1. Creating Bank Accounts")
    print("-" * 60)
    
    account1 = service.create_account(AccountCreate(
        account_number="1234567890",
        account_type=AccountType.SAVINGS,
        customer_name="John Doe",
        initial_balance=Decimal("5000.00")
    ))
    print(f"✓ Created: {account1.customer_name} - {account1.account_number}")
    print(f"  Type: {account1.account_type}, Balance: ${account1.balance}")
    
    account2 = service.create_account(AccountCreate(
        account_number="0987654321",
        account_type=AccountType.CHECKING,
        customer_name="Jane Smith",
        initial_balance=Decimal("3000.00")
    ))
    print(f"✓ Created: {account2.customer_name} - {account2.account_number}")
    print(f"  Type: {account2.account_type}, Balance: ${account2.balance}")
    print()
    
    # Example 2: Check balance
    print("2. Balance Inquiry")
    print("-" * 60)
    balance = service.get_balance("1234567890")
    print(f"Account: {balance.account_number}")
    print(f"Balance: ${balance.balance} {balance.currency}")
    print(f"Available: ${balance.available_balance}")
    print()
    
    # Example 3: Deposit
    print("3. Deposit Transaction")
    print("-" * 60)
    deposit_tx = service.deposit("1234567890", Decimal("1000.00"))
    print(f"✓ Deposit successful")
    print(f"  Transaction ID: {deposit_tx.transaction_id}")
    print(f"  Amount: ${deposit_tx.amount}")
    print(f"  Status: {deposit_tx.status}")
    
    new_balance = service.get_balance("1234567890")
    print(f"  New Balance: ${new_balance.balance}")
    print()
    
    # Example 4: Withdrawal
    print("4. Withdrawal Transaction")
    print("-" * 60)
    withdrawal_tx = service.withdraw("1234567890", Decimal("500.00"))
    print(f"✓ Withdrawal successful")
    print(f"  Transaction ID: {withdrawal_tx.transaction_id}")
    print(f"  Amount: ${withdrawal_tx.amount}")
    print(f"  Status: {withdrawal_tx.status}")
    
    new_balance = service.get_balance("1234567890")
    print(f"  New Balance: ${new_balance.balance}")
    print()
    
    # Example 5: Transfer
    print("5. Transfer Between Accounts")
    print("-" * 60)
    transfer_tx = service.transfer(
        "1234567890",
        "0987654321",
        Decimal("750.00")
    )
    print(f"✓ Transfer successful")
    print(f"  Transaction ID: {transfer_tx.transaction_id}")
    print(f"  From: {transfer_tx.from_account}")
    print(f"  To: {transfer_tx.to_account}")
    print(f"  Amount: ${transfer_tx.amount}")
    
    balance1 = service.get_balance("1234567890")
    balance2 = service.get_balance("0987654321")
    print(f"  Account 1 Balance: ${balance1.balance}")
    print(f"  Account 2 Balance: ${balance2.balance}")
    print()
    
    # Example 6: Transaction History
    print("6. Transaction History")
    print("-" * 60)
    history = service.get_transaction_history("1234567890", page=1, page_size=10)
    print(f"Account: {history.account_number}")
    print(f"Total Transactions: {history.total_count}")
    print(f"\nRecent Transactions:")
    
    for tx in history.transactions:
        print(f"  - {tx.transaction_type.value}: ${tx.amount} ({tx.status.value})")
        print(f"    ID: {tx.transaction_id}")
        print(f"    Time: {tx.timestamp}")
    
    print()
    print("=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
