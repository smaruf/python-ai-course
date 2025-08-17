"""
Risk Management System (RMS) for monitoring positions and margins
"""
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from core.models import User, Position, Contract
from storage.database import db_manager
import asyncio


class RiskManager:
    """
    Comprehensive risk management system for monitoring and controlling trading risks
    """
    
    def __init__(self):
        self.risk_limits = {
            'max_position_size': 1000,  # Max position size per contract
            'max_total_exposure': 500000,  # Max total exposure per user
            'margin_call_threshold': 0.8,  # Margin call at 80% utilization
            'force_liquidation_threshold': 0.95,  # Force liquidation at 95%
            'max_daily_loss': 0.05,  # Max 5% daily loss
            'concentration_limit': 0.3,  # Max 30% in single position
            'volatility_limit': 0.1  # Max 10% daily volatility exposure
        }
        self.risk_alerts = []
    
    async def check_pre_trade_risk(self, user_id: int, order_request: Dict) -> Dict:
        """
        Check risk limits before allowing a trade
        """
        db = next(db_manager.get_db())
        
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {'allowed': False, 'reason': 'User not found'}
            
            # Get user's current positions
            positions = db.query(Position).filter(Position.user_id == user_id).all()
            
            # Calculate current exposure
            total_exposure = sum(abs(pos.quantity * pos.avg_entry_price) for pos in positions)
            
            # Check position size limit
            new_exposure = float(order_request['quantity']) * float(order_request.get('price', 2000))
            if new_exposure > self.risk_limits['max_position_size'] * 2000:  # Assuming $2000 per unit
                return {'allowed': False, 'reason': 'Position size exceeds limit'}
            
            # Check total exposure limit
            if total_exposure + new_exposure > self.risk_limits['max_total_exposure']:
                return {'allowed': False, 'reason': 'Total exposure would exceed limit'}
            
            # Check margin requirements
            margin_check = await self._check_margin_requirements(user, positions, order_request, db)
            if not margin_check['sufficient']:
                return {'allowed': False, 'reason': margin_check['reason']}
            
            # Check concentration limits
            concentration_check = await self._check_concentration_limits(positions, order_request)
            if not concentration_check['allowed']:
                return {'allowed': False, 'reason': concentration_check['reason']}
            
            return {'allowed': True, 'reason': 'Risk checks passed'}
            
        finally:
            db.close()
    
    async def check_post_trade_risk(self, user_id: int) -> Dict:
        """
        Check risk metrics after a trade is executed
        """
        db = next(db_manager.get_db())
        
        try:
            user = db.query(User).filter(User.id == user_id).first()
            positions = db.query(Position).filter(Position.user_id == user_id).all()
            
            risk_metrics = await self._calculate_risk_metrics(user, positions)
            alerts = await self._generate_risk_alerts(risk_metrics)
            
            return {
                'user_id': user_id,
                'risk_metrics': risk_metrics,
                'alerts': alerts,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        finally:
            db.close()
    
    async def monitor_margin_requirements(self, user_id: int, current_prices: Dict[int, float]) -> Dict:
        """
        Monitor margin requirements and generate margin calls if needed
        """
        db = next(db_manager.get_db())
        
        try:
            user = db.query(User).filter(User.id == user_id).first()
            positions = db.query(Position).filter(Position.user_id == user_id).all()
            
            if not user or not positions:
                return {'margin_adequate': True, 'margin_call': False}
            
            # Calculate total margin requirement
            total_margin_required = 0
            total_unrealized_pnl = 0
            
            for position in positions:
                if position.contract_id in current_prices:
                    current_price = current_prices[position.contract_id]
                    
                    # Update unrealized P&L
                    if position.quantity != 0:
                        position.unrealized_pnl = (current_price - position.avg_entry_price) * position.quantity
                        total_unrealized_pnl += position.unrealized_pnl
                    
                    # Calculate margin requirement
                    contract = db.query(Contract).filter(Contract.id == position.contract_id).first()
                    if contract:
                        margin_per_unit = contract.maintenance_margin
                        total_margin_required += abs(position.quantity) * margin_per_unit
            
            # Calculate available margin
            account_equity = user.account_balance + total_unrealized_pnl
            available_margin = account_equity - total_margin_required
            margin_utilization = total_margin_required / account_equity if account_equity > 0 else 1.0
            
            margin_call = margin_utilization > self.risk_limits['margin_call_threshold']
            force_liquidation = margin_utilization > self.risk_limits['force_liquidation_threshold']
            
            # Update user's margin available
            user.margin_available = max(0, available_margin)
            db.commit()
            
            return {
                'margin_adequate': not margin_call,
                'margin_call': margin_call,
                'force_liquidation': force_liquidation,
                'margin_utilization': margin_utilization,
                'total_margin_required': total_margin_required,
                'available_margin': available_margin,
                'account_equity': account_equity
            }
            
        finally:
            db.close()
    
    async def calculate_var(self, user_id: int, confidence_level: float = 0.95, time_horizon: int = 1) -> Dict:
        """
        Calculate Value at Risk (VaR) for user's portfolio
        """
        db = next(db_manager.get_db())
        
        try:
            positions = db.query(Position).filter(Position.user_id == user_id).all()
            
            if not positions:
                return {'var': 0.0, 'expected_shortfall': 0.0}
            
            # Simplified VaR calculation
            total_exposure = sum(abs(pos.quantity * pos.avg_entry_price) for pos in positions)
            
            # Assume 2% daily volatility for gold
            daily_volatility = 0.02
            
            # VaR calculation (parametric method)
            from scipy.stats import norm
            z_score = norm.ppf(1 - confidence_level)
            var = total_exposure * daily_volatility * z_score * (time_horizon ** 0.5)
            
            # Expected Shortfall (Conditional VaR)
            expected_shortfall = total_exposure * daily_volatility * norm.pdf(z_score) / (1 - confidence_level)
            
            return {
                'var': abs(var),
                'expected_shortfall': abs(expected_shortfall),
                'confidence_level': confidence_level,
                'time_horizon_days': time_horizon,
                'total_exposure': total_exposure
            }
            
        except ImportError:
            # Fallback if scipy is not available
            total_exposure = sum(abs(pos.quantity * pos.avg_entry_price) for pos in positions)
            var = total_exposure * 0.02 * 1.65  # Approximate 95% VaR
            return {
                'var': var,
                'expected_shortfall': var * 1.3,
                'confidence_level': confidence_level,
                'time_horizon_days': time_horizon,
                'total_exposure': total_exposure
            }
        finally:
            db.close()
    
    async def generate_risk_report(self, user_id: int, current_prices: Dict[int, float]) -> Dict:
        """
        Generate comprehensive risk report for a user
        """
        margin_status = await self.monitor_margin_requirements(user_id, current_prices)
        var_metrics = await self.calculate_var(user_id)
        post_trade_risk = await self.check_post_trade_risk(user_id)
        
        risk_score = self._calculate_risk_score(margin_status, var_metrics, post_trade_risk)
        
        return {
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat(),
            'risk_score': risk_score,
            'margin_status': margin_status,
            'var_metrics': var_metrics,
            'risk_metrics': post_trade_risk.get('risk_metrics', {}),
            'alerts': post_trade_risk.get('alerts', []),
            'recommendations': self._generate_risk_recommendations(risk_score, margin_status, var_metrics)
        }
    
    async def _check_margin_requirements(self, user: object, positions: List, order_request: Dict, db: Session) -> Dict:
        """
        Check if user has sufficient margin for new order
        """
        # Get contract for margin calculation
        contract = db.query(Contract).filter(Contract.symbol == order_request['contract_symbol']).first()
        if not contract:
            return {'sufficient': False, 'reason': 'Contract not found'}
        
        # Calculate additional margin needed
        additional_margin = float(order_request['quantity']) * contract.initial_margin
        
        if user.margin_available < additional_margin:
            return {'sufficient': False, 'reason': 'Insufficient margin available'}
        
        return {'sufficient': True, 'reason': 'Margin requirements met'}
    
    async def _check_concentration_limits(self, positions: List, order_request: Dict) -> Dict:
        """
        Check position concentration limits
        """
        total_exposure = sum(abs(pos.quantity * pos.avg_entry_price) for pos in positions)
        
        if total_exposure == 0:
            return {'allowed': True, 'reason': 'No existing positions'}
        
        # Calculate exposure for the contract in the order
        contract_symbol = order_request['contract_symbol']
        contract_exposure = sum(
            abs(pos.quantity * pos.avg_entry_price) for pos in positions
            # Note: This is simplified - in reality we'd match by contract_id
        )
        
        new_exposure = float(order_request['quantity']) * float(order_request.get('price', 2000))
        projected_contract_exposure = contract_exposure + new_exposure
        projected_concentration = projected_contract_exposure / (total_exposure + new_exposure)
        
        if projected_concentration > self.risk_limits['concentration_limit']:
            return {
                'allowed': False,
                'reason': f'Position concentration would exceed {self.risk_limits["concentration_limit"]*100}% limit'
            }
        
        return {'allowed': True, 'reason': 'Concentration limits satisfied'}
    
    async def _calculate_risk_metrics(self, user: object, positions: List) -> Dict:
        """
        Calculate comprehensive risk metrics
        """
        if not positions:
            return {
                'total_exposure': 0,
                'leverage_ratio': 0,
                'concentration_ratio': 0,
                'unrealized_pnl': 0,
                'position_count': 0
            }
        
        total_exposure = sum(abs(pos.quantity * pos.avg_entry_price) for pos in positions)
        total_unrealized_pnl = sum(pos.unrealized_pnl for pos in positions)
        leverage_ratio = total_exposure / user.account_balance if user.account_balance > 0 else 0
        
        # Calculate concentration (largest position as % of total)
        position_exposures = [abs(pos.quantity * pos.avg_entry_price) for pos in positions]
        max_position_exposure = max(position_exposures) if position_exposures else 0
        concentration_ratio = max_position_exposure / total_exposure if total_exposure > 0 else 0
        
        return {
            'total_exposure': total_exposure,
            'leverage_ratio': leverage_ratio,
            'concentration_ratio': concentration_ratio,
            'unrealized_pnl': total_unrealized_pnl,
            'position_count': len(positions),
            'largest_position': max_position_exposure
        }
    
    async def _generate_risk_alerts(self, risk_metrics: Dict) -> List[Dict]:
        """
        Generate risk alerts based on metrics
        """
        alerts = []
        
        if risk_metrics['leverage_ratio'] > 5:
            alerts.append({
                'type': 'HIGH_LEVERAGE',
                'severity': 'HIGH',
                'message': f"Leverage ratio {risk_metrics['leverage_ratio']:.1f}x is very high",
                'recommendation': 'Consider reducing position sizes'
            })
        
        if risk_metrics['concentration_ratio'] > self.risk_limits['concentration_limit']:
            alerts.append({
                'type': 'HIGH_CONCENTRATION',
                'severity': 'MEDIUM',
                'message': f"Position concentration {risk_metrics['concentration_ratio']:.1%} exceeds limit",
                'recommendation': 'Diversify positions across multiple contracts'
            })
        
        if risk_metrics['unrealized_pnl'] < -risk_metrics.get('total_exposure', 0) * 0.1:
            alerts.append({
                'type': 'LARGE_UNREALIZED_LOSS',
                'severity': 'HIGH',
                'message': 'Unrealized losses exceed 10% of exposure',
                'recommendation': 'Review positions and consider stop-loss orders'
            })
        
        return alerts
    
    def _calculate_risk_score(self, margin_status: Dict, var_metrics: Dict, post_trade_risk: Dict) -> float:
        """
        Calculate overall risk score (0-100, higher is riskier)
        """
        score = 0
        
        # Margin utilization component (0-40 points)
        margin_util = margin_status.get('margin_utilization', 0)
        score += min(40, margin_util * 50)
        
        # VaR component (0-30 points)
        var_ratio = var_metrics.get('var', 0) / max(var_metrics.get('total_exposure', 1), 1)
        score += min(30, var_ratio * 1000)
        
        # Risk metrics component (0-30 points)
        risk_metrics = post_trade_risk.get('risk_metrics', {})
        leverage = risk_metrics.get('leverage_ratio', 0)
        concentration = risk_metrics.get('concentration_ratio', 0)
        score += min(15, leverage * 3) + min(15, concentration * 50)
        
        return min(100, score)
    
    def _generate_risk_recommendations(self, risk_score: float, margin_status: Dict, var_metrics: Dict) -> List[str]:
        """
        Generate risk management recommendations
        """
        recommendations = []
        
        if risk_score > 70:
            recommendations.append("HIGH RISK: Immediate action required to reduce risk exposure")
        elif risk_score > 50:
            recommendations.append("MEDIUM RISK: Monitor positions closely and consider risk reduction")
        
        if margin_status.get('margin_utilization', 0) > 0.8:
            recommendations.append("Consider adding funds or reducing positions to improve margin situation")
        
        if var_metrics.get('var', 0) > 10000:
            recommendations.append("High VaR detected - consider portfolio hedging strategies")
        
        return recommendations


# Global instance
risk_manager = RiskManager()