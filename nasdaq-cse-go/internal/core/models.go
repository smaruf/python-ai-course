// Package core contains the core data models for the trading simulator
package core

import (
	"time"
)

// OrderSide represents the side of an order
type OrderSide string

const (
	OrderSideBuy  OrderSide = "BUY"
	OrderSideSell OrderSide = "SELL"
)

// OrderType represents the type of an order
type OrderType string

const (
	OrderTypeMarket OrderType = "MARKET"
	OrderTypeLimit  OrderType = "LIMIT"
	OrderTypeStop   OrderType = "STOP"
)

// OrderStatus represents the status of an order
type OrderStatus string

const (
	OrderStatusPending   OrderStatus = "PENDING"
	OrderStatusFilled    OrderStatus = "FILLED"
	OrderStatusCancelled OrderStatus = "CANCELLED"
	OrderStatusRejected  OrderStatus = "REJECTED"
)

// ContractType represents the type of trading contract
type ContractType string

const (
	ContractTypeGoldFutures ContractType = "GOLD_FUTURES"
	ContractTypeGoldOption  ContractType = "GOLD_OPTION"
)

// User represents a trading user in the system
type User struct {
	ID              uint      `gorm:"primaryKey" json:"id"`
	Username        string    `gorm:"unique;not null" json:"username"`
	Email           string    `gorm:"unique;not null" json:"email"`
	AccountBalance  float64   `gorm:"default:100000.0" json:"account_balance"`
	MarginAvailable float64   `gorm:"default:100000.0" json:"margin_available"`
	CreatedAt       time.Time `json:"created_at"`
	UpdatedAt       time.Time `json:"updated_at"`
	IsActive        bool      `gorm:"default:true" json:"is_active"`
}

// Contract represents a trading contract
type Contract struct {
	ID                 uint         `gorm:"primaryKey" json:"id"`
	Symbol             string       `gorm:"index;not null" json:"symbol"`
	ContractType       ContractType `json:"contract_type"`
	ExpiryDate         time.Time    `json:"expiry_date"`
	ContractSize       float64      `json:"contract_size"`       // Troy ounces per contract
	TickSize           float64      `gorm:"default:0.01" json:"tick_size"`
	InitialMargin      float64      `json:"initial_margin"`
	MaintenanceMargin  float64      `json:"maintenance_margin"`
	CreatedAt          time.Time    `json:"created_at"`
	UpdatedAt          time.Time    `json:"updated_at"`
	IsActive           bool         `gorm:"default:true" json:"is_active"`
}

// Order represents a trading order
type Order struct {
	ID              uint        `gorm:"primaryKey" json:"id"`
	OrderID         string      `gorm:"unique;not null" json:"order_id"`
	UserID          uint        `gorm:"not null" json:"user_id"`
	ContractID      uint        `gorm:"not null" json:"contract_id"`
	Side            OrderSide   `json:"side"`
	OrderType       OrderType   `json:"order_type"`
	Quantity        float64     `json:"quantity"`
	Price           *float64    `json:"price,omitempty"`
	StopPrice       *float64    `json:"stop_price,omitempty"`
	Status          OrderStatus `json:"status"`
	FilledQuantity  float64     `gorm:"default:0" json:"filled_quantity"`
	AvgFillPrice    *float64    `json:"avg_fill_price,omitempty"`
	CreatedAt       time.Time   `json:"created_at"`
	UpdatedAt       time.Time   `json:"updated_at"`

	// Associations
	User     User     `gorm:"foreignKey:UserID" json:"user,omitempty"`
	Contract Contract `gorm:"foreignKey:ContractID" json:"contract,omitempty"`
}

// Trade represents an executed trade
type Trade struct {
	ID           uint       `gorm:"primaryKey" json:"id"`
	TradeID      string     `gorm:"unique;not null" json:"trade_id"`
	BuyOrderID   *string    `json:"buy_order_id,omitempty"`
	SellOrderID  *string    `json:"sell_order_id,omitempty"`
	ContractID   uint       `gorm:"not null" json:"contract_id"`
	Quantity     float64    `json:"quantity"`
	Price        float64    `json:"price"`
	TradeTime    time.Time  `json:"trade_time"`
	CreatedAt    time.Time  `json:"created_at"`

	// Associations
	Contract Contract `gorm:"foreignKey:ContractID" json:"contract,omitempty"`
}

// Position represents a user's position in a contract
type Position struct {
	ID                 uint      `gorm:"primaryKey" json:"id"`
	UserID             uint      `gorm:"not null" json:"user_id"`
	ContractID         uint      `gorm:"not null" json:"contract_id"`
	Quantity           float64   `json:"quantity"`
	AvgEntryPrice      float64   `json:"avg_entry_price"`
	UnrealizedPnL      float64   `gorm:"default:0" json:"unrealized_pnl"`
	RealizedPnL        float64   `gorm:"default:0" json:"realized_pnl"`
	MarginRequirement  float64   `json:"margin_requirement"`
	LastUpdated        time.Time `json:"last_updated"`
	CreatedAt          time.Time `json:"created_at"`
	UpdatedAt          time.Time `json:"updated_at"`

	// Associations
	User     User     `gorm:"foreignKey:UserID" json:"user,omitempty"`
	Contract Contract `gorm:"foreignKey:ContractID" json:"contract,omitempty"`
}

// MarketData represents market data for a contract
type MarketData struct {
	ID           uint      `gorm:"primaryKey" json:"id"`
	ContractID   uint      `gorm:"not null" json:"contract_id"`
	Price        float64   `json:"price"`
	Bid          float64   `json:"bid"`
	Ask          float64   `json:"ask"`
	Volume       int64     `json:"volume"`
	Change24h    float64   `json:"change_24h"`
	ChangePercent float64  `json:"change_percent"`
	Timestamp    time.Time `json:"timestamp"`
	CreatedAt    time.Time `json:"created_at"`

	// Associations
	Contract Contract `gorm:"foreignKey:ContractID" json:"contract,omitempty"`
}

// AIAnalysis represents AI-generated analysis
type AIAnalysis struct {
	ID              uint      `gorm:"primaryKey" json:"id"`
	UserID          uint      `gorm:"not null" json:"user_id"`
	AnalysisType    string    `json:"analysis_type"`
	PredictedDirection string `json:"predicted_direction"`
	ConfidenceScore float64   `json:"confidence_score"`
	Suggestion      string    `json:"suggestion"`
	RiskLevel       string    `json:"risk_level"`
	Timestamp       time.Time `json:"timestamp"`
	CreatedAt       time.Time `json:"created_at"`

	// Associations
	User User `gorm:"foreignKey:UserID" json:"user,omitempty"`
}

// API Request/Response Models

// UserCreateRequest represents a request to create a new user
type UserCreateRequest struct {
	Username string `json:"username" validate:"required,min=3,max=20"`
	Email    string `json:"email" validate:"required,email"`
}

// OrderCreateRequest represents a request to create a new order
type OrderCreateRequest struct {
	ContractSymbol string     `json:"contract_symbol" validate:"required"`
	Side           OrderSide  `json:"side" validate:"required"`
	OrderType      OrderType  `json:"order_type" validate:"required"`
	Quantity       float64    `json:"quantity" validate:"required,gt=0"`
	Price          *float64   `json:"price,omitempty" validate:"omitempty,gt=0"`
	StopPrice      *float64   `json:"stop_price,omitempty" validate:"omitempty,gt=0"`
}

// ChatMessageRequest represents a chat message to the AI assistant
type ChatMessageRequest struct {
	Message string `json:"message" validate:"required,max=500"`
	UserID  uint   `json:"user_id" validate:"required"`
}

// TradingContextRequest represents trading context for AI analysis
type TradingContextRequest struct {
	UserID uint `json:"user_id" validate:"required"`
}

// MarketDataResponse represents current market data
type MarketDataResponse struct {
	Timestamp     time.Time `json:"timestamp"`
	Price         float64   `json:"price"`
	Bid           float64   `json:"bid"`
	Ask           float64   `json:"ask"`
	Volume        int64     `json:"volume"`
	Change24h     float64   `json:"change_24h"`
	ChangePercent float64   `json:"change_percent"`
}

// ChartDataPoint represents a single point in chart data
type ChartDataPoint struct {
	Timestamp time.Time `json:"timestamp"`
	Price     float64   `json:"price"`
	Volume    int64     `json:"volume"`
}

// ChartDataResponse represents chart data for frontend
type ChartDataResponse struct {
	Data []ChartDataPoint `json:"data"`
	Type string           `json:"type"`
}