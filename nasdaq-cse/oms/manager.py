"""
Order Management System (OMS) for handling order lifecycle
"""
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from core.models import Order, Trade, Position, Contract, OrderSide, OrderType, OrderStatus
from storage.database import db_manager
import asyncio
import random


class MatchingEngine:
    """
    Simple matching engine for order execution
    """
    
    def __init__(self):
        self.order_book = {
            'bids': [],  # Buy orders sorted by price (highest first)
            'asks': []   # Sell orders sorted by price (lowest first)
        }
        self.last_trade_price = 2050.0
    
    async def process_order(self, order: Order, db: Session) -> List[Trade]:
        """
        Process an order through the matching engine
        """
        trades = []
        
        if order.order_type == OrderType.MARKET:
            trades = await self._execute_market_order(order, db)
        elif order.order_type == OrderType.LIMIT:
            trades = await self._execute_limit_order(order, db)
        
        return trades
    
    async def _execute_market_order(self, order: Order, db: Session) -> List[Trade]:
        """
        Execute market order at current market price
        """
        # Simulate market execution with small slippage
        execution_price = self.last_trade_price * (1 + random.uniform(-0.001, 0.001))
        
        trade = Trade(
            trade_id=str(uuid.uuid4()),
            buy_order_id=order.order_id if order.side == OrderSide.BUY else None,
            sell_order_id=order.order_id if order.side == OrderSide.SELL else None,
            contract_id=order.contract_id,
            quantity=order.quantity,
            price=execution_price,
            trade_time=datetime.utcnow()
        )
        
        db.add(trade)
        
        # Update order status
        order.status = OrderStatus.FILLED
        order.filled_quantity = order.quantity
        order.avg_fill_price = execution_price
        order.updated_at = datetime.utcnow()
        
        self.last_trade_price = execution_price
        
        return [trade]
    
    async def _execute_limit_order(self, order: Order, db: Session) -> List[Trade]:
        """
        Execute limit order if price conditions are met
        """
        # Simplified limit order execution
        # In real system, this would check order book for matching orders
        
        current_market_price = self.last_trade_price
        can_execute = False
        
        if order.side == OrderSide.BUY and order.price >= current_market_price:
            can_execute = True
        elif order.side == OrderSide.SELL and order.price <= current_market_price:
            can_execute = True
        
        if can_execute:
            return await self._execute_market_order(order, db)
        else:
            # Order remains pending
            order.status = OrderStatus.PENDING
            return []
    
    def get_market_depth(self) -> Dict:
        """
        Get current market depth (order book)
        """
        return {
            'bids': self.order_book['bids'][:10],  # Top 10 bids
            'asks': self.order_book['asks'][:10],  # Top 10 asks
            'last_price': self.last_trade_price
        }


class OrderManager:
    """
    Manages order lifecycle and position tracking
    """
    
    def __init__(self):
        self.matching_engine = MatchingEngine()
    
    async def submit_order(self, user_id: int, order_request: Dict) -> Dict:
        """
        Submit a new order
        """
        db = next(db_manager.get_db())
        
        try:
            # Get contract
            contract = db.query(Contract).filter(
                Contract.symbol == order_request['contract_symbol']
            ).first()
            
            if not contract:
                return {'success': False, 'error': 'Contract not found'}
            
            # Create order
            order = Order(
                order_id=str(uuid.uuid4()),
                user_id=user_id,
                contract_id=contract.id,
                side=OrderSide(order_request['side']),
                order_type=OrderType(order_request['order_type']),
                quantity=float(order_request['quantity']),
                price=float(order_request.get('price', 0)) if order_request.get('price') else None,
                stop_price=float(order_request.get('stop_price', 0)) if order_request.get('stop_price') else None,
                status=OrderStatus.PENDING
            )
            
            db.add(order)
            db.commit()
            
            # Process order through matching engine
            trades = await self.matching_engine.process_order(order, db)
            
            # Update positions if order was executed
            if trades:
                await self._update_positions(user_id, trades, db)
            
            db.commit()
            
            return {
                'success': True,
                'order_id': order.order_id,
                'status': order.status.value,
                'trades': [{'trade_id': trade.trade_id, 'price': trade.price, 'quantity': trade.quantity} for trade in trades]
            }
            
        except Exception as e:
            db.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            db.close()
    
    async def cancel_order(self, order_id: str, user_id: int) -> Dict:
        """
        Cancel an existing order
        """
        db = next(db_manager.get_db())
        
        try:
            order = db.query(Order).filter(
                Order.order_id == order_id,
                Order.user_id == user_id,
                Order.status == OrderStatus.PENDING
            ).first()
            
            if not order:
                return {'success': False, 'error': 'Order not found or cannot be cancelled'}
            
            order.status = OrderStatus.CANCELLED
            order.updated_at = datetime.utcnow()
            
            db.commit()
            
            return {'success': True, 'message': 'Order cancelled successfully'}
            
        except Exception as e:
            db.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            db.close()
    
    async def get_user_orders(self, user_id: int, limit: int = 100) -> List[Dict]:
        """
        Get user's orders
        """
        db = next(db_manager.get_db())
        
        try:
            orders = db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).limit(limit).all()
            
            return [
                {
                    'order_id': order.order_id,
                    'contract_id': order.contract_id,
                    'side': order.side.value,
                    'order_type': order.order_type.value,
                    'quantity': order.quantity,
                    'price': order.price,
                    'status': order.status.value,
                    'filled_quantity': order.filled_quantity,
                    'avg_fill_price': order.avg_fill_price,
                    'created_at': order.created_at.isoformat(),
                    'updated_at': order.updated_at.isoformat()
                }
                for order in orders
            ]
            
        finally:
            db.close()
    
    async def get_user_trades(self, user_id: int, limit: int = 100) -> List[Dict]:
        """
        Get user's trade history
        """
        db = next(db_manager.get_db())
        
        try:
            # Get trades through orders
            trades = db.query(Trade).join(Order, 
                (Trade.buy_order_id == Order.order_id) | (Trade.sell_order_id == Order.order_id)
            ).filter(Order.user_id == user_id).order_by(Trade.trade_time.desc()).limit(limit).all()
            
            return [
                {
                    'trade_id': trade.trade_id,
                    'contract_id': trade.contract_id,
                    'quantity': trade.quantity,
                    'price': trade.price,
                    'trade_time': trade.trade_time.isoformat()
                }
                for trade in trades
            ]
            
        finally:
            db.close()
    
    async def get_user_positions(self, user_id: int) -> List[Dict]:
        """
        Get user's current positions
        """
        db = next(db_manager.get_db())
        
        try:
            positions = db.query(Position).filter(Position.user_id == user_id).all()
            
            return [
                {
                    'position_id': pos.id,
                    'contract_id': pos.contract_id,
                    'quantity': pos.quantity,
                    'avg_entry_price': pos.avg_entry_price,
                    'unrealized_pnl': pos.unrealized_pnl,
                    'realized_pnl': pos.realized_pnl,
                    'margin_requirement': pos.margin_requirement,
                    'last_updated': pos.last_updated.isoformat()
                }
                for pos in positions
            ]
            
        finally:
            db.close()
    
    async def _update_positions(self, user_id: int, trades: List[Trade], db: Session):
        """
        Update user positions based on executed trades
        """
        for trade in trades:
            # Find existing position
            position = db.query(Position).filter(
                Position.user_id == user_id,
                Position.contract_id == trade.contract_id
            ).first()
            
            # Determine if this is a buy or sell
            order = db.query(Order).filter(
                (Order.order_id == trade.buy_order_id) | (Order.order_id == trade.sell_order_id)
            ).first()
            
            if not order:
                continue
            
            trade_quantity = trade.quantity if order.side == OrderSide.BUY else -trade.quantity
            
            if position:
                # Update existing position
                old_quantity = position.quantity
                old_value = old_quantity * position.avg_entry_price
                new_value = trade_quantity * trade.price
                
                position.quantity += trade_quantity
                
                if position.quantity != 0:
                    position.avg_entry_price = (old_value + new_value) / position.quantity
                else:
                    # Position closed
                    position.realized_pnl += old_value + new_value
                    position.avg_entry_price = 0
                
                position.last_updated = datetime.utcnow()
                
            else:
                # Create new position
                contract = db.query(Contract).filter(Contract.id == trade.contract_id).first()
                margin_req = contract.initial_margin if contract else 1000.0
                
                position = Position(
                    user_id=user_id,
                    contract_id=trade.contract_id,
                    quantity=trade_quantity,
                    avg_entry_price=trade.price,
                    margin_requirement=margin_req,
                    last_updated=datetime.utcnow()
                )
                db.add(position)
    
    async def update_position_pnl(self, current_prices: Dict[int, float]):
        """
        Update unrealized P&L for all positions based on current market prices
        """
        db = next(db_manager.get_db())
        
        try:
            positions = db.query(Position).all()
            
            for position in positions:
                if position.contract_id in current_prices:
                    current_price = current_prices[position.contract_id]
                    if position.quantity != 0:
                        position.unrealized_pnl = (current_price - position.avg_entry_price) * position.quantity
                        position.last_updated = datetime.utcnow()
            
            db.commit()
            
        finally:
            db.close()


# Global instance
order_manager = OrderManager()