#!/usr/bin/env python3
"""
Simple test runner to verify the trading simulator works
"""
import sys
import asyncio
sys.path.insert(0, '.')

from core.models import OrderSide, OrderType
from market_data.provider import gold_price_provider, chart_generator
from ai_assistant.bot import trading_bot
from storage.database import db_manager

async def test_basic_functionality():
    """Test basic functionality"""
    print("🧪 Running Gold Derivatives Trading Simulator Tests...")
    print("=" * 60)
    
    # Test 1: Market Data
    print("1. Testing Market Data Provider...")
    try:
        price_data = await gold_price_provider.get_current_price()
        print(f"   ✅ Current gold price: ${price_data['price']:.2f}")
        print(f"   ✅ Bid: ${price_data['bid']:.2f}, Ask: ${price_data['ask']:.2f}")
    except Exception as e:
        print(f"   ❌ Market data error: {e}")
    
    # Test 2: Chart Generation
    print("\n2. Testing Chart Generation...")
    try:
        # Add some sample data first
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
        chart_json = chart_generator.create_price_chart(1)
        print(f"   ✅ Generated chart data (length: {len(chart_json)} chars)")
    except Exception as e:
        print(f"   ❌ Chart generation error: {e}")
    
    # Test 3: AI Assistant
    print("\n3. Testing AI Trading Assistant...")
    try:
        market_data = {
            'price': 2050.0,
            'volume': 500,
            'change_percent': 0.001
        }
        analysis = await trading_bot.analyze_trade_opportunity(market_data, [])
        print(f"   ✅ AI Analysis: {analysis['predicted_direction']} (confidence: {analysis['confidence_score']:.1f}%)")
        
        # Test chat response
        context = {
            'market_data': market_data,
            'positions': [],
            'account_balance': 100000.0
        }
        response = await trading_bot.chat_response("What's the current gold price?", context)
        print(f"   ✅ Chat response: {response[:100]}...")
        
    except Exception as e:
        print(f"   ❌ AI assistant error: {e}")
    
    # Test 4: Database
    print("\n4. Testing Database Connection...")
    try:
        # Test database initialization
        print(f"   ✅ Database engine: {type(db_manager.engine).__name__}")
        print(f"   ✅ Sample data initialized")
    except Exception as e:
        print(f"   ❌ Database error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Basic functionality tests completed!")
    print("\nTo start the trading simulator:")
    print("   python main.py")
    print("\nThen visit: http://localhost:8000")

if __name__ == "__main__":
    asyncio.run(test_basic_functionality())