// Package terminal provides the Bloomberg-style terminal command parser
package terminal

import (
	"fmt"
	"strconv"
	"strings"

	"github.com/smaruf/python-ai-course/nasdaq-cse-go/internal/core"
	"github.com/smaruf/python-ai-course/nasdaq-cse-go/internal/dealer"
)

// Parser parses and dispatches Bloomberg-lite terminal commands
type Parser struct {
	dealerMgr *dealer.Manager
}

// NewParser creates a new terminal command parser
func NewParser(mgr *dealer.Manager) *Parser {
	return &Parser{dealerMgr: mgr}
}

// Execute parses a raw command string, dispatches it, and returns a response
func (p *Parser) Execute(raw string, dealerID uint) core.TerminalCommandResponse {
	raw = strings.TrimSpace(raw)
	if raw == "" {
		return errorResp("empty command")
	}

	tokens := strings.Fields(raw)
	cmd := strings.ToLower(tokens[0])

	switch {
	// b BO1001 GP 100 350      — limit buy
	// b BO1001 GP 100          — market buy (no price)
	case cmd == "b":
		return p.handleBuy(tokens, dealerID, false)

	// bm BO1003 GP 100         — explicit market buy
	case cmd == "bm":
		return p.handleBuy(tokens, dealerID, true)

	// s BO1002 BATBC 500 25.4  — limit sell
	// s BO1002 BATBC 500       — market sell
	case cmd == "s":
		return p.handleSell(tokens, dealerID, false)

	// sm BO1003 GP 100         — explicit market sell
	case cmd == "sm":
		return p.handleSell(tokens, dealerID, true)

	// bo maruf                 — search BO accounts
	case cmd == "bo":
		return p.handleBOSearch(tokens, dealerID)

	// switch BO1002            — switch active BO context
	case cmd == "switch":
		return p.handleSwitch(tokens, dealerID)

	// clone BO1001 -> BO1005   — clone last order
	case cmd == "clone":
		return p.handleClone(tokens, dealerID)

	// repeat last for BO1002   — repeat last order for a BO
	case cmd == "repeat":
		return p.handleRepeat(tokens, dealerID)

	// reverse GP BO1003        — close/reverse position
	case cmd == "reverse":
		return p.handleReverse(tokens, dealerID)

	// basket GP 10000 weighted — basket order
	case cmd == "basket":
		return p.handleBasket(tokens, dealerID)

	// alloc GP 1M proportional — proportional allocation
	case cmd == "alloc":
		return p.handleAlloc(tokens, dealerID)

	// dashboard BO1001         — BO dashboard
	case cmd == "dashboard", cmd == "dash":
		return p.handleDashboard(tokens, dealerID)

	// pos BO1001               — BO positions
	case cmd == "pos", cmd == "positions":
		return p.handlePositions(tokens, dealerID)

	// orders BO1001            — BO order history
	case cmd == "orders":
		return p.handleOrders(tokens, dealerID)

	// watch BO1001 add GP      — watchlist management
	case cmd == "watch":
		return p.handleWatch(tokens, dealerID)

	// risk                     — dealer risk dashboard
	case cmd == "risk":
		return p.handleRisk(dealerID)

	// help                     — show command reference
	case cmd == "help":
		return p.handleHelp()

	default:
		return errorResp(fmt.Sprintf("unknown command '%s' — type 'help' for usage", cmd))
	}
}

// --- Command handlers ---

// handleBuy processes buy commands: b BO1001 GP 100 [350]
// With group syntax:           b [GROUP-HNI] GP 100 [350]
func (p *Parser) handleBuy(tokens []string, dealerID uint, forceMarket bool) core.TerminalCommandResponse {
	return p.handleOrderCmd(tokens, dealerID, core.OrderSideBuy, forceMarket)
}

// handleSell processes sell commands: s BO1002 BATBC 500 [25.4]
func (p *Parser) handleSell(tokens []string, dealerID uint, forceMarket bool) core.TerminalCommandResponse {
	return p.handleOrderCmd(tokens, dealerID, core.OrderSideSell, forceMarket)
}

// handleOrderCmd is the shared handler for b/bm/s/sm commands
func (p *Parser) handleOrderCmd(tokens []string, dealerID uint, side core.OrderSide, forceMarket bool) core.TerminalCommandResponse {
	// Minimum: cmd BOID SYMBOL QTY
	if len(tokens) < 4 {
		return errorResp("usage: b/s <BO_ID | [GROUP]> <SYMBOL> <QTY> [PRICE]")
	}

	boOrGroup := tokens[1]
	symbol := strings.ToUpper(tokens[2])
	qty, err := strconv.ParseFloat(tokens[3], 64)
	if err != nil || qty <= 0 {
		return errorResp(fmt.Sprintf("invalid quantity: %s", tokens[3]))
	}

	var price *float64
	orderType := core.OrderTypeMarket
	if !forceMarket && len(tokens) >= 5 {
		p64, e := strconv.ParseFloat(tokens[4], 64)
		if e == nil && p64 > 0 {
			price = &p64
			orderType = core.OrderTypeLimit
		}
	}

	// Group order syntax: b [GROUP-HNI] GP 100 350
	if strings.HasPrefix(boOrGroup, "[") && strings.HasSuffix(boOrGroup, "]") {
		groupName := boOrGroup[1 : len(boOrGroup)-1]
		req := core.GroupOrderRequest{
			GroupName: groupName,
			Symbol:    symbol,
			Side:      side,
			OrderType: orderType,
			Quantity:  qty,
			Price:     price,
			DealerID:  dealerID,
		}
		orders, errs := p.dealerMgr.SubmitGroupOrder(req)
		return groupOrderResp(groupName, symbol, side, qty, orders, errs)
	}

	// Single BO order
	req := core.BOOrderCreateRequest{
		BOID:      boOrGroup,
		Symbol:    symbol,
		Side:      side,
		OrderType: orderType,
		Quantity:  qty,
		Price:     price,
		DealerID:  dealerID,
	}
	order, err := p.dealerMgr.SubmitBOOrder(req)
	if err != nil {
		return errorResp(err.Error())
	}

	priceStr := "MARKET"
	if price != nil {
		priceStr = fmt.Sprintf("%.2f", *price)
	}
	return core.TerminalCommandResponse{
		Success: true,
		Output:  fmt.Sprintf("✅ %s %s: %s x%.0f @ %s — %s", boOrGroup, side, symbol, qty, priceStr, order.Status),
		Data:    order,
	}
}

func (p *Parser) handleBOSearch(tokens []string, dealerID uint) core.TerminalCommandResponse {
	if len(tokens) < 2 {
		return errorResp("usage: bo <search_term>")
	}
	query := strings.Join(tokens[1:], " ")
	results, err := p.dealerMgr.SearchBO(dealerID, query)
	if err != nil {
		return errorResp(err.Error())
	}
	if len(results) == 0 {
		return core.TerminalCommandResponse{Success: true, Output: fmt.Sprintf("No BO accounts matching '%s'", query)}
	}

	var lines []string
	for _, r := range results {
		lines = append(lines, fmt.Sprintf("  %-10s %-25s BP:%.2f Pos:%d PendOrd:%d",
			r.BOID, r.ClientName, r.BuyingPower, r.PositionCount, r.PendingOrders))
	}
	return core.TerminalCommandResponse{
		Success: true,
		Output:  "BO Search Results:\n" + strings.Join(lines, "\n"),
		Data:    results,
	}
}

func (p *Parser) handleSwitch(tokens []string, dealerID uint) core.TerminalCommandResponse {
	if len(tokens) < 2 {
		return errorResp("usage: switch <BO_ID>")
	}
	msg, err := p.dealerMgr.SwitchBO(dealerID, strings.ToUpper(tokens[1]))
	if err != nil {
		return errorResp(err.Error())
	}
	return core.TerminalCommandResponse{Success: true, Output: msg}
}

// handleClone processes: clone BO1001 -> BO1005
func (p *Parser) handleClone(tokens []string, dealerID uint) core.TerminalCommandResponse {
	// Accepted forms: clone BO1001 -> BO1005   or   clone BO1001 BO1005
	if len(tokens) < 3 {
		return errorResp("usage: clone <SOURCE_BO> -> <TARGET_BO>")
	}
	src := strings.ToUpper(tokens[1])
	tgt := ""
	if len(tokens) >= 4 && tokens[2] == "->" {
		tgt = strings.ToUpper(tokens[3])
	} else if len(tokens) == 3 {
		tgt = strings.ToUpper(tokens[2])
	} else {
		return errorResp("usage: clone <SOURCE_BO> -> <TARGET_BO>")
	}

	req := core.CloneOrderRequest{SourceBOID: src, TargetBOID: tgt, DealerID: dealerID}
	order, err := p.dealerMgr.CloneOrder(req)
	if err != nil {
		return errorResp(err.Error())
	}
	return core.TerminalCommandResponse{
		Success: true,
		Output:  fmt.Sprintf("✅ Cloned last order from %s to %s (order %s)", src, tgt, order.OrderID[:8]),
		Data:    order,
	}
}

// handleRepeat processes: repeat last for BO1002
func (p *Parser) handleRepeat(tokens []string, dealerID uint) core.TerminalCommandResponse {
	// Forms: repeat last for BO1002   or   repeat BO1002
	boID := ""
	if len(tokens) >= 4 && tokens[1] == "last" && tokens[2] == "for" {
		boID = strings.ToUpper(tokens[3])
	} else if len(tokens) >= 2 {
		boID = strings.ToUpper(tokens[1])
	} else {
		return errorResp("usage: repeat last for <BO_ID>")
	}

	order, err := p.dealerMgr.RepeatLastOrder(dealerID, boID)
	if err != nil {
		return errorResp(err.Error())
	}
	return core.TerminalCommandResponse{
		Success: true,
		Output:  fmt.Sprintf("✅ Repeated last order for %s (order %s)", boID, order.OrderID[:8]),
		Data:    order,
	}
}

// handleReverse processes: reverse GP BO1003
func (p *Parser) handleReverse(tokens []string, dealerID uint) core.TerminalCommandResponse {
	if len(tokens) < 3 {
		return errorResp("usage: reverse <SYMBOL> <BO_ID>")
	}
	symbol := strings.ToUpper(tokens[1])
	boID := strings.ToUpper(tokens[2])

	order, err := p.dealerMgr.ReversePosition(dealerID, symbol, boID)
	if err != nil {
		return errorResp(err.Error())
	}
	return core.TerminalCommandResponse{
		Success: true,
		Output:  fmt.Sprintf("✅ Reversed %s position for %s", symbol, boID),
		Data:    order,
	}
}

// handleBasket processes: basket GP 10000 [weighted]
func (p *Parser) handleBasket(tokens []string, dealerID uint) core.TerminalCommandResponse {
	if len(tokens) < 3 {
		return errorResp("usage: basket <SYMBOL> <TOTAL_QTY> [weighted]")
	}
	symbol := strings.ToUpper(tokens[1])
	totalQty, err := parseValue(tokens[2])
	if err != nil || totalQty <= 0 {
		return errorResp(fmt.Sprintf("invalid quantity: %s", tokens[2]))
	}

	weighted := len(tokens) >= 4 && strings.EqualFold(tokens[3], "weighted")

	req := core.BasketOrderRequest{
		Symbol:   symbol,
		Side:     core.OrderSideBuy,
		TotalQty: totalQty,
		DealerID: dealerID,
		Weighted: weighted,
	}
	orders, errs := p.dealerMgr.SubmitBasketOrder(req)

	return basketResp(symbol, totalQty, orders, errs)
}

// handleAlloc processes: alloc GP 1M proportional
func (p *Parser) handleAlloc(tokens []string, dealerID uint) core.TerminalCommandResponse {
	if len(tokens) < 3 {
		return errorResp("usage: alloc <SYMBOL> <VALUE> [proportional]")
	}
	symbol := strings.ToUpper(tokens[1])
	value, err := parseValue(tokens[2])
	if err != nil || value <= 0 {
		return errorResp(fmt.Sprintf("invalid value: %s", tokens[2]))
	}

	req := core.AllocOrderRequest{Symbol: symbol, TotalValue: value, DealerID: dealerID}
	orders, errs := p.dealerMgr.SubmitAllocOrder(req)

	return basketResp(symbol, value, orders, errs)
}

func (p *Parser) handleDashboard(tokens []string, dealerID uint) core.TerminalCommandResponse {
	boID := ""
	if len(tokens) >= 2 {
		boID = strings.ToUpper(tokens[1])
	} else {
		ctx := p.dealerMgr.GetContext(dealerID)
		boID = ctx.ActiveBOID
	}
	if boID == "" {
		return errorResp("no active BO — use: dashboard <BO_ID>")
	}
	dash, err := p.dealerMgr.GetBODashboard(boID)
	if err != nil {
		return errorResp(err.Error())
	}
	out := fmt.Sprintf(
		"┌─────────────────────────┐\n"+
			"│ BO: %-19s │\n"+
			"│ Client: %-15s │\n"+
			"│ Buying Power: %-9.2f │\n"+
			"│ Exposure: %-13.2f │\n"+
			"│ Margin: %-15s │\n"+
			"│ Holdings: %-13d │\n"+
			"│ Unrealized P/L: %-7.2f │\n"+
			"│ Pending Orders: %-7d │\n"+
			"└─────────────────────────┘",
		dash.BOID, dash.ClientName, dash.BuyingPower, dash.Exposure,
		dash.MarginStatus, dash.Holdings, dash.UnrealizedPnL, dash.PendingOrders,
	)
	return core.TerminalCommandResponse{Success: true, Output: out, Data: dash}
}

func (p *Parser) handlePositions(tokens []string, dealerID uint) core.TerminalCommandResponse {
	boID := ""
	if len(tokens) >= 2 {
		boID = strings.ToUpper(tokens[1])
	} else {
		ctx := p.dealerMgr.GetContext(dealerID)
		boID = ctx.ActiveBOID
	}
	if boID == "" {
		return errorResp("no active BO — use: pos <BO_ID>")
	}
	positions, err := p.dealerMgr.GetBOPositions(boID)
	if err != nil {
		return errorResp(err.Error())
	}
	if len(positions) == 0 {
		return core.TerminalCommandResponse{Success: true, Output: fmt.Sprintf("%s has no open positions", boID)}
	}
	header := fmt.Sprintf("%-10s %8s %8s %8s %10s", "Symbol", "Qty", "AvgPrice", "LTP", "P/L")
	sep := strings.Repeat("-", 50)
	var rows []string
	for _, p2 := range positions {
		rows = append(rows, fmt.Sprintf("%-10s %8.0f %8.2f %8.2f %+10.2f", p2.Symbol, p2.Quantity, p2.AvgPrice, p2.LTP, p2.UnrealizedPnL))
	}
	return core.TerminalCommandResponse{
		Success: true,
		Output:  header + "\n" + sep + "\n" + strings.Join(rows, "\n"),
		Data:    positions,
	}
}

func (p *Parser) handleOrders(tokens []string, dealerID uint) core.TerminalCommandResponse {
	boID := ""
	if len(tokens) >= 2 {
		boID = strings.ToUpper(tokens[1])
	} else {
		ctx := p.dealerMgr.GetContext(dealerID)
		boID = ctx.ActiveBOID
	}
	if boID == "" {
		return errorResp("no active BO — use: orders <BO_ID>")
	}
	orders, err := p.dealerMgr.GetBOOrders(boID, 20)
	if err != nil {
		return errorResp(err.Error())
	}
	if len(orders) == 0 {
		return core.TerminalCommandResponse{Success: true, Output: fmt.Sprintf("%s has no orders", boID)}
	}
	header := fmt.Sprintf("%-8s %-6s %-10s %8s %8s %-10s", "ID", "Side", "Symbol", "Qty", "Price", "Status")
	sep := strings.Repeat("-", 55)
	var rows []string
	for _, o := range orders {
		priceStr := "MARKET"
		if o.Price != nil {
			priceStr = fmt.Sprintf("%.2f", *o.Price)
		}
		rows = append(rows, fmt.Sprintf("%-8s %-6s %-10s %8.0f %8s %-10s",
			o.OrderID[:8], o.Side, o.Symbol, o.Quantity, priceStr, o.Status))
	}
	return core.TerminalCommandResponse{
		Success: true,
		Output:  header + "\n" + sep + "\n" + strings.Join(rows, "\n"),
		Data:    orders,
	}
}

func (p *Parser) handleWatch(tokens []string, dealerID uint) core.TerminalCommandResponse {
	// watch BO1001 add GP
	if len(tokens) < 4 || strings.ToLower(tokens[2]) != "add" {
		return errorResp("usage: watch <BO_ID> add <SYMBOL>")
	}
	boID := strings.ToUpper(tokens[1])
	symbol := strings.ToUpper(tokens[3])
	if err := p.dealerMgr.AddToWatchlist(boID, symbol); err != nil {
		return errorResp(err.Error())
	}
	return core.TerminalCommandResponse{Success: true, Output: fmt.Sprintf("✅ Added %s to %s watchlist", symbol, boID)}
}

func (p *Parser) handleRisk(dealerID uint) core.TerminalCommandResponse {
	data := p.dealerMgr.GetBORiskDashboard(dealerID)
	return core.TerminalCommandResponse{Success: true, Output: "Risk dashboard loaded", Data: data}
}

func (p *Parser) handleHelp() core.TerminalCommandResponse {
	help := `Bloomberg-Lite Terminal Command Reference
==========================================
ORDERS
  b  <BO_ID> <SYM> <QTY> [PRICE]    Limit/market buy for BO account
  bm <BO_ID> <SYM> <QTY>            Market buy
  s  <BO_ID> <SYM> <QTY> [PRICE]    Limit/market sell for BO account
  sm <BO_ID> <SYM> <QTY>            Market sell
  b  [GROUP-HNI] <SYM> <QTY> [PX]  Group order for all BOs in group

BASKET & ALLOCATION
  basket <SYM> <QTY> [weighted]     Distribute order across all BOs
  alloc  <SYM> <VALUE> [proportional] Allocate by buying-power weight

DEALER WORKFLOW
  switch  <BO_ID>                   Switch active BO context
  clone   <SRC_BO> -> <TGT_BO>     Clone last order to another BO
  repeat  last for <BO_ID>          Repeat last order for a BO
  reverse <SYM> <BO_ID>            Reverse (close) position

INFORMATION
  bo       <SEARCH>                 Search BO accounts
  dashboard [BO_ID]                 Show BO dashboard panel
  pos      [BO_ID]                  Show BO positions
  orders   [BO_ID]                  Show BO order history
  watch    <BO_ID> add <SYM>       Add to BO watchlist
  risk                              Show dealer risk dashboard
  help                              Show this help`
	return core.TerminalCommandResponse{Success: true, Output: help}
}

// --- Helpers ---

func errorResp(msg string) core.TerminalCommandResponse {
	return core.TerminalCommandResponse{Success: false, Error: msg, Output: "❌ " + msg}
}

func groupOrderResp(group, symbol string, side core.OrderSide, qty float64, orders []core.BOOrder, errs []error) core.TerminalCommandResponse {
	lines := []string{fmt.Sprintf("Group order [%s]: %s %s x%.0f", group, side, symbol, qty)}
	for _, o := range orders {
		lines = append(lines, fmt.Sprintf("  ✅ %s order %s", o.Status, o.OrderID[:8]))
	}
	for _, e := range errs {
		lines = append(lines, fmt.Sprintf("  ❌ %s", e.Error()))
	}
	return core.TerminalCommandResponse{
		Success: len(orders) > 0,
		Output:  strings.Join(lines, "\n"),
		Data:    orders,
	}
}

func basketResp(symbol string, totalQty float64, orders []core.BOOrder, errs []error) core.TerminalCommandResponse {
	lines := []string{fmt.Sprintf("Basket %s total=%.0f", symbol, totalQty)}
	for _, o := range orders {
		lines = append(lines, fmt.Sprintf("  ✅ BO[%d] order %s x%.0f", o.BOAccountID, o.OrderID[:8], o.Quantity))
	}
	for _, e := range errs {
		lines = append(lines, fmt.Sprintf("  ❌ %s", e.Error()))
	}
	return core.TerminalCommandResponse{
		Success: len(orders) > 0,
		Output:  strings.Join(lines, "\n"),
		Data:    orders,
	}
}

// parseValue parses numeric values optionally suffixed with K/M/B
func parseValue(s string) (float64, error) {
	s = strings.TrimSpace(s)
	multiplier := 1.0
	upper := strings.ToUpper(s)
	if strings.HasSuffix(upper, "B") {
		multiplier = 1_000_000_000
		s = s[:len(s)-1]
	} else if strings.HasSuffix(upper, "M") {
		multiplier = 1_000_000
		s = s[:len(s)-1]
	} else if strings.HasSuffix(upper, "K") {
		multiplier = 1_000
		s = s[:len(s)-1]
	}
	v, err := strconv.ParseFloat(s, 64)
	if err != nil {
		return 0, err
	}
	return v * multiplier, nil
}
