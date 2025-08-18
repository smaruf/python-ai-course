// Package communication provides FIX/FAST protocol simulation for market connectivity
package communication

import (
	"encoding/json"
	"fmt"
	"sort"
	"strconv"
	"strings"
	"time"

	"github.com/google/uuid"
)

// MessageType represents FIX message types
type MessageType string

const (
	MessageTypeNewOrderSingle        MessageType = "D"
	MessageTypeExecutionReport       MessageType = "8"
	MessageTypeMarketDataSnapshot    MessageType = "W"
	MessageTypeMarketDataIncremental MessageType = "X"
	MessageTypeHeartbeat             MessageType = "0"
	MessageTypeLogon                 MessageType = "A"
	MessageTypeLogout                MessageType = "5"
)

// FIXMessage represents a FIX protocol message
type FIXMessage struct {
	MsgType MessageType       `json:"msg_type"`
	Fields  map[string]string `json:"fields"`
}

// NewFIXMessage creates a new FIX message
func NewFIXMessage(msgType MessageType, fields map[string]string) *FIXMessage {
	if fields == nil {
		fields = make(map[string]string)
	}
	
	fields["35"] = string(msgType)                                          // MsgType
	fields["52"] = time.Now().UTC().Format("20060102-15:04:05")           // SendingTime

	return &FIXMessage{
		MsgType: msgType,
		Fields:  fields,
	}
}

// ToFIXString converts message to FIX format string
func (fm *FIXMessage) ToFIXString() string {
	fixParts := []string{"8=FIX.4.4"} // BeginString

	// Sort field tags for consistent ordering
	var tags []string
	for tag := range fm.Fields {
		tags = append(tags, tag)
	}
	sort.Strings(tags)

	// Add all fields
	for _, tag := range tags {
		fixParts = append(fixParts, fmt.Sprintf("%s=%s", tag, fm.Fields[tag]))
	}

	// Calculate body length (everything after the BodyLength field)
	body := strings.Join(fixParts[1:], "|")
	bodyLength := fmt.Sprintf("9=%d", len(body))
	fixParts = append([]string{fixParts[0], bodyLength}, fixParts[1:]...)

	// Calculate checksum (simplified)
	fullMessage := strings.Join(fixParts, "|")
	checksum := 0
	for _, char := range fullMessage {
		checksum += int(char)
	}
	checksum = checksum % 256
	fixParts = append(fixParts, fmt.Sprintf("10=%03d", checksum))

	return strings.Join(fixParts, "|")
}

// FromFIXString parses FIX message from string
func FromFIXString(fixString string) (*FIXMessage, error) {
	parts := strings.Split(fixString, "|")
	fields := make(map[string]string)

	for _, part := range parts {
		if strings.Contains(part, "=") {
			tagValue := strings.SplitN(part, "=", 2)
			if len(tagValue) == 2 {
				fields[tagValue[0]] = tagValue[1]
			}
		}
	}

	msgTypeStr, exists := fields["35"]
	if !exists {
		return nil, fmt.Errorf("missing MsgType field")
	}

	return &FIXMessage{
		MsgType: MessageType(msgTypeStr),
		Fields:  fields,
	}, nil
}

// MessageHandler defines the interface for handling FIX messages
type MessageHandler func(*FIXMessage) error

// FIXEngine handles FIX protocol communication
type FIXEngine struct {
	senderCompID     string
	targetCompID     string
	seqNum          int
	sessions        map[string]interface{}
	messageHandlers map[string]MessageHandler
	isLoggedIn      bool
}

// NewFIXEngine creates a new FIX engine
func NewFIXEngine(senderCompID string) *FIXEngine {
	return &FIXEngine{
		senderCompID:    senderCompID,
		targetCompID:    "EXCHANGE",
		seqNum:         1,
		sessions:       make(map[string]interface{}),
		messageHandlers: make(map[string]MessageHandler),
		isLoggedIn:     false,
	}
}

// Logon simulates FIX logon process
func (fe *FIXEngine) Logon(username, password string) error {
	logonMsg := NewFIXMessage(MessageTypeLogon, map[string]string{
		"49":  fe.senderCompID,           // SenderCompID
		"56":  fe.targetCompID,           // TargetCompID
		"34":  strconv.Itoa(fe.seqNum),   // MsgSeqNum
		"553": username,                  // Username
		"554": password,                  // Password
		"98":  "0",                       // EncryptMethod (None)
		"108": "30",                      // HeartBtInt
	})

	fe.seqNum++

	// Simulate successful logon
	time.Sleep(100 * time.Millisecond)
	fe.isLoggedIn = true

	fmt.Printf("FIX Logon: %s\n", logonMsg.ToFIXString())
	return nil
}

// SendNewOrder sends new order via FIX protocol
func (fe *FIXEngine) SendNewOrder(orderData map[string]interface{}) (string, error) {
	if !fe.isLoggedIn {
		return "", fmt.Errorf("not logged in to FIX session")
	}

	clOrdID := uuid.New().String()[:8]

	// Convert order side
	side := "1" // Buy
	if orderData["side"].(string) == "SELL" {
		side = "2"
	}

	// Convert order type
	ordType := "1" // Market
	if orderData["order_type"].(string) == "LIMIT" {
		ordType = "2"
	}

	fields := map[string]string{
		"49": fe.senderCompID,
		"56": fe.targetCompID,
		"34": strconv.Itoa(fe.seqNum),
		"11": clOrdID,                                    // ClOrdID
		"55": orderData["symbol"].(string),               // Symbol
		"54": side,                                       // Side
		"38": fmt.Sprintf("%.0f", orderData["quantity"]), // OrderQty
		"40": ordType,                                    // OrdType
		"59": "0",                                        // TimeInForce (DAY)
	}

	// Add price for limit orders
	if price, exists := orderData["price"]; exists && price != nil {
		fields["44"] = fmt.Sprintf("%.2f", price.(float64))
	}

	// Add account if provided
	if account, exists := orderData["account"]; exists {
		fields["1"] = account.(string)
	} else {
		fields["1"] = "DEMO001"
	}

	orderMsg := NewFIXMessage(MessageTypeNewOrderSingle, fields)
	fe.seqNum++

	// Simulate sending message
	fixString := orderMsg.ToFIXString()
	fmt.Printf("FIX Order: %s\n", fixString)

	// Simulate execution report response
	go fe.simulateExecutionReport(clOrdID, orderData)

	return clOrdID, nil
}

// simulateExecutionReport simulates execution report from exchange
func (fe *FIXEngine) simulateExecutionReport(clOrdID string, orderData map[string]interface{}) {
	time.Sleep(100 * time.Millisecond)

	execID := uuid.New().String()[:8]

	// Simulate market execution
	fillPrice := 2050.0
	if price, exists := orderData["price"]; exists && price != nil {
		fillPrice = price.(float64)
	}

	if orderData["order_type"].(string) == "MARKET" {
		// Add small slippage for market orders
		slippage := 0.1
		if orderData["side"].(string) == "SELL" {
			slippage = -0.1
		}
		fillPrice = 2050.0 + slippage
	}

	side := "1"
	if orderData["side"].(string) == "SELL" {
		side = "2"
	}

	execReport := NewFIXMessage(MessageTypeExecutionReport, map[string]string{
		"49":  fe.targetCompID,
		"56":  fe.senderCompID,
		"34":  strconv.Itoa(fe.seqNum),
		"11":  clOrdID,                                      // ClOrdID
		"17":  execID,                                       // ExecID
		"150": "F",                                          // ExecType (Trade)
		"39":  "2",                                          // OrdStatus (Filled)
		"55":  orderData["symbol"].(string),                 // Symbol
		"54":  side,                                         // Side
		"38":  fmt.Sprintf("%.0f", orderData["quantity"]),   // OrderQty
		"32":  fmt.Sprintf("%.0f", orderData["quantity"]),   // LastQty
		"31":  fmt.Sprintf("%.2f", fillPrice),               // LastPx
		"14":  fmt.Sprintf("%.0f", orderData["quantity"]),   // CumQty
		"6":   fmt.Sprintf("%.2f", fillPrice),               // AvgPx
	})

	fmt.Printf("FIX Execution: %s\n", execReport.ToFIXString())

	// Call execution handler if registered
	if handler, exists := fe.messageHandlers["execution"]; exists {
		handler(execReport)
	}
}

// SubscribeMarketData subscribes to market data feeds
func (fe *FIXEngine) SubscribeMarketData(symbols []string) error {
	if !fe.isLoggedIn {
		return fmt.Errorf("not logged in to FIX session")
	}

	for _, symbol := range symbols {
		reqID := uuid.New().String()[:8]

		mdRequest := NewFIXMessage(MessageTypeMarketDataSnapshot, map[string]string{
			"49":  fe.senderCompID,
			"56":  fe.targetCompID,
			"34":  strconv.Itoa(fe.seqNum),
			"262": reqID,     // MDReqID
			"263": "1",       // SubscriptionRequestType (Snapshot + Updates)
			"264": "1",       // MarketDepth
			"267": "2",       // NoMDEntryTypes
			"269": "0|1",     // MDEntryType (Bid|Offer)
			"146": "1",       // NoRelatedSym
			"55":  symbol,    // Symbol
		})

		fe.seqNum++
		fmt.Printf("FIX Market Data Request: %s\n", mdRequest.ToFIXString())
	}

	// Start market data simulation
	go fe.simulateMarketData(symbols)
	return nil
}

// simulateMarketData simulates market data updates
func (fe *FIXEngine) simulateMarketData(symbols []string) {
	ticker := time.NewTicker(5 * time.Second)
	defer ticker.Stop()

	for range ticker.C {
		if !fe.isLoggedIn {
			break
		}

		for _, symbol := range symbols {
			// Generate random price movements
			basePrice := 2050.0
			priceChange := float64((time.Now().UnixNano()%1000 - 500)) / 250.0 // Random price change
			bidPrice := basePrice + priceChange - 0.5
			askPrice := basePrice + priceChange + 0.5

			mdUpdate := NewFIXMessage(MessageTypeMarketDataIncremental, map[string]string{
				"49":  fe.targetCompID,
				"56":  fe.senderCompID,
				"34":  strconv.Itoa(fe.seqNum),
				"55":  symbol,                           // Symbol
				"268": "2",                             // NoMDEntries
				"269": "0",                             // MDEntryType (Bid)
				"270": fmt.Sprintf("%.2f", bidPrice),   // MDEntryPx
				"271": "100",                           // MDEntrySize
				"272": fmt.Sprintf("%.2f", askPrice),   // MDEntryPx for Ask
			})

			// Call market data handler if registered
			if handler, exists := fe.messageHandlers["market_data"]; exists {
				handler(mdUpdate)
			}
		}
	}
}

// RegisterHandler registers a message handler
func (fe *FIXEngine) RegisterHandler(handlerType string, handler MessageHandler) {
	fe.messageHandlers[handlerType] = handler
}

// Logout performs FIX logout
func (fe *FIXEngine) Logout() error {
	if fe.isLoggedIn {
		logoutMsg := NewFIXMessage(MessageTypeLogout, map[string]string{
			"49": fe.senderCompID,
			"56": fe.targetCompID,
			"34": strconv.Itoa(fe.seqNum),
		})

		fmt.Printf("FIX Logout: %s\n", logoutMsg.ToFIXString())
		fe.isLoggedIn = false
	}
	return nil
}

// FASTDecoder provides simplified FAST (FIX Adapted for STreaming) decoder
type FASTDecoder struct {
	templates map[string]map[string]interface{}
}

// NewFASTDecoder creates a new FAST decoder
func NewFASTDecoder() *FASTDecoder {
	return &FASTDecoder{
		templates: map[string]map[string]interface{}{
			"MarketData": {
				"id":     1,
				"fields": []string{"Symbol", "BidPrice", "AskPrice", "LastPrice", "Volume"},
			},
			"Trade": {
				"id":     2,
				"fields": []string{"Symbol", "Price", "Quantity", "Timestamp"},
			},
		},
	}
}

// DecodeMessage decodes FAST message (simplified implementation)
func (fd *FASTDecoder) DecodeMessage(fastData []byte) (map[string]interface{}, error) {
	// This is a simplified decoder - real FAST is much more complex
	var data map[string]interface{}
	if err := json.Unmarshal(fastData, &data); err != nil {
		return map[string]interface{}{
			"error": "Failed to decode FAST message",
		}, err
	}
	return data, nil
}

// EncodeMessage encodes message to FAST format (simplified)
func (fd *FASTDecoder) EncodeMessage(templateName string, data map[string]interface{}) ([]byte, error) {
	template, exists := fd.templates[templateName]
	if !exists {
		return nil, fmt.Errorf("template %s not found", templateName)
	}

	message := map[string]interface{}{
		"template":    templateName,
		"template_id": template["id"],
		"data":        data,
		"timestamp":   time.Now().Format(time.RFC3339),
	}

	return json.Marshal(message)
}

// CommunicationManager manages FIX/FAST communication protocols
type CommunicationManager struct {
	fixEngine   *FIXEngine
	fastDecoder *FASTDecoder
	isConnected bool
}

// NewCommunicationManager creates a new communication manager
func NewCommunicationManager() *CommunicationManager {
	return &CommunicationManager{
		fixEngine:   NewFIXEngine("CSE_TRADING"),
		fastDecoder: NewFASTDecoder(),
		isConnected: false,
	}
}

// Connect connects to exchange via FIX protocol
func (cm *CommunicationManager) Connect(username, password string) error {
	if err := cm.fixEngine.Logon(username, password); err != nil {
		return fmt.Errorf("failed to connect: %w", err)
	}

	cm.isConnected = true

	// Subscribe to market data
	symbols := []string{"GOLD2024DEC", "GOLD2025MAR"}
	if err := cm.fixEngine.SubscribeMarketData(symbols); err != nil {
		return fmt.Errorf("failed to subscribe to market data: %w", err)
	}

	fmt.Println("✅ Connected to exchange via FIX protocol")
	return nil
}

// SendOrder sends order via FIX protocol
func (cm *CommunicationManager) SendOrder(orderData map[string]interface{}) (string, error) {
	if !cm.isConnected {
		return "", fmt.Errorf("not connected to exchange")
	}

	return cm.fixEngine.SendNewOrder(orderData)
}

// Disconnect disconnects from exchange
func (cm *CommunicationManager) Disconnect() error {
	if cm.isConnected {
		if err := cm.fixEngine.Logout(); err != nil {
			return err
		}
		cm.isConnected = false
		fmt.Println("🔌 Disconnected from exchange")
	}
	return nil
}

// RegisterExecutionHandler registers handler for execution reports
func (cm *CommunicationManager) RegisterExecutionHandler(handler MessageHandler) {
	cm.fixEngine.RegisterHandler("execution", handler)
}

// RegisterMarketDataHandler registers handler for market data updates
func (cm *CommunicationManager) RegisterMarketDataHandler(handler MessageHandler) {
	cm.fixEngine.RegisterHandler("market_data", handler)
}

// IsConnected returns connection status
func (cm *CommunicationManager) IsConnected() bool {
	return cm.isConnected
}