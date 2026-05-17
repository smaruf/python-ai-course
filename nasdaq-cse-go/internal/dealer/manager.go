// Package dealer provides the multi-BO dealer workstation manager
package dealer

import (
	"fmt"
	"math"
	"strings"
	"sync"
	"time"

	"github.com/google/uuid"
	"github.com/smaruf/python-ai-course/nasdaq-cse-go/internal/core"
	"gorm.io/gorm"
)

// StockQuote holds simulated real-time quote data for CSE stocks
type StockQuote struct {
	Symbol  string
	LTP     float64
	Bid     float64
	Ask     float64
	Change  float64
}

// defaultQuotes provides simulated prices for common CSE/DSE stocks
var defaultQuotes = map[string]StockQuote{
	"GP":    {Symbol: "GP", LTP: 350.0, Bid: 349.5, Ask: 350.5, Change: 1.5},
	"BATBC": {Symbol: "BATBC", LTP: 25.4, Bid: 25.3, Ask: 25.5, Change: -0.1},
	"SQPH":  {Symbol: "SQPH", LTP: 220.0, Bid: 219.5, Ask: 220.5, Change: 2.0},
	"BRAC":  {Symbol: "BRAC", LTP: 45.0, Bid: 44.8, Ask: 45.2, Change: 0.5},
	"ROBI":  {Symbol: "ROBI", LTP: 18.5, Bid: 18.4, Ask: 18.6, Change: -0.2},
	"LHBL":  {Symbol: "LHBL", LTP: 60.0, Bid: 59.5, Ask: 60.5, Change: 1.0},
	"OLYMPIC": {Symbol: "OLYMPIC", LTP: 150.0, Bid: 149.5, Ask: 150.5, Change: 0.8},
	"BXPHARMA": {Symbol: "BXPHARMA", LTP: 80.0, Bid: 79.5, Ask: 80.5, Change: -0.5},
}

// Manager is the multi-BO dealer workstation manager
type Manager struct {
	db           *gorm.DB
	contexts     map[uint]*core.DealerContext // keyed by DealerID
	contextMu    sync.RWMutex
	stockQuotes  map[string]StockQuote
	quotesMu     sync.RWMutex
}

// NewManager creates a new dealer workstation manager
func NewManager(db *gorm.DB) *Manager {
	quotes := make(map[string]StockQuote, len(defaultQuotes))
	for k, v := range defaultQuotes {
		quotes[k] = v
	}
	return &Manager{
		db:          db,
		contexts:    make(map[uint]*core.DealerContext),
		stockQuotes: quotes,
	}
}

// --- Dealer Context ---

// GetContext returns or initialises the dealer context for a given dealerID
func (m *Manager) GetContext(dealerID uint) *core.DealerContext {
	m.contextMu.Lock()
	defer m.contextMu.Unlock()
	if ctx, ok := m.contexts[dealerID]; ok {
		return ctx
	}
	ctx := &core.DealerContext{DealerID: dealerID}
	m.contexts[dealerID] = ctx
	return ctx
}

// SwitchBO switches the active BO account for a dealer
func (m *Manager) SwitchBO(dealerID uint, boID string) (string, error) {
	acc, err := m.findBOAccount(boID)
	if err != nil {
		return "", fmt.Errorf("BO account %s not found", boID)
	}
	if acc.DealerID != dealerID {
		return "", fmt.Errorf("dealer does not manage BO account %s", boID)
	}
	m.contextMu.Lock()
	ctx := m.getOrCreateContext(dealerID)
	ctx.ActiveBOID = boID
	ctx.ActiveBOAcc = acc
	m.contextMu.Unlock()

	m.writeAudit(dealerID, &acc.ID, "SWITCH_BO", fmt.Sprintf("Switched active BO to %s (%s)", boID, acc.ClientName), "")
	return fmt.Sprintf("Current BO: %s (%s)", boID, acc.ClientName), nil
}

// --- BO Account Queries ---

// GetBODashboard returns a live snapshot dashboard for a BO account
func (m *Manager) GetBODashboard(boID string) (*core.BODashboardResponse, error) {
	acc, err := m.findBOAccount(boID)
	if err != nil {
		return nil, err
	}

	var positions []core.BOPosition
	m.db.Where("bo_account_id = ?", acc.ID).Find(&positions)

	// Update LTP and recalculate unrealized P&L
	m.quotesMu.RLock()
	for i := range positions {
		if q, ok := m.stockQuotes[positions[i].Symbol]; ok {
			positions[i].LTP = q.LTP
			positions[i].UnrealizedPnL = (q.LTP - positions[i].AvgPrice) * positions[i].Quantity
		}
	}
	m.quotesMu.RUnlock()

	totalPnL := 0.0
	totalExposure := 0.0
	for _, p := range positions {
		totalPnL += p.UnrealizedPnL
		totalExposure += p.Quantity * p.AvgPrice
	}

	var pendingCount int64
	m.db.Model(&core.BOOrder{}).
		Where("bo_account_id = ? AND status = ?", acc.ID, core.OrderStatusPending).
		Count(&pendingCount)

	return &core.BODashboardResponse{
		BOID:          acc.BOID,
		ClientName:    acc.ClientName,
		BuyingPower:   acc.BuyingPower,
		Exposure:      totalExposure,
		MarginStatus:  acc.MarginStatus,
		Holdings:      len(positions),
		UnrealizedPnL: totalPnL,
		PendingOrders: int(pendingCount),
		Positions:     positions,
	}, nil
}

// SearchBO searches BO accounts by BO-ID substring or client name
func (m *Manager) SearchBO(dealerID uint, query string) ([]core.BOSearchResult, error) {
	query = strings.TrimSpace(strings.ToLower(query))

	var accounts []core.BOAccount
	m.db.Where("dealer_id = ? AND is_active = ?", dealerID, true).Find(&accounts)

	var results []core.BOSearchResult
	for _, acc := range accounts {
		if strings.Contains(strings.ToLower(acc.BOID), query) ||
			strings.Contains(strings.ToLower(acc.ClientName), query) {

			var posCount int64
			m.db.Model(&core.BOPosition{}).Where("bo_account_id = ?", acc.ID).Count(&posCount)

			var pendingCount int64
			m.db.Model(&core.BOOrder{}).
				Where("bo_account_id = ? AND status = ?", acc.ID, core.OrderStatusPending).
				Count(&pendingCount)

			results = append(results, core.BOSearchResult{
				BOID:          acc.BOID,
				ClientName:    acc.ClientName,
				BuyingPower:   acc.BuyingPower,
				PositionCount: int(posCount),
				PendingOrders: int(pendingCount),
			})
		}
	}
	return results, nil
}

// ListBOs returns all BO accounts managed by a dealer
func (m *Manager) ListBOs(dealerID uint) ([]core.BOAccount, error) {
	var accounts []core.BOAccount
	if err := m.db.Where("dealer_id = ? AND is_active = ?", dealerID, true).Find(&accounts).Error; err != nil {
		return nil, err
	}
	return accounts, nil
}

// --- Order Submission ---

// SubmitBOOrder submits an order for a specific BO account
func (m *Manager) SubmitBOOrder(req core.BOOrderCreateRequest) (*core.BOOrder, error) {
	acc, err := m.findBOAccount(req.BOID)
	if err != nil {
		return nil, fmt.Errorf("BO account %s not found", req.BOID)
	}

	// RMS pre-trade check
	if err := m.checkBORisk(acc, req.Symbol, req.Side, req.Quantity, req.Price); err != nil {
		return nil, fmt.Errorf("❌ %s %s", req.BOID, err.Error())
	}

	price := req.Price
	if price == nil && req.OrderType == core.OrderTypeLimit {
		return nil, fmt.Errorf("limit order requires a price")
	}

	order := &core.BOOrder{
		OrderID:     uuid.New().String(),
		BOAccountID: acc.ID,
		DealerID:    req.DealerID,
		Symbol:      strings.ToUpper(req.Symbol),
		Side:        req.Side,
		OrderType:   req.OrderType,
		Quantity:    req.Quantity,
		Price:       price,
		Status:      core.OrderStatusPending,
	}

	if err := m.db.Create(order).Error; err != nil {
		return nil, fmt.Errorf("failed to save order: %w", err)
	}

	// Simulate immediate execution
	m.executeOrder(order, acc)

	m.writeAudit(req.DealerID, &acc.ID, "SUBMIT_ORDER",
		fmt.Sprintf("%s %s %s %.0f @ %v for %s", req.Side, req.Symbol, req.OrderType, req.Quantity, req.Price, req.BOID), "")

	ctx := m.GetContext(req.DealerID)
	ctx.LastOrderID = order.OrderID

	return order, nil
}

// SubmitGroupOrder submits the same order for all BO accounts in a named group
func (m *Manager) SubmitGroupOrder(req core.GroupOrderRequest) ([]core.BOOrder, []error) {
	var group core.ClientGroup
	if err := m.db.Preload("Members").
		Where("group_name = ? AND dealer_id = ?", req.GroupName, req.DealerID).
		First(&group).Error; err != nil {
		return nil, []error{fmt.Errorf("group %s not found", req.GroupName)}
	}

	var orders []core.BOOrder
	var errs []error

	for _, member := range group.Members {
		var acc core.BOAccount
		if err := m.db.First(&acc, member.BOAccountID).Error; err != nil {
			errs = append(errs, fmt.Errorf("BO account %d not found", member.BOAccountID))
			continue
		}

		boReq := core.BOOrderCreateRequest{
			BOID:      acc.BOID,
			Symbol:    req.Symbol,
			Side:      req.Side,
			OrderType: req.OrderType,
			Quantity:  req.Quantity,
			Price:     req.Price,
			DealerID:  req.DealerID,
		}
		order, err := m.SubmitBOOrder(boReq)
		if err != nil {
			errs = append(errs, fmt.Errorf("%s: %w", acc.BOID, err))
			continue
		}
		orders = append(orders, *order)
	}

	m.writeAudit(req.DealerID, nil, "GROUP_ORDER",
		fmt.Sprintf("Group %s: %s %s x%.0f", req.GroupName, req.Side, req.Symbol, req.Quantity), "")

	return orders, errs
}

// SubmitBasketOrder distributes a total quantity across BO accounts, optionally weighted by buying power
func (m *Manager) SubmitBasketOrder(req core.BasketOrderRequest) ([]core.BOOrder, []error) {
	var accounts []core.BOAccount
	if len(req.BOIDs) > 0 {
		for _, boID := range req.BOIDs {
			acc, err := m.findBOAccount(boID)
			if err != nil {
				continue
			}
			accounts = append(accounts, *acc)
		}
	} else {
		m.db.Where("dealer_id = ? AND is_active = ?", req.DealerID, true).Find(&accounts)
	}

	if len(accounts) == 0 {
		return nil, []error{fmt.Errorf("no eligible BO accounts for basket order")}
	}

	// Calculate allocations
	allocations := m.calculateAllocations(accounts, req.TotalQty, req.Weighted)

	var orders []core.BOOrder
	var errs []error

	for _, acc := range accounts {
		qty := allocations[acc.ID]
		if qty <= 0 {
			continue
		}
		boReq := core.BOOrderCreateRequest{
			BOID:      acc.BOID,
			Symbol:    req.Symbol,
			Side:      req.Side,
			OrderType: core.OrderTypeMarket,
			Quantity:  qty,
			DealerID:  req.DealerID,
		}
		order, err := m.SubmitBOOrder(boReq)
		if err != nil {
			errs = append(errs, fmt.Errorf("%s: %w", acc.BOID, err))
			continue
		}
		orders = append(orders, *order)
	}

	m.writeAudit(req.DealerID, nil, "BASKET_ORDER",
		fmt.Sprintf("Basket %s %s x%.0f weighted=%v", req.Side, req.Symbol, req.TotalQty, req.Weighted), "")

	return orders, errs
}

// SubmitAllocOrder distributes a total monetary value proportionally across all managed BOs
func (m *Manager) SubmitAllocOrder(req core.AllocOrderRequest) ([]core.BOOrder, []error) {
	var accounts []core.BOAccount
	m.db.Where("dealer_id = ? AND is_active = ?", req.DealerID, true).Find(&accounts)

	// Get current LTP
	m.quotesMu.RLock()
	quote, ok := m.stockQuotes[req.Symbol]
	m.quotesMu.RUnlock()

	ltp := 1.0
	if ok && quote.LTP > 0 {
		ltp = quote.LTP
	}

	totalBP := 0.0
	for _, acc := range accounts {
		totalBP += acc.BuyingPower
	}
	if totalBP == 0 {
		totalBP = 1
	}

	var orders []core.BOOrder
	var errs []error

	for _, acc := range accounts {
		share := (acc.BuyingPower / totalBP) * req.TotalValue
		qty := math.Floor(share / ltp)
		if qty <= 0 {
			continue
		}
		boReq := core.BOOrderCreateRequest{
			BOID:      acc.BOID,
			Symbol:    req.Symbol,
			Side:      core.OrderSideBuy,
			OrderType: core.OrderTypeMarket,
			Quantity:  qty,
			DealerID:  req.DealerID,
		}
		order, err := m.SubmitBOOrder(boReq)
		if err != nil {
			errs = append(errs, fmt.Errorf("%s: %w", acc.BOID, err))
			continue
		}
		orders = append(orders, *order)
	}

	m.writeAudit(req.DealerID, nil, "ALLOC_ORDER",
		fmt.Sprintf("Alloc %s value=%.0f proportional", req.Symbol, req.TotalValue), "")

	return orders, errs
}

// CloneOrder clones the last order of sourceBOID to targetBOID
func (m *Manager) CloneOrder(req core.CloneOrderRequest) (*core.BOOrder, error) {
	srcAcc, err := m.findBOAccount(req.SourceBOID)
	if err != nil {
		return nil, fmt.Errorf("source BO %s not found", req.SourceBOID)
	}

	var lastOrder core.BOOrder
	if err := m.db.Where("bo_account_id = ?", srcAcc.ID).
		Order("created_at desc").First(&lastOrder).Error; err != nil {
		return nil, fmt.Errorf("no orders found for %s", req.SourceBOID)
	}

	boReq := core.BOOrderCreateRequest{
		BOID:      req.TargetBOID,
		Symbol:    lastOrder.Symbol,
		Side:      lastOrder.Side,
		OrderType: lastOrder.OrderType,
		Quantity:  lastOrder.Quantity,
		Price:     lastOrder.Price,
		DealerID:  req.DealerID,
	}

	order, err := m.SubmitBOOrder(boReq)
	if err != nil {
		return nil, err
	}

	m.writeAudit(req.DealerID, nil, "CLONE_ORDER",
		fmt.Sprintf("Cloned order from %s to %s: %s %s x%.0f", req.SourceBOID, req.TargetBOID, lastOrder.Side, lastOrder.Symbol, lastOrder.Quantity), "")

	return order, nil
}

// RepeatLastOrder repeats the last order placed by the dealer for the given BO account
func (m *Manager) RepeatLastOrder(dealerID uint, boID string) (*core.BOOrder, error) {
	acc, err := m.findBOAccount(boID)
	if err != nil {
		return nil, fmt.Errorf("BO account %s not found", boID)
	}

	var lastOrder core.BOOrder
	if err := m.db.Where("bo_account_id = ? AND dealer_id = ?", acc.ID, dealerID).
		Order("created_at desc").First(&lastOrder).Error; err != nil {
		return nil, fmt.Errorf("no previous orders found for %s", boID)
	}

	boReq := core.BOOrderCreateRequest{
		BOID:      boID,
		Symbol:    lastOrder.Symbol,
		Side:      lastOrder.Side,
		OrderType: lastOrder.OrderType,
		Quantity:  lastOrder.Quantity,
		Price:     lastOrder.Price,
		DealerID:  dealerID,
	}

	order, err := m.SubmitBOOrder(boReq)
	if err != nil {
		return nil, err
	}

	m.writeAudit(dealerID, &acc.ID, "REPEAT_ORDER",
		fmt.Sprintf("Repeated last order for %s: %s %s x%.0f", boID, lastOrder.Side, lastOrder.Symbol, lastOrder.Quantity), "")

	return order, nil
}

// ReversePosition submits an opposing market order to close the position for a given symbol
func (m *Manager) ReversePosition(dealerID uint, symbol, boID string) (*core.BOOrder, error) {
	acc, err := m.findBOAccount(boID)
	if err != nil {
		return nil, fmt.Errorf("BO account %s not found", boID)
	}

	var pos core.BOPosition
	if err := m.db.Where("bo_account_id = ? AND symbol = ?", acc.ID, strings.ToUpper(symbol)).
		First(&pos).Error; err != nil {
		return nil, fmt.Errorf("no position found for %s in %s", symbol, boID)
	}

	side := core.OrderSideSell
	if pos.Quantity < 0 {
		side = core.OrderSideBuy
	}
	qty := math.Abs(pos.Quantity)

	boReq := core.BOOrderCreateRequest{
		BOID:      boID,
		Symbol:    symbol,
		Side:      side,
		OrderType: core.OrderTypeMarket,
		Quantity:  qty,
		DealerID:  dealerID,
	}

	order, err := m.SubmitBOOrder(boReq)
	if err != nil {
		return nil, err
	}

	m.writeAudit(dealerID, &acc.ID, "REVERSE_POSITION",
		fmt.Sprintf("Reversed %s position for %s: %s x%.0f", symbol, boID, side, qty), "")

	return order, nil
}

// --- Positions ---

// GetBOPositions returns the live positions for a BO account
func (m *Manager) GetBOPositions(boID string) ([]core.BOPosition, error) {
	acc, err := m.findBOAccount(boID)
	if err != nil {
		return nil, err
	}
	var positions []core.BOPosition
	m.db.Where("bo_account_id = ?", acc.ID).Find(&positions)

	m.quotesMu.RLock()
	for i := range positions {
		if q, ok := m.stockQuotes[positions[i].Symbol]; ok {
			positions[i].LTP = q.LTP
			positions[i].UnrealizedPnL = (q.LTP - positions[i].AvgPrice) * positions[i].Quantity
		}
	}
	m.quotesMu.RUnlock()

	return positions, nil
}

// --- Orders ---

// GetBOOrders returns orders for a BO account
func (m *Manager) GetBOOrders(boID string, limit int) ([]core.BOOrder, error) {
	acc, err := m.findBOAccount(boID)
	if err != nil {
		return nil, err
	}
	var orders []core.BOOrder
	q := m.db.Where("bo_account_id = ?", acc.ID).Order("created_at desc")
	if limit > 0 {
		q = q.Limit(limit)
	}
	q.Find(&orders)
	return orders, nil
}

// --- Watchlist ---

// GetWatchlist returns the watchlist items for a BO account
func (m *Manager) GetWatchlist(boID string) ([]core.WatchlistItem, error) {
	acc, err := m.findBOAccount(boID)
	if err != nil {
		return nil, err
	}
	var wl core.Watchlist
	if err := m.db.Where("bo_account_id = ?", acc.ID).Preload("Items").First(&wl).Error; err != nil {
		return []core.WatchlistItem{}, nil
	}
	return wl.Items, nil
}

// AddToWatchlist adds a symbol to a BO account's watchlist
func (m *Manager) AddToWatchlist(boID, symbol string) error {
	acc, err := m.findBOAccount(boID)
	if err != nil {
		return err
	}
	var wl core.Watchlist
	if err := m.db.Where("bo_account_id = ?", acc.ID).First(&wl).Error; err != nil {
		wl = core.Watchlist{BOAccountID: acc.ID, Name: "Default"}
		m.db.Create(&wl)
	}
	item := core.WatchlistItem{WatchlistID: wl.ID, Symbol: strings.ToUpper(symbol), AddedAt: time.Now()}
	return m.db.Create(&item).Error
}

// --- Risk Dashboard ---

// GetBORiskDashboard returns a risk summary for all BOs managed by a dealer
func (m *Manager) GetBORiskDashboard(dealerID uint) map[string]interface{} {
	var accounts []core.BOAccount
	m.db.Where("dealer_id = ? AND is_active = ?", dealerID, true).Find(&accounts)

	type boRisk struct {
		BOID       string  `json:"bo_id"`
		ClientName string  `json:"client_name"`
		Exposure   float64 `json:"exposure"`
		Leverage   float64 `json:"leverage"`
		PnL        float64 `json:"unrealized_pnl"`
		Alert      string  `json:"alert,omitempty"`
	}

	var risks []boRisk
	totalExposure := 0.0

	m.quotesMu.RLock()
	defer m.quotesMu.RUnlock()

	for _, acc := range accounts {
		var positions []core.BOPosition
		m.db.Where("bo_account_id = ?", acc.ID).Find(&positions)

		exposure := 0.0
		pnl := 0.0
		for _, p := range positions {
			exposure += p.Quantity * p.AvgPrice
			if q, ok := m.stockQuotes[p.Symbol]; ok {
				pnl += (q.LTP - p.AvgPrice) * p.Quantity
			}
		}

		leverage := 0.0
		if acc.BuyingPower > 0 {
			leverage = exposure / acc.BuyingPower
		}

		alert := ""
		if leverage > 3 {
			alert = fmt.Sprintf("%s exceeded exposure", acc.BOID)
		}
		if acc.MarginStatus == "CALL" {
			alert = fmt.Sprintf("%s margin call risk", acc.BOID)
		}

		totalExposure += exposure
		risks = append(risks, boRisk{
			BOID:       acc.BOID,
			ClientName: acc.ClientName,
			Exposure:   exposure,
			Leverage:   leverage,
			PnL:        pnl,
			Alert:      alert,
		})
	}

	return map[string]interface{}{
		"dealer_id":       dealerID,
		"total_exposure":  totalExposure,
		"bo_count":        len(accounts),
		"bo_risks":        risks,
		"timestamp":       time.Now().Format(time.RFC3339),
	}
}

// --- Audit Trail ---

// GetAuditLog returns audit log entries for a dealer
func (m *Manager) GetAuditLog(dealerID uint, limit int) ([]core.AuditLog, error) {
	var logs []core.AuditLog
	q := m.db.Where("dealer_id = ?", dealerID).Order("timestamp desc")
	if limit > 0 {
		q = q.Limit(limit)
	}
	if err := q.Find(&logs).Error; err != nil {
		return nil, err
	}
	return logs, nil
}

// --- Groups ---

// ListGroups returns all client groups for a dealer
func (m *Manager) ListGroups(dealerID uint) ([]core.ClientGroup, error) {
	var groups []core.ClientGroup
	if err := m.db.Preload("Members").
		Where("dealer_id = ? AND is_active = ?", dealerID, true).
		Find(&groups).Error; err != nil {
		return nil, err
	}
	return groups, nil
}

// --- Stock Quotes ---

// GetQuote returns the simulated quote for a symbol
func (m *Manager) GetQuote(symbol string) (StockQuote, bool) {
	m.quotesMu.RLock()
	defer m.quotesMu.RUnlock()
	q, ok := m.stockQuotes[strings.ToUpper(symbol)]
	return q, ok
}

// UpdateQuote updates the simulated price for a symbol (called by market data service)
func (m *Manager) UpdateQuote(symbol string, price float64) {
	m.quotesMu.Lock()
	defer m.quotesMu.Unlock()
	sym := strings.ToUpper(symbol)
	if q, ok := m.stockQuotes[sym]; ok {
		change := price - q.LTP
		m.stockQuotes[sym] = StockQuote{
			Symbol: sym,
			LTP:    price,
			Bid:    price - 0.5,
			Ask:    price + 0.5,
			Change: change,
		}
	}
}

// --- Internal helpers ---

func (m *Manager) findBOAccount(boID string) (*core.BOAccount, error) {
	var acc core.BOAccount
	if err := m.db.Where("bo_id = ?", boID).First(&acc).Error; err != nil {
		return nil, fmt.Errorf("BO account not found: %s", boID)
	}
	return &acc, nil
}

func (m *Manager) getOrCreateContext(dealerID uint) *core.DealerContext {
	if ctx, ok := m.contexts[dealerID]; ok {
		return ctx
	}
	ctx := &core.DealerContext{DealerID: dealerID}
	m.contexts[dealerID] = ctx
	return ctx
}

// checkBORisk performs pre-trade risk checks for a BO account order
func (m *Manager) checkBORisk(acc *core.BOAccount, symbol string, side core.OrderSide, qty float64, price *float64) error {
	m.quotesMu.RLock()
	quote, ok := m.stockQuotes[strings.ToUpper(symbol)]
	m.quotesMu.RUnlock()

	estimatedPrice := 0.0
	if price != nil {
		estimatedPrice = *price
	} else if ok {
		estimatedPrice = quote.LTP
	}

	orderValue := qty * estimatedPrice

	if side == core.OrderSideBuy {
		if acc.BuyingPower < orderValue {
			return fmt.Errorf("insufficient buying power (required: %.2f, available: %.2f)", orderValue, acc.BuyingPower)
		}
	}

	// Check concentration: single order should not exceed 50% of buying power
	if acc.BuyingPower > 0 && orderValue/acc.BuyingPower > 0.5 {
		return fmt.Errorf("order value exceeds 50%% of buying power — concentration limit")
	}

	return nil
}

// executeOrder simulates order execution and updates positions
func (m *Manager) executeOrder(order *core.BOOrder, acc *core.BOAccount) {
	m.quotesMu.RLock()
	quote, ok := m.stockQuotes[order.Symbol]
	m.quotesMu.RUnlock()

	execPrice := 0.0
	if order.Price != nil {
		execPrice = *order.Price
	} else if ok {
		execPrice = quote.LTP
	} else {
		execPrice = 100.0 // fallback
	}

	order.Status = core.OrderStatusFilled
	order.FilledQty = order.Quantity
	order.AvgFillPrice = &execPrice
	order.UpdatedAt = time.Now()
	m.db.Save(order)

	// Update position
	qty := order.Quantity
	if order.Side == core.OrderSideSell {
		qty = -qty
	}

	var pos core.BOPosition
	err := m.db.Where("bo_account_id = ? AND symbol = ?", acc.ID, order.Symbol).First(&pos).Error
	if err == nil {
		oldValue := pos.Quantity * pos.AvgPrice
		newValue := qty * execPrice
		pos.Quantity += qty
		if pos.Quantity != 0 {
			pos.AvgPrice = math.Abs((oldValue + newValue) / pos.Quantity)
		} else {
			pos.AvgPrice = 0
		}
		pos.LTP = execPrice
		pos.UpdatedAt = time.Now()
		m.db.Save(&pos)
	} else {
		pos = core.BOPosition{
			BOAccountID: acc.ID,
			Symbol:      order.Symbol,
			Quantity:    qty,
			AvgPrice:    execPrice,
			LTP:         execPrice,
		}
		m.db.Create(&pos)
	}

	// Adjust buying power
	if order.Side == core.OrderSideBuy {
		acc.BuyingPower -= order.Quantity * execPrice
	} else {
		acc.BuyingPower += order.Quantity * execPrice
	}
	m.db.Save(acc)
}

// calculateAllocations computes per-BO quantity allocations for a basket order
func (m *Manager) calculateAllocations(accounts []core.BOAccount, totalQty float64, weighted bool) map[uint]float64 {
	allocs := make(map[uint]float64, len(accounts))
	if !weighted {
		each := math.Floor(totalQty / float64(len(accounts)))
		for _, acc := range accounts {
			allocs[acc.ID] = each
		}
		return allocs
	}

	totalBP := 0.0
	for _, acc := range accounts {
		totalBP += acc.BuyingPower
	}
	if totalBP == 0 {
		each := math.Floor(totalQty / float64(len(accounts)))
		for _, acc := range accounts {
			allocs[acc.ID] = each
		}
		return allocs
	}

	for _, acc := range accounts {
		allocs[acc.ID] = math.Floor((acc.BuyingPower / totalBP) * totalQty)
	}
	return allocs
}

// writeAudit records an audit log entry
func (m *Manager) writeAudit(dealerID uint, boAccID *uint, action, details, ip string) {
	log := core.AuditLog{
		DealerID:    dealerID,
		BOAccountID: boAccID,
		Action:      action,
		Details:     details,
		IPAddress:   ip,
		Timestamp:   time.Now(),
	}
	m.db.Create(&log)
}
