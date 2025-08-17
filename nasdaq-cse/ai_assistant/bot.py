"""
AI-powered bot assistant for trading analysis and suggestions
"""
import json
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pandas as pd


class TradingBot:
    """
    AI-powered trading assistant that analyzes trades, risk, and provides suggestions
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.analysis_history = []
        self.risk_thresholds = {
            'high_exposure': 0.7,  # 70% of account
            'high_concentration': 0.5,  # 50% in single position
            'volatility_threshold': 0.05,  # 5% daily volatility
            'margin_warning': 0.8  # 80% margin utilization
        }
        self._initialize_model()
    
    def _initialize_model(self):
        """
        Initialize the ML model with sample training data
        """
        # Generate synthetic training data for demonstration
        np.random.seed(42)
        n_samples = 1000
        
        # Features: price_change, volume, volatility, rsi, moving_avg_ratio
        X = np.random.randn(n_samples, 5)
        
        # Target: future price movement (simplified)
        y = X[:, 0] * 0.3 + X[:, 2] * 0.2 + np.random.randn(n_samples) * 0.1
        
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        self.model.fit(X_scaled, y)
    
    async def analyze_trade_opportunity(self, market_data: Dict, user_positions: List[Dict]) -> Dict:
        """
        Analyze current market conditions and suggest trading opportunities
        """
        current_price = market_data.get('price', 2000)
        volume = market_data.get('volume', 500)
        
        # Calculate technical indicators
        rsi = self._calculate_rsi(market_data)
        volatility = self._calculate_volatility(market_data)
        moving_avg_ratio = self._calculate_moving_average_ratio(market_data)
        
        # Prepare features for ML model
        features = np.array([[
            market_data.get('change_percent', 0),
            volume / 1000,  # Normalize volume
            volatility,
            rsi,
            moving_avg_ratio
        ]])
        
        features_scaled = self.scaler.transform(features)
        price_prediction = self.model.predict(features_scaled)[0]
        
        # Generate trading suggestion
        suggestion = self._generate_trading_suggestion(
            current_price, price_prediction, rsi, volatility, user_positions
        )
        
        analysis = {
            'timestamp': datetime.utcnow().isoformat(),
            'analysis_type': 'trade_suggestion',
            'current_price': current_price,
            'predicted_direction': 'BULLISH' if price_prediction > 0 else 'BEARISH',
            'confidence_score': min(abs(price_prediction) * 100, 95),
            'technical_indicators': {
                'rsi': rsi,
                'volatility': volatility,
                'moving_avg_ratio': moving_avg_ratio
            },
            'suggestion': suggestion,
            'risk_level': self._assess_risk_level(user_positions, market_data)
        }
        
        self.analysis_history.append(analysis)
        return analysis
    
    async def analyze_risk(self, user_positions: List[Dict], account_balance: float) -> Dict:
        """
        Analyze risk exposure and provide warnings/suggestions
        """
        total_exposure = sum(pos.get('quantity', 0) * pos.get('avg_entry_price', 0) for pos in user_positions)
        exposure_ratio = total_exposure / account_balance if account_balance > 0 else 0
        
        # Calculate position concentration
        if user_positions:
            max_position = max(abs(pos.get('quantity', 0) * pos.get('avg_entry_price', 0)) for pos in user_positions)
            concentration_ratio = max_position / total_exposure if total_exposure > 0 else 0
        else:
            concentration_ratio = 0
        
        # Calculate total P&L
        total_unrealized_pnl = sum(pos.get('unrealized_pnl', 0) for pos in user_positions)
        total_realized_pnl = sum(pos.get('realized_pnl', 0) for pos in user_positions)
        
        risk_warnings = []
        recommendations = []
        
        # Check various risk conditions
        if exposure_ratio > self.risk_thresholds['high_exposure']:
            risk_warnings.append(f"High exposure: {exposure_ratio:.1%} of account balance")
            recommendations.append("Consider reducing position sizes or adding hedges")
        
        if concentration_ratio > self.risk_thresholds['high_concentration']:
            risk_warnings.append(f"High concentration: {concentration_ratio:.1%} in single position")
            recommendations.append("Diversify positions across multiple contracts")
        
        if total_unrealized_pnl < -account_balance * 0.1:
            risk_warnings.append("Unrealized losses exceed 10% of account balance")
            recommendations.append("Consider stop-loss orders or position reduction")
        
        risk_level = "LOW"
        if len(risk_warnings) >= 3:
            risk_level = "HIGH"
        elif len(risk_warnings) >= 1:
            risk_level = "MEDIUM"
        
        analysis = {
            'timestamp': datetime.utcnow().isoformat(),
            'analysis_type': 'risk_analysis',
            'risk_level': risk_level,
            'exposure_ratio': exposure_ratio,
            'concentration_ratio': concentration_ratio,
            'total_unrealized_pnl': total_unrealized_pnl,
            'total_realized_pnl': total_realized_pnl,
            'risk_warnings': risk_warnings,
            'recommendations': recommendations,
            'confidence_score': 85.0
        }
        
        self.analysis_history.append(analysis)
        return analysis
    
    async def suggest_hedging_strategy(self, user_positions: List[Dict], market_data: Dict) -> Dict:
        """
        Suggest hedging strategies based on current positions
        """
        if not user_positions:
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'analysis_type': 'hedging_strategy',
                'suggestion': 'No positions to hedge',
                'confidence_score': 0.0
            }
        
        # Calculate net exposure
        net_long_exposure = sum(
            pos.get('quantity', 0) for pos in user_positions if pos.get('quantity', 0) > 0
        )
        net_short_exposure = sum(
            abs(pos.get('quantity', 0)) for pos in user_positions if pos.get('quantity', 0) < 0
        )
        
        net_exposure = net_long_exposure - net_short_exposure
        current_price = market_data.get('price', 2000)
        volatility = self._calculate_volatility(market_data)
        
        hedging_suggestions = []
        
        if abs(net_exposure) > 0:
            hedge_ratio = min(abs(net_exposure) * 0.5, abs(net_exposure))  # 50% hedge
            
            if net_exposure > 0:  # Net long, suggest short hedge
                hedging_suggestions.append({
                    'action': 'SELL',
                    'quantity': hedge_ratio,
                    'reason': 'Hedge against long exposure',
                    'contract': 'GOLD2024DEC'
                })
            else:  # Net short, suggest long hedge
                hedging_suggestions.append({
                    'action': 'BUY',
                    'quantity': hedge_ratio,
                    'reason': 'Hedge against short exposure',
                    'contract': 'GOLD2024DEC'
                })
        
        if volatility > self.risk_thresholds['volatility_threshold']:
            hedging_suggestions.append({
                'action': 'REDUCE_POSITION',
                'quantity': abs(net_exposure) * 0.3,
                'reason': 'High volatility detected, reduce exposure',
                'contract': 'ALL'
            })
        
        analysis = {
            'timestamp': datetime.utcnow().isoformat(),
            'analysis_type': 'hedging_strategy',
            'net_exposure': net_exposure,
            'current_volatility': volatility,
            'hedging_suggestions': hedging_suggestions,
            'confidence_score': 80.0
        }
        
        self.analysis_history.append(analysis)
        return analysis
    
    async def chat_response(self, user_message: str, context: Dict) -> str:
        """
        Generate a chat response based on user message and trading context
        """
        user_message_lower = user_message.lower()
        
        # Simple keyword-based responses (can be enhanced with NLP)
        if any(word in user_message_lower for word in ['price', 'gold', 'current']):
            current_price = context.get('market_data', {}).get('price', 'N/A')
            return f"The current gold price is ${current_price:.2f} per ounce. The market is showing {'bullish' if context.get('market_data', {}).get('change_percent', 0) > 0 else 'bearish'} sentiment today."
        
        elif any(word in user_message_lower for word in ['risk', 'exposure', 'danger']):
            positions = context.get('positions', [])
            if positions:
                risk_analysis = await self.analyze_risk(positions, context.get('account_balance', 100000))
                return f"Your current risk level is {risk_analysis['risk_level']}. Exposure ratio: {risk_analysis['exposure_ratio']:.1%}. {risk_analysis['recommendations'][0] if risk_analysis['recommendations'] else 'Risk levels are acceptable.'}"
            else:
                return "You currently have no open positions, so your risk exposure is minimal."
        
        elif any(word in user_message_lower for word in ['buy', 'sell', 'trade', 'suggest']):
            market_data = context.get('market_data', {})
            positions = context.get('positions', [])
            analysis = await self.analyze_trade_opportunity(market_data, positions)
            return f"Based on current analysis, I suggest a {analysis['predicted_direction']} outlook with {analysis['confidence_score']:.0f}% confidence. {analysis['suggestion']}"
        
        elif any(word in user_message_lower for word in ['hedge', 'protect', 'cover']):
            positions = context.get('positions', [])
            market_data = context.get('market_data', {})
            hedging = await self.suggest_hedging_strategy(positions, market_data)
            if hedging['hedging_suggestions']:
                suggestion = hedging['hedging_suggestions'][0]
                return f"For hedging, consider {suggestion['action']} {suggestion['quantity']:.0f} units. Reason: {suggestion['reason']}"
            else:
                return "No hedging required at this time based on your current positions."
        
        elif any(word in user_message_lower for word in ['help', 'guide', 'how']):
            return "I can help you with: 1) Current gold prices and market analysis, 2) Risk assessment of your positions, 3) Trading suggestions based on technical indicators, 4) Hedging strategies to protect your portfolio. Just ask me about any of these topics!"
        
        else:
            return "I'm here to help with your gold derivatives trading. Ask me about current prices, risk analysis, trading suggestions, or hedging strategies. What would you like to know?"
    
    def _calculate_rsi(self, market_data: Dict, period: int = 14) -> float:
        """
        Calculate RSI indicator (simplified version)
        """
        # Simplified RSI calculation for demonstration
        change_percent = market_data.get('change_percent', 0)
        # Convert to 0-100 scale with some randomness for demonstration
        rsi = 50 + (change_percent * 1000) + random.uniform(-10, 10)
        return max(0, min(100, rsi))
    
    def _calculate_volatility(self, market_data: Dict) -> float:
        """
        Calculate price volatility
        """
        # Simplified volatility calculation
        return abs(market_data.get('change_percent', 0)) + random.uniform(0.01, 0.03)
    
    def _calculate_moving_average_ratio(self, market_data: Dict) -> float:
        """
        Calculate ratio of current price to moving average
        """
        current_price = market_data.get('price', 2000)
        # Simulated moving average
        ma_price = current_price * random.uniform(0.98, 1.02)
        return current_price / ma_price
    
    def _generate_trading_suggestion(self, current_price: float, prediction: float, 
                                   rsi: float, volatility: float, positions: List[Dict]) -> str:
        """
        Generate human-readable trading suggestion
        """
        suggestions = []
        
        if prediction > 0.01:
            suggestions.append("Consider LONG position - bullish signals detected")
        elif prediction < -0.01:
            suggestions.append("Consider SHORT position - bearish signals detected")
        else:
            suggestions.append("HOLD - market showing neutral signals")
        
        if rsi > 70:
            suggestions.append("RSI indicates overbought conditions")
        elif rsi < 30:
            suggestions.append("RSI indicates oversold conditions")
        
        if volatility > 0.05:
            suggestions.append("High volatility - consider smaller position sizes")
        
        if len(positions) > 3:
            suggestions.append("Consider position consolidation")
        
        return "; ".join(suggestions)
    
    def _assess_risk_level(self, positions: List[Dict], market_data: Dict) -> str:
        """
        Assess overall risk level
        """
        risk_factors = 0
        
        if len(positions) > 5:
            risk_factors += 1
        
        if market_data.get('change_percent', 0) > 0.05:
            risk_factors += 1
        
        total_exposure = sum(abs(pos.get('quantity', 0)) for pos in positions)
        if total_exposure > 1000:
            risk_factors += 1
        
        if risk_factors >= 2:
            return "HIGH"
        elif risk_factors == 1:
            return "MEDIUM"
        else:
            return "LOW"


# Global instance
trading_bot = TradingBot()