// Package oms provides Order Management System functionality
package oms

import (
	"fmt"
	"math/rand"
	"time"

	"github.com/google/uuid"
	"github.com/smaruf/python-ai-course/nasdaq-cse-go/internal/core"
	"gorm.io/gorm"
)

// MatchingEngine handles order execution and matching
type MatchingEngine struct {
	orderBook     map[string][]core.Order // Key: contract symbol
	lastTradePrice map[string]float64      // Key: contract symbol
}

// NewMatchingEngine creates a new matching engine
func NewMatchingEngine() *MatchingEngine {
	return &MatchingEngine{
		orderBook:      make(map[string][]core.Order),
		lastTradePrice: make(map[string]float64),
	}
}

// ProcessOrder processes an order through the matching engine
func (me *MatchingEngine) ProcessOrder(order *core.Order, contract *core.Contract, db *gorm.DB) ([]core.Trade, error) {
	var trades []core.Trade

	switch order.OrderType {
	case core.OrderTypeMarket:
		trade, err := me.executeMarketOrder(order, contract, db)
		if err != nil {
			return nil, err
		}
		trades = append(trades, *trade)
	case core.OrderTypeLimit:
		executedTrades, err := me.executeLimitOrder(order, contract, db)
		if err != nil {
			return nil, err
		}
		trades = append(trades, executedTrades...)
	default:
		return nil, fmt.Errorf("unsupported order type: %s", order.OrderType)
	}

	return trades, nil
}

// executeMarketOrder executes a market order at current market price
func (me *MatchingEngine) executeMarketOrder(order *core.Order, contract *core.Contract, db *gorm.DB) (*core.Trade, error) {
	// Get last trade price or use default
	lastPrice, exists := me.lastTradePrice[contract.Symbol]
	if !exists {
		lastPrice = 2050.0 // Default gold price
	}

	// Simulate market execution with small slippage
	slippage := (rand.Float64() - 0.5) * 0.002 // ±0.1% slippage
	executionPrice := lastPrice * (1 + slippage)

	// Create trade
	trade := core.Trade{
		TradeID:    uuid.New().String(),
		ContractID: order.ContractID,
		Quantity:   order.Quantity,
		Price:      executionPrice,
		TradeTime:  time.Now(),
	}

	// Set order IDs based on side
	if order.Side == core.OrderSideBuy {
		trade.BuyOrderID = &order.OrderID
	} else {
		trade.SellOrderID = &order.OrderID
	}

	// Update order status
	order.Status = core.OrderStatusFilled
	order.FilledQuantity = order.Quantity
	avgPrice := executionPrice
	order.AvgFillPrice = &avgPrice

	// Save trade to database
	if err := db.Create(&trade).Error; err != nil {
		return nil, fmt.Errorf("failed to create trade: %w", err)
	}

	// Update last trade price
	me.lastTradePrice[contract.Symbol] = executionPrice

	return &trade, nil
}

// executeLimitOrder executes a limit order if price conditions are met
func (me *MatchingEngine) executeLimitOrder(order *core.Order, contract *core.Contract, db *gorm.DB) ([]core.Trade, error) {
	if order.Price == nil {
		return nil, fmt.Errorf("limit order must have a price")
	}

	// Get current market price
	lastPrice, exists := me.lastTradePrice[contract.Symbol]
	if !exists {
		lastPrice = 2050.0
	}

	canExecute := false
	if order.Side == core.OrderSideBuy && *order.Price >= lastPrice {
		canExecute = true
	} else if order.Side == core.OrderSideSell && *order.Price <= lastPrice {
		canExecute = true
	}

	if canExecute {
		// Execute at limit price
		trade := core.Trade{
			TradeID:    uuid.New().String(),
			ContractID: order.ContractID,
			Quantity:   order.Quantity,
			Price:      *order.Price,
			TradeTime:  time.Now(),
		}

		if order.Side == core.OrderSideBuy {
			trade.BuyOrderID = &order.OrderID
		} else {
			trade.SellOrderID = &order.OrderID
		}

		// Update order status
		order.Status = core.OrderStatusFilled
		order.FilledQuantity = order.Quantity
		order.AvgFillPrice = order.Price

		// Save trade
		if err := db.Create(&trade).Error; err != nil {
			return nil, fmt.Errorf("failed to create trade: %w", err)
		}

		me.lastTradePrice[contract.Symbol] = *order.Price
		return []core.Trade{trade}, nil
	}

	// Order remains pending
	order.Status = core.OrderStatusPending
	return []core.Trade{}, nil
}

// GetMarketDepth returns current market depth
func (me *MatchingEngine) GetMarketDepth(symbol string) map[string]interface{} {
	orders := me.orderBook[symbol]
	
	var bids, asks []core.Order
	for _, order := range orders {
		if order.Status == core.OrderStatusPending {
			if order.Side == core.OrderSideBuy {
				bids = append(bids, order)
			} else {
				asks = append(asks, order)
			}
		}
	}

	// Limit to top 10
	if len(bids) > 10 {
		bids = bids[:10]
	}
	if len(asks) > 10 {
		asks = asks[:10]
	}

	return map[string]interface{}{
		"bids":       bids,
		"asks":       asks,
		"last_price": me.lastTradePrice[symbol],
	}
}

// OrderManager manages order lifecycle and position tracking
type OrderManager struct {
	matchingEngine *MatchingEngine
	db             *gorm.DB
}

// NewOrderManager creates a new order manager
func NewOrderManager(db *gorm.DB) *OrderManager {
	return &OrderManager{
		matchingEngine: NewMatchingEngine(),
		db:             db,
	}
}

// SubmitOrderResult represents the result of submitting an order
type SubmitOrderResult struct {
	Success bool                     `json:"success"`
	OrderID string                   `json:"order_id,omitempty"`
	Status  string                   `json:"status,omitempty"`
	Trades  []map[string]interface{} `json:"trades,omitempty"`
	Error   string                   `json:"error,omitempty"`
}

// SubmitOrder submits a new order
func (om *OrderManager) SubmitOrder(userID uint, orderRequest core.OrderCreateRequest) SubmitOrderResult {
	// Get contract
	var contract core.Contract
	if err := om.db.Where("symbol = ?", orderRequest.ContractSymbol).First(&contract).Error; err != nil {
		return SubmitOrderResult{
			Success: false,
			Error:   "Contract not found",
		}
	}

	// Create order
	order := core.Order{
		OrderID:    uuid.New().String(),
		UserID:     userID,
		ContractID: contract.ID,
		Side:       orderRequest.Side,
		OrderType:  orderRequest.OrderType,
		Quantity:   orderRequest.Quantity,
		Price:      orderRequest.Price,
		StopPrice:  orderRequest.StopPrice,
		Status:     core.OrderStatusPending,
	}

	// Save order to database
	if err := om.db.Create(&order).Error; err != nil {
		return SubmitOrderResult{
			Success: false,
			Error:   fmt.Sprintf("Failed to create order: %v", err),
		}
	}

	// Process order through matching engine
	trades, err := om.matchingEngine.ProcessOrder(&order, &contract, om.db)
	if err != nil {
		return SubmitOrderResult{
			Success: false,
			Error:   fmt.Sprintf("Failed to process order: %v", err),
		}
	}

	// Update order in database
	if err := om.db.Save(&order).Error; err != nil {
		return SubmitOrderResult{
			Success: false,
			Error:   fmt.Sprintf("Failed to update order: %v", err),
		}
	}

	// Update positions if order was executed
	if len(trades) > 0 {
		if err := om.updatePositions(userID, trades); err != nil {
			return SubmitOrderResult{
				Success: false,
				Error:   fmt.Sprintf("Failed to update positions: %v", err),
			}
		}
	}

	// Prepare trade data for response
	var tradeData []map[string]interface{}
	for _, trade := range trades {
		tradeData = append(tradeData, map[string]interface{}{
			"trade_id": trade.TradeID,
			"price":    trade.Price,
			"quantity": trade.Quantity,
		})
	}

	return SubmitOrderResult{
		Success: true,
		OrderID: order.OrderID,
		Status:  string(order.Status),
		Trades:  tradeData,
	}
}

// CancelOrder cancels an existing order
func (om *OrderManager) CancelOrder(orderID string, userID uint) map[string]interface{} {
	var order core.Order
	if err := om.db.Where("order_id = ? AND user_id = ? AND status = ?", 
		orderID, userID, core.OrderStatusPending).First(&order).Error; err != nil {
		return map[string]interface{}{
			"success": false,
			"error":   "Order not found or cannot be cancelled",
		}
	}

	order.Status = core.OrderStatusCancelled
	if err := om.db.Save(&order).Error; err != nil {
		return map[string]interface{}{
			"success": false,
			"error":   fmt.Sprintf("Failed to cancel order: %v", err),
		}
	}

	return map[string]interface{}{
		"success": true,
		"message": "Order cancelled successfully",
	}
}

// GetUserOrders returns user's orders
func (om *OrderManager) GetUserOrders(userID uint, limit int) ([]map[string]interface{}, error) {
	var orders []core.Order
	query := om.db.Where("user_id = ?", userID).Order("created_at desc")
	if limit > 0 {
		query = query.Limit(limit)
	}
	
	if err := query.Find(&orders).Error; err != nil {
		return nil, fmt.Errorf("failed to fetch orders: %w", err)
	}

	var result []map[string]interface{}
	for _, order := range orders {
		orderData := map[string]interface{}{
			"order_id":        order.OrderID,
			"contract_id":     order.ContractID,
			"side":            string(order.Side),
			"order_type":      string(order.OrderType),
			"quantity":        order.Quantity,
			"price":           order.Price,
			"status":          string(order.Status),
			"filled_quantity": order.FilledQuantity,
			"avg_fill_price":  order.AvgFillPrice,
			"created_at":      order.CreatedAt.Format(time.RFC3339),
			"updated_at":      order.UpdatedAt.Format(time.RFC3339),
		}
		result = append(result, orderData)
	}

	return result, nil
}

// GetUserTrades returns user's trade history
func (om *OrderManager) GetUserTrades(userID uint, limit int) ([]map[string]interface{}, error) {
	var trades []core.Trade
	
	// Join with orders to filter by user
	query := om.db.Joins("JOIN orders ON (trades.buy_order_id = orders.order_id OR trades.sell_order_id = orders.order_id)").
		Where("orders.user_id = ?", userID).
		Order("trades.trade_time desc")
	
	if limit > 0 {
		query = query.Limit(limit)
	}
	
	if err := query.Find(&trades).Error; err != nil {
		return nil, fmt.Errorf("failed to fetch trades: %w", err)
	}

	var result []map[string]interface{}
	for _, trade := range trades {
		tradeData := map[string]interface{}{
			"trade_id":    trade.TradeID,
			"contract_id": trade.ContractID,
			"quantity":    trade.Quantity,
			"price":       trade.Price,
			"trade_time":  trade.TradeTime.Format(time.RFC3339),
		}
		result = append(result, tradeData)
	}

	return result, nil
}

// GetUserPositions returns user's current positions
func (om *OrderManager) GetUserPositions(userID uint) ([]map[string]interface{}, error) {
	var positions []core.Position
	if err := om.db.Where("user_id = ?", userID).Find(&positions).Error; err != nil {
		return nil, fmt.Errorf("failed to fetch positions: %w", err)
	}

	var result []map[string]interface{}
	for _, pos := range positions {
		posData := map[string]interface{}{
			"position_id":        pos.ID,
			"contract_id":        pos.ContractID,
			"quantity":           pos.Quantity,
			"avg_entry_price":    pos.AvgEntryPrice,
			"unrealized_pnl":     pos.UnrealizedPnL,
			"realized_pnl":       pos.RealizedPnL,
			"margin_requirement": pos.MarginRequirement,
			"last_updated":       pos.LastUpdated.Format(time.RFC3339),
		}
		result = append(result, posData)
	}

	return result, nil
}

// updatePositions updates user positions based on executed trades
func (om *OrderManager) updatePositions(userID uint, trades []core.Trade) error {
	for _, trade := range trades {
		// Find existing position
		var position core.Position
		err := om.db.Where("user_id = ? AND contract_id = ?", userID, trade.ContractID).First(&position).Error
		
		// Determine if this is a buy or sell
		var order core.Order
		if trade.BuyOrderID != nil {
			if err := om.db.Where("order_id = ?", *trade.BuyOrderID).First(&order).Error; err != nil {
				continue
			}
		} else if trade.SellOrderID != nil {
			if err := om.db.Where("order_id = ?", *trade.SellOrderID).First(&order).Error; err != nil {
				continue
			}
		} else {
			continue
		}

		tradeQuantity := trade.Quantity
		if order.Side == core.OrderSideSell {
			tradeQuantity = -trade.Quantity
		}

		if err == nil {
			// Update existing position
			oldQuantity := position.Quantity
			oldValue := oldQuantity * position.AvgEntryPrice
			newValue := tradeQuantity * trade.Price

			position.Quantity += tradeQuantity

			if position.Quantity != 0 {
				position.AvgEntryPrice = (oldValue + newValue) / position.Quantity
			} else {
				// Position closed
				position.RealizedPnL += oldValue + newValue
				position.AvgEntryPrice = 0
			}

			position.LastUpdated = time.Now()
			if err := om.db.Save(&position).Error; err != nil {
				return fmt.Errorf("failed to update position: %w", err)
			}
		} else {
			// Create new position
			var contract core.Contract
			if err := om.db.First(&contract, trade.ContractID).Error; err != nil {
				continue
			}

			position = core.Position{
				UserID:            userID,
				ContractID:        trade.ContractID,
				Quantity:          tradeQuantity,
				AvgEntryPrice:     trade.Price,
				MarginRequirement: contract.InitialMargin,
				LastUpdated:       time.Now(),
			}

			if err := om.db.Create(&position).Error; err != nil {
				return fmt.Errorf("failed to create position: %w", err)
			}
		}
	}

	return nil
}

// UpdatePositionPnL updates unrealized P&L for all positions based on current market prices
func (om *OrderManager) UpdatePositionPnL(currentPrices map[uint]float64) error {
	var positions []core.Position
	if err := om.db.Find(&positions).Error; err != nil {
		return fmt.Errorf("failed to fetch positions: %w", err)
	}

	for _, position := range positions {
		if currentPrice, exists := currentPrices[position.ContractID]; exists {
			if position.Quantity != 0 {
				position.UnrealizedPnL = (currentPrice - position.AvgEntryPrice) * position.Quantity
				position.LastUpdated = time.Now()
				
				if err := om.db.Save(&position).Error; err != nil {
					return fmt.Errorf("failed to update position P&L: %w", err)
				}
			}
		}
	}

	return nil
}