// Package tests provides unit tests for the Order Management System
package tests

import (
	"testing"

	"github.com/smaruf/python-ai-course/nasdaq-cse-go/internal/core"
	"github.com/smaruf/python-ai-course/nasdaq-cse-go/internal/oms"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

func setupTestDB(t *testing.T) *gorm.DB {
	db, err := gorm.Open(sqlite.Open(":memory:"), &gorm.Config{})
	if err != nil {
		t.Fatalf("Failed to open test database: %v", err)
	}

	// Auto-migrate
	err = db.AutoMigrate(
		&core.User{},
		&core.Contract{},
		&core.Order{},
		&core.Trade{},
		&core.Position{},
	)
	if err != nil {
		t.Fatalf("Failed to migrate test database: %v", err)
	}

	// Create test contract
	contract := core.Contract{
		Symbol:            "GOLD2024DEC",
		ContractType:      core.ContractTypeGoldFutures,
		ContractSize:      100.0,
		TickSize:          0.01,
		InitialMargin:     5000.0,
		MaintenanceMargin: 3500.0,
		IsActive:          true,
	}
	db.Create(&contract)

	// Create test user
	user := core.User{
		Username:        "test_user",
		Email:           "test@example.com",
		AccountBalance:  100000.0,
		MarginAvailable: 100000.0,
		IsActive:        true,
	}
	db.Create(&user)

	return db
}

func TestOrderManager_SubmitOrder(t *testing.T) {
	db := setupTestDB(t)
	orderManager := oms.NewOrderManager(db)

	tests := []struct {
		name    string
		userID  uint
		order   core.OrderCreateRequest
		wantErr bool
	}{
		{
			name:   "Valid market buy order",
			userID: 1,
			order: core.OrderCreateRequest{
				ContractSymbol: "GOLD2024DEC",
				Side:           core.OrderSideBuy,
				OrderType:      core.OrderTypeMarket,
				Quantity:       5.0,
			},
			wantErr: false,
		},
		{
			name:   "Valid limit sell order",
			userID: 1,
			order: core.OrderCreateRequest{
				ContractSymbol: "GOLD2024DEC",
				Side:           core.OrderSideSell,
				OrderType:      core.OrderTypeLimit,
				Quantity:       3.0,
				Price:          func() *float64 { p := 2100.0; return &p }(),
			},
			wantErr: false,
		},
		{
			name:   "Invalid contract symbol",
			userID: 1,
			order: core.OrderCreateRequest{
				ContractSymbol: "INVALID",
				Side:           core.OrderSideBuy,
				OrderType:      core.OrderTypeMarket,
				Quantity:       1.0,
			},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := orderManager.SubmitOrder(tt.userID, tt.order)
			
			if tt.wantErr && result.Success {
				t.Errorf("Expected error but got success")
			}
			if !tt.wantErr && !result.Success {
				t.Errorf("Expected success but got error: %s", result.Error)
			}
			if !tt.wantErr && result.Success && result.OrderID == "" {
				t.Errorf("Expected order ID but got empty string")
			}
		})
	}
}

func TestOrderManager_GetUserOrders(t *testing.T) {
	db := setupTestDB(t)
	orderManager := oms.NewOrderManager(db)

	// Submit a test order first
	orderRequest := core.OrderCreateRequest{
		ContractSymbol: "GOLD2024DEC",
		Side:           core.OrderSideBuy,
		OrderType:      core.OrderTypeMarket,
		Quantity:       5.0,
	}
	orderManager.SubmitOrder(1, orderRequest)

	// Get user orders
	orders, err := orderManager.GetUserOrders(1, 10)
	if err != nil {
		t.Errorf("GetUserOrders failed: %v", err)
	}

	if len(orders) == 0 {
		t.Errorf("Expected at least one order but got none")
	}

	// Check order structure
	order := orders[0]
	if _, ok := order["order_id"]; !ok {
		t.Errorf("Order missing order_id field")
	}
	if _, ok := order["side"]; !ok {
		t.Errorf("Order missing side field")
	}
	if _, ok := order["quantity"]; !ok {
		t.Errorf("Order missing quantity field")
	}
}

func TestOrderManager_GetUserPositions(t *testing.T) {
	db := setupTestDB(t)
	orderManager := oms.NewOrderManager(db)

	// Submit and execute an order to create a position
	orderRequest := core.OrderCreateRequest{
		ContractSymbol: "GOLD2024DEC",
		Side:           core.OrderSideBuy,
		OrderType:      core.OrderTypeMarket,
		Quantity:       5.0,
	}
	result := orderManager.SubmitOrder(1, orderRequest)
	if !result.Success {
		t.Fatalf("Failed to submit order: %s", result.Error)
	}

	// Get user positions
	positions, err := orderManager.GetUserPositions(1)
	if err != nil {
		t.Errorf("GetUserPositions failed: %v", err)
	}

	if len(positions) == 0 {
		t.Errorf("Expected at least one position but got none")
	}

	// Check position structure
	position := positions[0]
	if _, ok := position["contract_id"]; !ok {
		t.Errorf("Position missing contract_id field")
	}
	if _, ok := position["quantity"]; !ok {
		t.Errorf("Position missing quantity field")
	}
	if _, ok := position["avg_entry_price"]; !ok {
		t.Errorf("Position missing avg_entry_price field")
	}
}

func TestMatchingEngine_ProcessOrder(t *testing.T) {
	db := setupTestDB(t)
	matchingEngine := oms.NewMatchingEngine()

	// Get test contract
	var contract core.Contract
	db.First(&contract)

	// Create test order
	order := core.Order{
		OrderID:    "test-order-1",
		UserID:     1,
		ContractID: contract.ID,
		Side:       core.OrderSideBuy,
		OrderType:  core.OrderTypeMarket,
		Quantity:   5.0,
		Status:     core.OrderStatusPending,
	}

	trades, err := matchingEngine.ProcessOrder(&order, &contract, db)
	if err != nil {
		t.Errorf("ProcessOrder failed: %v", err)
	}

	if len(trades) == 0 {
		t.Errorf("Expected at least one trade but got none")
	}

	if order.Status != core.OrderStatusFilled {
		t.Errorf("Expected order status to be FILLED but got %s", order.Status)
	}

	// Check trade details
	trade := trades[0]
	if trade.Quantity != order.Quantity {
		t.Errorf("Expected trade quantity %f but got %f", order.Quantity, trade.Quantity)
	}
	if trade.Price <= 0 {
		t.Errorf("Expected positive trade price but got %f", trade.Price)
	}
}