#!/usr/bin/env python3
"""
Contextual AI Assistant Example
===============================

An AI assistant that understands application context and provides smart,
context-aware responses. Based on the nasdaq-cse AI assistant implementation.

This example demonstrates:
- Context-aware AI responses
- Smart routing based on query content
- Application state integration
- Session management
"""

import asyncio
import json
import random
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import requests


@dataclass
class MarketData:
    """Market data structure"""
    symbol: str
    price: float
    change_percent: float
    volume: int
    volatility: float
    timestamp: datetime


@dataclass
class Portfolio:
    """User portfolio structure"""
    user_id: int
    total_value: float
    positions: List[Dict[str, Any]]
    risk_level: str
    last_updated: datetime


class TradingAssistant:
    """Context-aware AI assistant for trading applications"""
    
    def __init__(self, model_type: str = "ollama"):
        self.model_type = model_type
        self.context_memory = {}
        self.conversation_history = []
        
    async def chat_response(self, user_message: str, app_context: Dict[str, Any]) -> str:
        """
        Generate context-aware AI response
        
        Args:
            user_message: User's question or request
            app_context: Current application state and context
            
        Returns:
            AI response tailored to the context
        """
        
        # Extract context components
        user_id = app_context.get('user_id')
        market_data = app_context.get('market_data')
        portfolio = app_context.get('portfolio')
        session_data = app_context.get('session', {})
        
        # Update context memory
        self._update_context_memory(user_id, app_context)
        
        # Smart routing based on message content
        response = await self._route_query(user_message, market_data, portfolio, session_data)
        
        # Store conversation
        self.conversation_history.append({
            'timestamp': datetime.now(),
            'user_id': user_id,
            'message': user_message,
            'response': response,
            'context': app_context
        })
        
        return response
    
    def _update_context_memory(self, user_id: int, context: Dict[str, Any]):
        """Update context memory for user"""
        if user_id not in self.context_memory:
            self.context_memory[user_id] = {
                'preferences': {},
                'interaction_count': 0,
                'last_active': datetime.now(),
                'topics_discussed': set()
            }
        
        self.context_memory[user_id]['interaction_count'] += 1
        self.context_memory[user_id]['last_active'] = datetime.now()
    
    async def _route_query(self, message: str, market_data: Optional[MarketData], 
                          portfolio: Optional[Portfolio], session_data: Dict) -> str:
        """Route query to appropriate handler based on content"""
        
        message_lower = message.lower()
        
        # Price and market data queries
        if any(word in message_lower for word in ['price', 'current', 'quote', 'market']):
            return self._handle_price_query(message, market_data)
        
        # Portfolio and position queries
        elif any(word in message_lower for word in ['portfolio', 'position', 'holdings', 'balance']):
            return self._handle_portfolio_query(message, portfolio)
        
        # Trading action queries
        elif any(word in message_lower for word in ['buy', 'sell', 'trade', 'order']):
            return await self._handle_trading_query(message, market_data, portfolio)
        
        # Risk and analysis queries
        elif any(word in message_lower for word in ['risk', 'analysis', 'recommend', 'suggest']):
            return await self._handle_analysis_query(message, market_data, portfolio)
        
        # General queries - use LLM with context
        else:
            return await self._handle_general_query(message, market_data, portfolio, session_data)
    
    def _handle_price_query(self, message: str, market_data: Optional[MarketData]) -> str:
        """Handle price and market data queries"""
        
        if not market_data:
            return "❌ Market data is not available at the moment. Please try again later."
        
        # Format price information
        price = market_data.price
        change = market_data.change_percent
        volume = market_data.volume
        volatility = market_data.volatility
        
        # Determine market sentiment
        if change > 2:
            sentiment = "strongly bullish 🚀"
        elif change > 0:
            sentiment = "bullish 📈"
        elif change > -2:
            sentiment = "bearish 📉"
        else:
            sentiment = "strongly bearish 🔻"
        
        # Volatility assessment
        if volatility > 0.4:
            vol_desc = "HIGH volatility ⚠️"
        elif volatility > 0.2:
            vol_desc = "moderate volatility"
        else:
            vol_desc = "low volatility ✅"
        
        response = f"""📊 **{market_data.symbol} Market Data**
        
**Current Price:** ${price:,.2f}
**Change:** {change:+.2f}% ({sentiment})
**Volume:** {volume:,} shares
**Volatility:** {volatility:.1%} ({vol_desc})
**Last Updated:** {market_data.timestamp.strftime('%H:%M:%S')}

{self._get_price_insight(change, volatility)}"""
        
        return response
    
    def _handle_portfolio_query(self, message: str, portfolio: Optional[Portfolio]) -> str:
        """Handle portfolio and position queries"""
        
        if not portfolio:
            return "❌ Portfolio data is not available. Please make sure you're logged in."
        
        total_value = portfolio.total_value
        positions = portfolio.positions
        risk_level = portfolio.risk_level
        
        # Calculate portfolio metrics
        position_count = len(positions)
        largest_position = max(positions, key=lambda x: x.get('value', 0)) if positions else None
        
        response = f"""💼 **Portfolio Summary**
        
**Total Value:** ${total_value:,.2f}
**Active Positions:** {position_count}
**Risk Level:** {risk_level.upper()}
**Last Updated:** {portfolio.last_updated.strftime('%Y-%m-%d %H:%M')}"""
        
        if largest_position:
            response += f"\n**Largest Position:** {largest_position.get('symbol', 'N/A')} (${largest_position.get('value', 0):,.2f})"
        
        if position_count > 0:
            response += f"\n\n**Positions:**"
            for pos in positions[:5]:  # Show top 5 positions
                symbol = pos.get('symbol', 'Unknown')
                quantity = pos.get('quantity', 0)
                value = pos.get('value', 0)
                pnl = pos.get('unrealized_pnl', 0)
                pnl_indicator = "📈" if pnl > 0 else "📉" if pnl < 0 else "➖"
                response += f"\n• {symbol}: {quantity} shares, ${value:,.2f} {pnl_indicator}"
        
        response += f"\n\n{self._get_portfolio_insight(portfolio)}"
        
        return response
    
    async def _handle_trading_query(self, message: str, market_data: Optional[MarketData], 
                                   portfolio: Optional[Portfolio]) -> str:
        """Handle trading action queries"""
        
        if not market_data:
            return "❌ Cannot provide trading advice without current market data."
        
        message_lower = message.lower()
        action = "buy" if "buy" in message_lower else "sell" if "sell" in message_lower else "trade"
        
        # Risk assessment
        risk_factors = []
        if market_data.volatility > 0.3:
            risk_factors.append("High volatility")
        if abs(market_data.change_percent) > 5:
            risk_factors.append("Large price movement")
        
        risk_level = "HIGH" if risk_factors else "MODERATE" if market_data.volatility > 0.2 else "LOW"
        
        # Build trading advice
        response = f"""🔄 **Trading Analysis for {action.upper()}**
        
**Current Conditions:**
• Price: ${market_data.price:,.2f}
• Change: {market_data.change_percent:+.2f}%
• Risk Level: {risk_level} ⚠️"""
        
        if risk_factors:
            response += f"\n• Risk Factors: {', '.join(risk_factors)}"
        
        # Action-specific advice
        if action == "buy":
            if market_data.change_percent < -2:
                advice = "Potential buying opportunity during the dip, but monitor closely."
            elif market_data.change_percent > 5:
                advice = "Consider waiting for a pullback before buying."
            else:
                advice = "Current conditions are reasonable for buying."
        else:  # sell
            if market_data.change_percent > 3:
                advice = "Good opportunity to take profits."
            elif market_data.change_percent < -5:
                advice = "Consider if this is a stop-loss situation or temporary dip."
            else:
                advice = "Evaluate your profit targets and risk tolerance."
        
        response += f"\n\n**Recommendation:** {advice}"
        response += f"\n\n⚠️ **Risk Management:**"
        response += f"\n• Set stop-loss orders"
        response += f"\n• Consider position sizing (risk only 1-2% of portfolio)"
        response += f"\n• Monitor market conditions closely"
        
        return response
    
    async def _handle_analysis_query(self, message: str, market_data: Optional[MarketData], 
                                    portfolio: Optional[Portfolio]) -> str:
        """Handle analysis and recommendation queries"""
        
        if not market_data:
            return "❌ Analysis requires current market data."
        
        # Technical analysis simulation
        analysis = self._generate_technical_analysis(market_data)
        
        response = f"""📈 **Market Analysis**
        
**Technical Indicators:**
• RSI: {analysis['rsi']:.1f} ({analysis['rsi_signal']})
• Moving Average: {analysis['ma_signal']}
• Volume: {analysis['volume_signal']}
• Trend: {analysis['trend']}

**Market Sentiment:** {analysis['sentiment']}

**Recommendations:**"""
        
        for rec in analysis['recommendations']:
            response += f"\n• {rec}"
        
        if portfolio:
            response += f"\n\n**Portfolio Specific:**"
            response += f"\n• Your risk level ({portfolio.risk_level}) suggests {self._get_risk_specific_advice(portfolio.risk_level, analysis)}"
        
        return response
    
    async def _handle_general_query(self, message: str, market_data: Optional[MarketData], 
                                   portfolio: Optional[Portfolio], session_data: Dict) -> str:
        """Handle general queries using LLM with context"""
        
        # Build contextual prompt
        context_parts = ["You are an expert trading assistant."]
        
        if market_data:
            context_parts.append(f"Current market: {market_data.symbol} at ${market_data.price} ({market_data.change_percent:+.2f}%)")
        
        if portfolio:
            context_parts.append(f"User portfolio: ${portfolio.total_value:,.2f} total value, {len(portfolio.positions)} positions")
        
        context = " ".join(context_parts)
        
        # Use LLM for general response
        return await self._call_llm_with_context(message, context)
    
    async def _call_llm_with_context(self, message: str, context: str) -> str:
        """Call LLM with trading context"""
        
        prompt = f"""{context}

User question: {message}

Provide a helpful response relevant to trading and finance. Be specific and actionable."""
        
        try:
            if self.model_type == "ollama":
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "llama3.1:8b",
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    return response.json().get("response", "I couldn't generate a response.")
                else:
                    return "I'm having trouble accessing my knowledge base right now."
            else:
                return "I need more context to answer that question properly."
                
        except Exception as e:
            return f"I encountered an error: {str(e)}"
    
    def _generate_technical_analysis(self, market_data: MarketData) -> Dict[str, Any]:
        """Generate simulated technical analysis"""
        
        # Simulate technical indicators (in real implementation, calculate from price history)
        rsi = random.uniform(20, 80)
        
        # RSI signals
        if rsi > 70:
            rsi_signal = "Overbought"
        elif rsi < 30:
            rsi_signal = "Oversold"
        else:
            rsi_signal = "Neutral"
        
        # Moving average signal based on current trend
        if market_data.change_percent > 1:
            ma_signal = "Above MA - Bullish"
        elif market_data.change_percent < -1:
            ma_signal = "Below MA - Bearish"
        else:
            ma_signal = "Near MA - Sideways"
        
        # Volume signal
        volume_signal = "High volume" if market_data.volume > 100000 else "Low volume"
        
        # Overall trend
        if market_data.change_percent > 2:
            trend = "Strong Uptrend"
        elif market_data.change_percent > 0:
            trend = "Weak Uptrend"
        elif market_data.change_percent > -2:
            trend = "Weak Downtrend"
        else:
            trend = "Strong Downtrend"
        
        # Sentiment
        if rsi > 60 and market_data.change_percent > 0:
            sentiment = "Bullish"
        elif rsi < 40 and market_data.change_percent < 0:
            sentiment = "Bearish"
        else:
            sentiment = "Neutral"
        
        # Recommendations
        recommendations = []
        if rsi > 70:
            recommendations.append("Consider taking profits - RSI indicates overbought conditions")
        elif rsi < 30:
            recommendations.append("Potential buying opportunity - RSI indicates oversold conditions")
        
        if market_data.volatility > 0.3:
            recommendations.append("Use smaller position sizes due to high volatility")
        
        if not recommendations:
            recommendations.append("Monitor current trends and wait for clearer signals")
        
        return {
            'rsi': rsi,
            'rsi_signal': rsi_signal,
            'ma_signal': ma_signal,
            'volume_signal': volume_signal,
            'trend': trend,
            'sentiment': sentiment,
            'recommendations': recommendations
        }
    
    def _get_price_insight(self, change_percent: float, volatility: float) -> str:
        """Get insight based on price movement"""
        if abs(change_percent) > 5:
            return "⚠️ Significant price movement detected. Consider reviewing your positions."
        elif volatility > 0.4:
            return "⚠️ High volatility environment. Use appropriate risk management."
        else:
            return "✅ Normal market conditions. Good time for regular trading strategies."
    
    def _get_portfolio_insight(self, portfolio: Portfolio) -> str:
        """Get portfolio-specific insight"""
        if portfolio.risk_level == "high":
            return "🚀 Your high-risk profile allows for aggressive strategies, but always manage risk."
        elif portfolio.risk_level == "low":
            return "🛡️ Your conservative profile suggests focusing on stable, low-volatility investments."
        else:
            return "⚖️ Your moderate risk profile allows for balanced growth and income strategies."
    
    def _get_risk_specific_advice(self, risk_level: str, analysis: Dict) -> str:
        """Get advice specific to user's risk level"""
        if risk_level == "high":
            return "aggressive positioning based on technical signals."
        elif risk_level == "low":
            return "conservative positioning and waiting for strong confirmation signals."
        else:
            return "balanced positioning with proper risk management."


# Demo application
async def demo_contextual_ai():
    """Demonstrate contextual AI assistant"""
    
    print("🤖 Contextual AI Trading Assistant Demo")
    print("=" * 50)
    
    # Initialize assistant
    assistant = TradingAssistant()
    
    # Sample market data
    market_data = MarketData(
        symbol="GOLD",
        price=2050.75,
        change_percent=1.2,
        volume=125000,
        volatility=0.25,
        timestamp=datetime.now()
    )
    
    # Sample portfolio
    portfolio = Portfolio(
        user_id=123,
        total_value=50000.0,
        positions=[
            {"symbol": "GOLD", "quantity": 10, "value": 20507.5, "unrealized_pnl": 500},
            {"symbol": "SILVER", "quantity": 100, "value": 2500.0, "unrealized_pnl": -50}
        ],
        risk_level="moderate",
        last_updated=datetime.now()
    )
    
    # Build context
    context = {
        'user_id': 123,
        'market_data': market_data,
        'portfolio': portfolio,
        'session': {'login_time': datetime.now() - timedelta(hours=1)}
    }
    
    # Demo queries
    queries = [
        "What's the current gold price?",
        "How is my portfolio performing?",
        "Should I buy more gold right now?",
        "What's your risk analysis?",
        "Explain technical analysis to me"
    ]
    
    print("Running sample queries:\n")
    
    for i, query in enumerate(queries, 1):
        print(f"📝 Query {i}: {query}")
        print("-" * 60)
        
        response = await assistant.chat_response(query, context)
        print(response)
        print("\n" + "=" * 80 + "\n")
        
        # Small delay for demo effect
        await asyncio.sleep(1)
    
    print("✅ Demo completed!")
    print(f"Conversation history: {len(assistant.conversation_history)} exchanges")


if __name__ == "__main__":
    asyncio.run(demo_contextual_ai())