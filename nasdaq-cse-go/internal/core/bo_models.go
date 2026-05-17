// Package core contains BO (Beneficial Owner) data models for the multi-BO dealer workstation
package core

import "time"

// DealerRole represents the role of a user in the dealer system
type DealerRole string

const (
	DealerRoleDealer    DealerRole = "DEALER"
	DealerRoleRMS       DealerRole = "RMS_OFFICER"
	DealerRoleAdmin     DealerRole = "ADMIN"
	DealerRoleViewer    DealerRole = "VIEWER"
)

// ClientGroupType represents the category of a client group
type ClientGroupType string

const (
	ClientGroupHNI          ClientGroupType = "HNI"
	ClientGroupMargin       ClientGroupType = "MARGIN"
	ClientGroupInstitutional ClientGroupType = "INSTITUTIONAL"
	ClientGroupProp         ClientGroupType = "PROP"
	ClientGroupFamilyOffice ClientGroupType = "FAMILY_OFFICE"
)

// BOAccount represents a Beneficial Owner account managed by a dealer
type BOAccount struct {
	ID            uint            `gorm:"primaryKey" json:"id"`
	BOID          string          `gorm:"uniqueIndex;not null" json:"bo_id"` // e.g., BO1001
	ClientName    string          `gorm:"not null" json:"client_name"`
	DealerID      uint            `gorm:"not null" json:"dealer_id"` // Managing dealer (User.ID)
	GroupType     ClientGroupType `json:"group_type"`
	BuyingPower   float64         `gorm:"default:0" json:"buying_power"`
	Exposure      float64         `gorm:"default:0" json:"exposure"`
	MarginStatus  string          `gorm:"default:'OK'" json:"margin_status"`
	IsActive      bool            `gorm:"default:true" json:"is_active"`
	CreatedAt     time.Time       `json:"created_at"`
	UpdatedAt     time.Time       `json:"updated_at"`
}

// ClientGroup represents a named group of BO accounts (e.g., GROUP-HNI)
type ClientGroup struct {
	ID          uint            `gorm:"primaryKey" json:"id"`
	GroupName   string          `gorm:"uniqueIndex;not null" json:"group_name"` // e.g., GROUP-HNI
	GroupType   ClientGroupType `json:"group_type"`
	DealerID    uint            `gorm:"not null" json:"dealer_id"`
	Description string          `json:"description"`
	IsActive    bool            `gorm:"default:true" json:"is_active"`
	CreatedAt   time.Time       `json:"created_at"`
	UpdatedAt   time.Time       `json:"updated_at"`
	Members     []ClientGroupMember `gorm:"foreignKey:GroupID" json:"members,omitempty"`
}

// ClientGroupMember represents the membership of a BO account in a client group
type ClientGroupMember struct {
	ID          uint      `gorm:"primaryKey" json:"id"`
	GroupID     uint      `gorm:"not null" json:"group_id"`
	BOAccountID uint      `gorm:"not null" json:"bo_account_id"`
	Weight      float64   `gorm:"default:1.0" json:"weight"` // For proportional allocation
	CreatedAt   time.Time `json:"created_at"`
}

// Watchlist represents a BO-specific stock watchlist
type Watchlist struct {
	ID          uint            `gorm:"primaryKey" json:"id"`
	BOAccountID uint            `gorm:"not null" json:"bo_account_id"`
	Name        string          `gorm:"not null" json:"name"`
	CreatedAt   time.Time       `json:"created_at"`
	UpdatedAt   time.Time       `json:"updated_at"`
	Items       []WatchlistItem `gorm:"foreignKey:WatchlistID" json:"items,omitempty"`
}

// WatchlistItem represents a single symbol entry in a watchlist
type WatchlistItem struct {
	ID          uint      `gorm:"primaryKey" json:"id"`
	WatchlistID uint      `gorm:"not null" json:"watchlist_id"`
	Symbol      string    `gorm:"not null" json:"symbol"`
	AddedAt     time.Time `json:"added_at"`
}

// AuditLog represents an immutable audit trail entry for dealer actions
type AuditLog struct {
	ID          uint      `gorm:"primaryKey" json:"id"`
	DealerID    uint      `gorm:"not null" json:"dealer_id"`
	BOAccountID *uint     `json:"bo_account_id,omitempty"`
	Action      string    `gorm:"not null" json:"action"`
	Details     string    `json:"details"`
	IPAddress   string    `json:"ip_address"`
	Timestamp   time.Time `json:"timestamp"`
	CreatedAt   time.Time `json:"created_at"`
}

// DealerPermission represents a dealer's role and access restrictions
type DealerPermission struct {
	ID           uint             `gorm:"primaryKey" json:"id"`
	DealerID     uint             `gorm:"not null" json:"dealer_id"`
	Role         DealerRole       `gorm:"not null" json:"role"`
	GroupType    *ClientGroupType `json:"group_type,omitempty"` // If set, restricts trading to this group
	CreatedAt    time.Time        `json:"created_at"`
	UpdatedAt    time.Time        `json:"updated_at"`
}

// BOOrder represents an order placed on behalf of a BO account by a dealer
type BOOrder struct {
	ID           uint        `gorm:"primaryKey" json:"id"`
	OrderID      string      `gorm:"uniqueIndex;not null" json:"order_id"`
	BOAccountID  uint        `gorm:"not null" json:"bo_account_id"`
	DealerID     uint        `gorm:"not null" json:"dealer_id"`
	Symbol       string      `gorm:"not null" json:"symbol"`
	Side         OrderSide   `json:"side"`
	OrderType    OrderType   `json:"order_type"`
	Quantity     float64     `json:"quantity"`
	Price        *float64    `json:"price,omitempty"`
	Status       OrderStatus `json:"status"`
	FilledQty    float64     `gorm:"default:0" json:"filled_qty"`
	AvgFillPrice *float64    `json:"avg_fill_price,omitempty"`
	GroupOrderID *string     `json:"group_order_id,omitempty"` // For basket/group orders
	CreatedAt    time.Time   `json:"created_at"`
	UpdatedAt    time.Time   `json:"updated_at"`
}

// BOPosition represents a BO account's holding in a stock
type BOPosition struct {
	ID            uint      `gorm:"primaryKey" json:"id"`
	BOAccountID   uint      `gorm:"not null" json:"bo_account_id"`
	Symbol        string    `gorm:"not null" json:"symbol"`
	Quantity      float64   `json:"quantity"`
	AvgPrice      float64   `json:"avg_price"`
	LTP           float64   `json:"ltp"` // Last Traded Price
	UnrealizedPnL float64   `gorm:"default:0" json:"unrealized_pnl"`
	CreatedAt     time.Time `json:"created_at"`
	UpdatedAt     time.Time `json:"updated_at"`
}

// DealerContext holds the in-memory session state for a dealer
type DealerContext struct {
	DealerID    uint
	ActiveBOID  string // Active BO account ID string e.g., "BO1001"
	ActiveBOAcc *BOAccount
	LastCommand string
	LastOrderID string
}

// --- Request / Response models ---

// TerminalCommandRequest represents a Bloomberg-style terminal command
type TerminalCommandRequest struct {
	Command  string `json:"command" validate:"required"`
	DealerID uint   `json:"dealer_id" validate:"required"`
}

// TerminalCommandResponse represents the result of executing a terminal command
type TerminalCommandResponse struct {
	Success bool        `json:"success"`
	Output  string      `json:"output"`
	Data    interface{} `json:"data,omitempty"`
	Error   string      `json:"error,omitempty"`
}

// BODashboardResponse represents a live snapshot of a BO account dashboard
type BODashboardResponse struct {
	BOID          string         `json:"bo_id"`
	ClientName    string         `json:"client_name"`
	BuyingPower   float64        `json:"buying_power"`
	Exposure      float64        `json:"exposure"`
	MarginStatus  string         `json:"margin_status"`
	Holdings      int            `json:"holdings"`
	UnrealizedPnL float64        `json:"unrealized_pnl"`
	PendingOrders int            `json:"pending_orders"`
	Positions     []BOPosition   `json:"positions,omitempty"`
}

// BOSearchResult represents a single result from a BO search query
type BOSearchResult struct {
	BOID          string  `json:"bo_id"`
	ClientName    string  `json:"client_name"`
	BuyingPower   float64 `json:"buying_power"`
	PositionCount int     `json:"position_count"`
	PendingOrders int     `json:"pending_orders"`
}

// GroupOrderRequest represents an order submitted for all BOs in a group
type GroupOrderRequest struct {
	GroupName string    `json:"group_name" validate:"required"`
	Symbol    string    `json:"symbol" validate:"required"`
	Side      OrderSide `json:"side" validate:"required"`
	OrderType OrderType `json:"order_type" validate:"required"`
	Quantity  float64   `json:"quantity" validate:"required,gt=0"`
	Price     *float64  `json:"price,omitempty"`
	DealerID  uint      `json:"dealer_id" validate:"required"`
}

// BasketOrderRequest represents a weighted basket order distributed across BO accounts
type BasketOrderRequest struct {
	Symbol   string    `json:"symbol" validate:"required"`
	Side     OrderSide `json:"side" validate:"required"`
	TotalQty float64   `json:"total_qty" validate:"required,gt=0"`
	BOIDs    []string  `json:"bo_ids"` // If empty, use all managed BOs
	DealerID uint      `json:"dealer_id" validate:"required"`
	Weighted bool      `json:"weighted"` // Weight allocation by buying power
}

// AllocOrderRequest represents a proportional value-based allocation order
type AllocOrderRequest struct {
	Symbol     string  `json:"symbol" validate:"required"`
	TotalValue float64 `json:"total_value" validate:"required,gt=0"`
	DealerID   uint    `json:"dealer_id" validate:"required"`
}

// CloneOrderRequest represents a request to clone the last order from one BO to another
type CloneOrderRequest struct {
	SourceBOID string `json:"source_bo_id" validate:"required"`
	TargetBOID string `json:"target_bo_id" validate:"required"`
	DealerID   uint   `json:"dealer_id" validate:"required"`
}

// SwitchBORequest represents a dealer context switch request
type SwitchBORequest struct {
	BOID     string `json:"bo_id" validate:"required"`
	DealerID uint   `json:"dealer_id" validate:"required"`
}

// BOOrderCreateRequest represents a direct BO order submission
type BOOrderCreateRequest struct {
	BOID      string    `json:"bo_id" validate:"required"`
	Symbol    string    `json:"symbol" validate:"required"`
	Side      OrderSide `json:"side" validate:"required"`
	OrderType OrderType `json:"order_type" validate:"required"`
	Quantity  float64   `json:"quantity" validate:"required,gt=0"`
	Price     *float64  `json:"price,omitempty"`
	DealerID  uint      `json:"dealer_id" validate:"required"`
}
