"""
Database configuration and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.models import Base
import json
import os
from datetime import datetime
from typing import Dict, Any


class DatabaseManager:
    def __init__(self, database_url: str = "sqlite:///./trading_simulator.db"):
        self.database_url = database_url
        self.engine = create_engine(database_url, connect_args={"check_same_thread": False})
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.create_tables()
        self.init_sample_data()
    
    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_db(self):
        """Get database session"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    def init_sample_data(self):
        """Initialize sample data for testing"""
        from core.models import Contract, ContractType, User
        
        db = next(self.get_db())
        
        # Check if sample data already exists
        if db.query(Contract).first() is not None:
            return
        
        # Create sample contracts
        sample_contracts = [
            Contract(
                symbol="GOLD2024DEC",
                contract_type=ContractType.GOLD_FUTURES,
                expiry_date=datetime(2024, 12, 31),
                contract_size=100.0,  # 100 troy ounces
                tick_size=0.01,
                initial_margin=5000.0,
                maintenance_margin=3500.0,
                is_active=True
            ),
            Contract(
                symbol="GOLD2025MAR",
                contract_type=ContractType.GOLD_FUTURES,
                expiry_date=datetime(2025, 3, 31),
                contract_size=100.0,
                tick_size=0.01,
                initial_margin=5200.0,
                maintenance_margin=3700.0,
                is_active=True
            ),
            Contract(
                symbol="GOLD2025JUN",
                contract_type=ContractType.GOLD_FUTURES,
                expiry_date=datetime(2025, 6, 30),
                contract_size=100.0,
                tick_size=0.01,
                initial_margin=5400.0,
                maintenance_margin=3900.0,
                is_active=True
            )
        ]
        
        for contract in sample_contracts:
            db.add(contract)
        
        # Create sample user
        sample_user = User(
            username="demo_trader",
            email="demo@example.com",
            account_balance=100000.0,
            margin_available=100000.0,
            is_active=True
        )
        db.add(sample_user)
        
        db.commit()


class JSONStorage:
    """
    JSON-based storage for persisting simulator state
    """
    def __init__(self, storage_dir: str = "./storage"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
    
    def save_trades(self, trades: Dict[str, Any]):
        """Save trades to JSON file"""
        filepath = os.path.join(self.storage_dir, "trades.json")
        with open(filepath, 'w') as f:
            json.dump(trades, f, indent=2, default=str)
    
    def load_trades(self) -> Dict[str, Any]:
        """Load trades from JSON file"""
        filepath = os.path.join(self.storage_dir, "trades.json")
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return {}
    
    def save_positions(self, positions: Dict[str, Any]):
        """Save positions to JSON file"""
        filepath = os.path.join(self.storage_dir, "positions.json")
        with open(filepath, 'w') as f:
            json.dump(positions, f, indent=2, default=str)
    
    def load_positions(self) -> Dict[str, Any]:
        """Load positions from JSON file"""
        filepath = os.path.join(self.storage_dir, "positions.json")
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return {}
    
    def save_user_decisions(self, decisions: Dict[str, Any]):
        """Save user decisions to JSON file"""
        filepath = os.path.join(self.storage_dir, "user_decisions.json")
        with open(filepath, 'w') as f:
            json.dump(decisions, f, indent=2, default=str)
    
    def load_user_decisions(self) -> Dict[str, Any]:
        """Load user decisions from JSON file"""
        filepath = os.path.join(self.storage_dir, "user_decisions.json")
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return {}
    
    def save_ai_analysis(self, analysis: Dict[str, Any]):
        """Save AI analysis to JSON file"""
        filepath = os.path.join(self.storage_dir, "ai_analysis.json")
        with open(filepath, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
    
    def load_ai_analysis(self) -> Dict[str, Any]:
        """Load AI analysis from JSON file"""
        filepath = os.path.join(self.storage_dir, "ai_analysis.json")
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return {}


# Global instances
db_manager = DatabaseManager()
json_storage = JSONStorage()