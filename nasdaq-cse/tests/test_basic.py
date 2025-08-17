"""
Basic tests for the trading simulator
"""
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from core.models import OrderSide, OrderType, OrderCreate
from oms.manager import order_manager
from market_data.provider import gold_price_provider, chart_generator
from ai_assistant.bot import trading_bot
from rms.manager import risk_manager


class TestMarketData:
    """Test market data functionality"""
    
    @pytest.mark.asyncio
    async def test_gold_price_simulation(self):
        """Test gold price simulation"""
        price = await gold_price_provider.get_current_price()
        
        assert isinstance(price, dict)
        assert 'price' in price
        assert 'bid' in price
        assert 'ask' in price
        assert 'timestamp' in price
        assert price['price'] > 0
        assert price['ask'] > price['bid']
    
    def test_chart_generation(self):
        """Test chart generation"""
        # Add some sample data
        gold_price_provider.price_history = [
            {
                'timestamp': '2024-01-01T12:00:00',
                'price': 2050.0,
                'bid': 2049.5,
                'ask': 2050.5,
                'volume': 500,
                'change_24h': 1.5,
                'change_percent': 0.001
            }
        ]
        
        chart_json = chart_generator.create_price_chart(24)
        assert isinstance(chart_json, str)
        assert len(chart_json) > 0


class TestAIAssistant:
    """Test AI assistant functionality"""
    
    @pytest.mark.asyncio
    async def test_trade_analysis(self):
        """Test trade opportunity analysis"""
        market_data = {
            'price': 2050.0,
            'volume': 500,
            'change_percent': 0.001
        }
        
        analysis = await trading_bot.analyze_trade_opportunity(market_data, [])
        
        assert isinstance(analysis, dict)
        assert 'predicted_direction' in analysis
        assert 'confidence_score' in analysis
        assert 'suggestion' in analysis
        assert analysis['predicted_direction'] in ['BULLISH', 'BEARISH']
    
    @pytest.mark.asyncio
    async def test_risk_analysis(self):
        """Test risk analysis"""
        positions = [
            {
                'quantity': 10,
                'avg_entry_price': 2000.0,
                'unrealized_pnl': 500.0,
                'realized_pnl': 0.0
            }
        ]
        
        analysis = await trading_bot.analyze_risk(positions, 100000.0)
        
        assert isinstance(analysis, dict)
        assert 'risk_level' in analysis
        assert 'exposure_ratio' in analysis
        assert 'recommendations' in analysis
        assert analysis['risk_level'] in ['LOW', 'MEDIUM', 'HIGH']
    
    @pytest.mark.asyncio
    async def test_chat_response(self):
        """Test chat response functionality"""
        context = {
            'market_data': {'price': 2050.0, 'change_percent': 0.001},
            'positions': [],
            'account_balance': 100000.0
        }
        
        response = await trading_bot.chat_response("What's the current gold price?", context)
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert "2050" in response or "price" in response.lower()


class TestOrderManagement:
    """Test order management functionality"""
    
    @pytest.mark.asyncio
    async def test_order_validation(self):
        """Test order validation"""
        # This is a basic test - in practice you'd use a test database
        order_request = {
            'contract_symbol': 'GOLD2024DEC',
            'side': 'BUY',
            'order_type': 'MARKET',
            'quantity': 1
        }
        
        # Mock database operations for testing
        with patch('oms.manager.db_manager.get_db') as mock_db:
            mock_session = MagicMock()
            mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_db.return_value.__exit__ = MagicMock(return_value=None)
            
            # Mock contract lookup
            mock_contract = MagicMock()
            mock_contract.id = 1
            mock_contract.symbol = 'GOLD2024DEC'
            mock_session.query().filter().first.return_value = mock_contract
            
            result = await order_manager.submit_order(1, order_request)
            
            # Should return some result structure
            assert isinstance(result, dict)


class TestRiskManagement:
    """Test risk management functionality"""
    
    @pytest.mark.asyncio
    async def test_pre_trade_risk_check(self):
        """Test pre-trade risk checking"""
        order_request = {
            'quantity': 1,
            'price': 2050.0,
            'contract_symbol': 'GOLD2024DEC'
        }
        
        # Mock database operations
        with patch('rms.manager.db_manager.get_db') as mock_db:
            mock_session = MagicMock()
            mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_db.return_value.__exit__ = MagicMock(return_value=None)
            
            # Mock user and positions
            mock_user = MagicMock()
            mock_user.account_balance = 100000.0
            mock_user.margin_available = 50000.0
            mock_session.query().filter().first.return_value = mock_user
            mock_session.query().filter().all.return_value = []  # No existing positions
            
            result = await risk_manager.check_pre_trade_risk(1, order_request)
            
            assert isinstance(result, dict)
            assert 'allowed' in result
            assert 'reason' in result
    
    @pytest.mark.asyncio
    async def test_var_calculation(self):
        """Test VaR calculation"""
        with patch('rms.manager.db_manager.get_db') as mock_db:
            mock_session = MagicMock()
            mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_db.return_value.__exit__ = MagicMock(return_value=None)
            
            # Mock positions
            mock_position = MagicMock()
            mock_position.quantity = 10
            mock_position.avg_entry_price = 2000.0
            mock_session.query().filter().all.return_value = [mock_position]
            
            result = await risk_manager.calculate_var(1)
            
            assert isinstance(result, dict)
            assert 'var' in result
            assert 'expected_shortfall' in result
            assert result['var'] >= 0


def test_basic_imports():
    """Test that all modules can be imported without errors"""
    import core.models
    import market_data.provider
    import ai_assistant.bot
    import oms.manager
    import rms.manager
    import storage.database
    
    # Basic sanity checks
    assert hasattr(core.models, 'OrderSide')
    assert hasattr(market_data.provider, 'gold_price_provider')
    assert hasattr(ai_assistant.bot, 'trading_bot')
    assert hasattr(oms.manager, 'order_manager')
    assert hasattr(rms.manager, 'risk_manager')


if __name__ == "__main__":
    # Run basic tests without pytest
    print("Running basic functionality tests...")
    
    # Test imports
    test_basic_imports()
    print("✅ All modules imported successfully")
    
    # Test market data
    async def run_basic_tests():
        try:
            price = await gold_price_provider.get_current_price()
            print(f"✅ Market data: ${price['price']}")
            
            analysis = await trading_bot.analyze_trade_opportunity(
                {'price': 2050.0, 'volume': 500, 'change_percent': 0.001}, []
            )
            print(f"✅ AI analysis: {analysis['predicted_direction']}")
            
            print("✅ Basic tests completed successfully!")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    asyncio.run(run_basic_tests())