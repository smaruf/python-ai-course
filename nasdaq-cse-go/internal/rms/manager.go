// Package rms provides Risk Management System functionality
package rms

import (
	"fmt"
	"math"
	"time"

	"github.com/smaruf/python-ai-course/nasdaq-cse-go/internal/core"
	"gorm.io/gorm"
)

// RiskLimits defines various risk limits for trading
type RiskLimits struct {
	MaxPositionSize           float64 // Max position size per contract
	MaxTotalExposure          float64 // Max total exposure per user
	MarginCallThreshold       float64 // Margin call at 80% utilization
	ForceLiquidationThreshold float64 // Force liquidation at 95%
	MaxDailyLoss              float64 // Max 5% daily loss
	ConcentrationLimit        float64 // Max 30% in single position
	VolatilityLimit           float64 // Max 10% daily volatility exposure
}

// DefaultRiskLimits returns default risk limits
func DefaultRiskLimits() RiskLimits {
	return RiskLimits{
		MaxPositionSize:           1000,
		MaxTotalExposure:          500000,
		MarginCallThreshold:       0.8,
		ForceLiquidationThreshold: 0.95,
		MaxDailyLoss:              0.05,
		ConcentrationLimit:        0.3,
		VolatilityLimit:           0.1,
	}
}

// RiskAlert represents a risk alert
type RiskAlert struct {
	Type           string `json:"type"`
	Severity       string `json:"severity"`
	Message        string `json:"message"`
	Recommendation string `json:"recommendation"`
}

// RiskMetrics contains calculated risk metrics
type RiskMetrics struct {
	TotalExposure      float64 `json:"total_exposure"`
	LeverageRatio      float64 `json:"leverage_ratio"`
	ConcentrationRatio float64 `json:"concentration_ratio"`
	UnrealizedPnL      float64 `json:"unrealized_pnl"`
	PositionCount      int     `json:"position_count"`
	LargestPosition    float64 `json:"largest_position"`
}

// VaRMetrics contains Value at Risk calculations
type VaRMetrics struct {
	VaR               float64 `json:"var"`
	ExpectedShortfall float64 `json:"expected_shortfall"`
	ConfidenceLevel   float64 `json:"confidence_level"`
	TimeHorizonDays   int     `json:"time_horizon_days"`
	TotalExposure     float64 `json:"total_exposure"`
}

// MarginStatus contains margin monitoring information
type MarginStatus struct {
	MarginAdequate       bool    `json:"margin_adequate"`
	MarginCall           bool    `json:"margin_call"`
	ForceLiquidation     bool    `json:"force_liquidation"`
	MarginUtilization    float64 `json:"margin_utilization"`
	TotalMarginRequired  float64 `json:"total_margin_required"`
	AvailableMargin      float64 `json:"available_margin"`
	AccountEquity        float64 `json:"account_equity"`
}

// RiskManager manages trading risks and monitoring
type RiskManager struct {
	db         *gorm.DB
	riskLimits RiskLimits
	riskAlerts []RiskAlert
}

// NewRiskManager creates a new risk manager
func NewRiskManager(db *gorm.DB) *RiskManager {
	return &RiskManager{
		db:         db,
		riskLimits: DefaultRiskLimits(),
		riskAlerts: make([]RiskAlert, 0),
	}
}

// CheckPreTradeRisk checks risk limits before allowing a trade
func (rm *RiskManager) CheckPreTradeRisk(userID uint, orderRequest core.OrderCreateRequest) map[string]interface{} {
	var user core.User
	if err := rm.db.First(&user, userID).Error; err != nil {
		return map[string]interface{}{
			"allowed": false,
			"reason":  "User not found",
		}
	}

	// Get user's current positions
	var positions []core.Position
	rm.db.Where("user_id = ?", userID).Find(&positions)

	// Calculate current exposure
	totalExposure := 0.0
	for _, pos := range positions {
		totalExposure += math.Abs(pos.Quantity * pos.AvgEntryPrice)
	}

	// Check position size limit
	estimatedPrice := 2000.0 // Default price estimate
	newExposure := orderRequest.Quantity * estimatedPrice
	if newExposure > rm.riskLimits.MaxPositionSize*estimatedPrice {
		return map[string]interface{}{
			"allowed": false,
			"reason":  "Position size exceeds limit",
		}
	}

	// Check total exposure limit
	if totalExposure+newExposure > rm.riskLimits.MaxTotalExposure {
		return map[string]interface{}{
			"allowed": false,
			"reason":  "Total exposure would exceed limit",
		}
	}

	// Check margin requirements
	marginCheck := rm.checkMarginRequirements(&user, positions, orderRequest)
	if !marginCheck["sufficient"].(bool) {
		return map[string]interface{}{
			"allowed": false,
			"reason":  marginCheck["reason"],
		}
	}

	// Check concentration limits
	concentrationCheck := rm.checkConcentrationLimits(positions, orderRequest)
	if !concentrationCheck["allowed"].(bool) {
		return map[string]interface{}{
			"allowed": false,
			"reason":  concentrationCheck["reason"],
		}
	}

	return map[string]interface{}{
		"allowed": true,
		"reason":  "Risk checks passed",
	}
}

// CheckPostTradeRisk checks risk metrics after a trade is executed
func (rm *RiskManager) CheckPostTradeRisk(userID uint) map[string]interface{} {
	var user core.User
	if err := rm.db.First(&user, userID).Error; err != nil {
		return map[string]interface{}{
			"error": "User not found",
		}
	}

	var positions []core.Position
	rm.db.Where("user_id = ?", userID).Find(&positions)

	riskMetrics := rm.calculateRiskMetrics(&user, positions)
	alerts := rm.generateRiskAlerts(riskMetrics)

	return map[string]interface{}{
		"user_id":      userID,
		"risk_metrics": riskMetrics,
		"alerts":       alerts,
		"timestamp":    time.Now().Format(time.RFC3339),
	}
}

// MonitorMarginRequirements monitors margin requirements and generates margin calls
func (rm *RiskManager) MonitorMarginRequirements(userID uint, currentPrices map[uint]float64) MarginStatus {
	var user core.User
	if err := rm.db.First(&user, userID).Error; err != nil {
		return MarginStatus{MarginAdequate: true, MarginCall: false}
	}

	var positions []core.Position
	rm.db.Where("user_id = ?", userID).Find(&positions)

	if len(positions) == 0 {
		return MarginStatus{MarginAdequate: true, MarginCall: false}
	}

	// Calculate total margin requirement
	totalMarginRequired := 0.0
	totalUnrealizedPnL := 0.0

	for _, position := range positions {
		if currentPrice, exists := currentPrices[position.ContractID]; exists {
			// Update unrealized P&L
			if position.Quantity != 0 {
				position.UnrealizedPnL = (currentPrice - position.AvgEntryPrice) * position.Quantity
				totalUnrealizedPnL += position.UnrealizedPnL
			}

			// Get contract for margin calculation
			var contract core.Contract
			if err := rm.db.First(&contract, position.ContractID).Error; err == nil {
				marginPerUnit := contract.MaintenanceMargin
				totalMarginRequired += math.Abs(position.Quantity) * marginPerUnit
			}
		}
	}

	// Calculate available margin
	accountEquity := user.AccountBalance + totalUnrealizedPnL
	availableMargin := accountEquity - totalMarginRequired
	var marginUtilization float64
	if accountEquity > 0 {
		marginUtilization = totalMarginRequired / accountEquity
	} else {
		marginUtilization = 1.0
	}

	marginCall := marginUtilization > rm.riskLimits.MarginCallThreshold
	forceLiquidation := marginUtilization > rm.riskLimits.ForceLiquidationThreshold

	// Update user's margin available
	user.MarginAvailable = math.Max(0, availableMargin)
	rm.db.Save(&user)

	return MarginStatus{
		MarginAdequate:       !marginCall,
		MarginCall:           marginCall,
		ForceLiquidation:     forceLiquidation,
		MarginUtilization:    marginUtilization,
		TotalMarginRequired:  totalMarginRequired,
		AvailableMargin:      availableMargin,
		AccountEquity:        accountEquity,
	}
}

// CalculateVaR calculates Value at Risk for user's portfolio
func (rm *RiskManager) CalculateVaR(userID uint, confidenceLevel float64, timeHorizon int) VaRMetrics {
	var positions []core.Position
	rm.db.Where("user_id = ?", userID).Find(&positions)

	if len(positions) == 0 {
		return VaRMetrics{
			VaR:               0.0,
			ExpectedShortfall: 0.0,
			ConfidenceLevel:   confidenceLevel,
			TimeHorizonDays:   timeHorizon,
		}
	}

	// Calculate total exposure
	totalExposure := 0.0
	for _, pos := range positions {
		totalExposure += math.Abs(pos.Quantity * pos.AvgEntryPrice)
	}

	// Simplified VaR calculation (parametric method)
	// Assume 2% daily volatility for gold
	dailyVolatility := 0.02

	// For 95% confidence level, z-score is approximately 1.65
	// For 99% confidence level, z-score is approximately 2.33
	var zScore float64
	switch {
	case confidenceLevel >= 0.99:
		zScore = 2.33
	case confidenceLevel >= 0.95:
		zScore = 1.65
	default:
		zScore = 1.28 // 90% confidence
	}

	// VaR calculation
	var1Day := totalExposure * dailyVolatility * zScore
	varTimeHorizon := var1Day * math.Sqrt(float64(timeHorizon))

	// Expected Shortfall (simplified)
	expectedShortfall := varTimeHorizon * 1.3

	return VaRMetrics{
		VaR:               math.Abs(varTimeHorizon),
		ExpectedShortfall: math.Abs(expectedShortfall),
		ConfidenceLevel:   confidenceLevel,
		TimeHorizonDays:   timeHorizon,
		TotalExposure:     totalExposure,
	}
}

// GenerateRiskReport generates comprehensive risk report for a user
func (rm *RiskManager) GenerateRiskReport(userID uint, currentPrices map[uint]float64) map[string]interface{} {
	marginStatus := rm.MonitorMarginRequirements(userID, currentPrices)
	varMetrics := rm.CalculateVaR(userID, 0.95, 1)
	postTradeRisk := rm.CheckPostTradeRisk(userID)

	riskScore := rm.calculateRiskScore(marginStatus, varMetrics, postTradeRisk)

	return map[string]interface{}{
		"user_id":         userID,
		"timestamp":       time.Now().Format(time.RFC3339),
		"risk_score":      riskScore,
		"margin_status":   marginStatus,
		"var_metrics":     varMetrics,
		"risk_metrics":    postTradeRisk["risk_metrics"],
		"alerts":          postTradeRisk["alerts"],
		"recommendations": rm.generateRiskRecommendations(riskScore, marginStatus, varMetrics),
	}
}

// checkMarginRequirements checks if user has sufficient margin for new order
func (rm *RiskManager) checkMarginRequirements(user *core.User, positions []core.Position, orderRequest core.OrderCreateRequest) map[string]interface{} {
	// Get contract for margin calculation
	var contract core.Contract
	if err := rm.db.Where("symbol = ?", orderRequest.ContractSymbol).First(&contract).Error; err != nil {
		return map[string]interface{}{
			"sufficient": false,
			"reason":     "Contract not found",
		}
	}

	// Calculate additional margin needed
	additionalMargin := orderRequest.Quantity * contract.InitialMargin

	if user.MarginAvailable < additionalMargin {
		return map[string]interface{}{
			"sufficient": false,
			"reason":     "Insufficient margin available",
		}
	}

	return map[string]interface{}{
		"sufficient": true,
		"reason":     "Margin requirements met",
	}
}

// checkConcentrationLimits checks position concentration limits
func (rm *RiskManager) checkConcentrationLimits(positions []core.Position, orderRequest core.OrderCreateRequest) map[string]interface{} {
	totalExposure := 0.0
	for _, pos := range positions {
		totalExposure += math.Abs(pos.Quantity * pos.AvgEntryPrice)
	}

	if totalExposure == 0 {
		return map[string]interface{}{
			"allowed": true,
			"reason":  "No existing positions",
		}
	}

	// Calculate exposure for the contract in the order (simplified)
	contractExposure := 0.0
	estimatedPrice := 2000.0 // Default price estimate
	
	newExposure := orderRequest.Quantity * estimatedPrice
	projectedContractExposure := contractExposure + newExposure
	projectedConcentration := projectedContractExposure / (totalExposure + newExposure)

	if projectedConcentration > rm.riskLimits.ConcentrationLimit {
		return map[string]interface{}{
			"allowed": false,
			"reason":  fmt.Sprintf("Position concentration would exceed %.0f%% limit", rm.riskLimits.ConcentrationLimit*100),
		}
	}

	return map[string]interface{}{
		"allowed": true,
		"reason":  "Concentration limits satisfied",
	}
}

// calculateRiskMetrics calculates comprehensive risk metrics
func (rm *RiskManager) calculateRiskMetrics(user *core.User, positions []core.Position) RiskMetrics {
	if len(positions) == 0 {
		return RiskMetrics{
			TotalExposure:      0,
			LeverageRatio:      0,
			ConcentrationRatio: 0,
			UnrealizedPnL:      0,
			PositionCount:      0,
		}
	}

	totalExposure := 0.0
	totalUnrealizedPnL := 0.0
	var positionExposures []float64

	for _, pos := range positions {
		exposure := math.Abs(pos.Quantity * pos.AvgEntryPrice)
		totalExposure += exposure
		totalUnrealizedPnL += pos.UnrealizedPnL
		positionExposures = append(positionExposures, exposure)
	}

	var leverageRatio float64
	if user.AccountBalance > 0 {
		leverageRatio = totalExposure / user.AccountBalance
	}

	// Calculate concentration (largest position as % of total)
	maxPositionExposure := 0.0
	for _, exposure := range positionExposures {
		if exposure > maxPositionExposure {
			maxPositionExposure = exposure
		}
	}

	var concentrationRatio float64
	if totalExposure > 0 {
		concentrationRatio = maxPositionExposure / totalExposure
	}

	return RiskMetrics{
		TotalExposure:      totalExposure,
		LeverageRatio:      leverageRatio,
		ConcentrationRatio: concentrationRatio,
		UnrealizedPnL:      totalUnrealizedPnL,
		PositionCount:      len(positions),
		LargestPosition:    maxPositionExposure,
	}
}

// generateRiskAlerts generates risk alerts based on metrics
func (rm *RiskManager) generateRiskAlerts(riskMetrics RiskMetrics) []RiskAlert {
	var alerts []RiskAlert

	if riskMetrics.LeverageRatio > 5 {
		alerts = append(alerts, RiskAlert{
			Type:           "HIGH_LEVERAGE",
			Severity:       "HIGH",
			Message:        fmt.Sprintf("Leverage ratio %.1fx is very high", riskMetrics.LeverageRatio),
			Recommendation: "Consider reducing position sizes",
		})
	}

	if riskMetrics.ConcentrationRatio > rm.riskLimits.ConcentrationLimit {
		alerts = append(alerts, RiskAlert{
			Type:           "HIGH_CONCENTRATION",
			Severity:       "MEDIUM",
			Message:        fmt.Sprintf("Position concentration %.1f%% exceeds limit", riskMetrics.ConcentrationRatio*100),
			Recommendation: "Diversify positions across multiple contracts",
		})
	}

	if riskMetrics.UnrealizedPnL < -riskMetrics.TotalExposure*0.1 {
		alerts = append(alerts, RiskAlert{
			Type:           "LARGE_UNREALIZED_LOSS",
			Severity:       "HIGH",
			Message:        "Unrealized losses exceed 10% of exposure",
			Recommendation: "Review positions and consider stop-loss orders",
		})
	}

	return alerts
}

// calculateRiskScore calculates overall risk score (0-100, higher is riskier)
func (rm *RiskManager) calculateRiskScore(marginStatus MarginStatus, varMetrics VaRMetrics, postTradeRisk map[string]interface{}) float64 {
	score := 0.0

	// Margin utilization component (0-40 points)
	score += math.Min(40, marginStatus.MarginUtilization*50)

	// VaR component (0-30 points)
	var varRatio float64
	if varMetrics.TotalExposure > 0 {
		varRatio = varMetrics.VaR / varMetrics.TotalExposure
	}
	score += math.Min(30, varRatio*1000)

	// Risk metrics component (0-30 points)
	if riskMetrics, ok := postTradeRisk["risk_metrics"].(RiskMetrics); ok {
		score += math.Min(15, riskMetrics.LeverageRatio*3)
		score += math.Min(15, riskMetrics.ConcentrationRatio*50)
	}

	return math.Min(100, score)
}

// generateRiskRecommendations generates risk management recommendations
func (rm *RiskManager) generateRiskRecommendations(riskScore float64, marginStatus MarginStatus, varMetrics VaRMetrics) []string {
	var recommendations []string

	if riskScore > 70 {
		recommendations = append(recommendations, "HIGH RISK: Immediate action required to reduce risk exposure")
	} else if riskScore > 50 {
		recommendations = append(recommendations, "MEDIUM RISK: Monitor positions closely and consider risk reduction")
	}

	if marginStatus.MarginUtilization > 0.8 {
		recommendations = append(recommendations, "Consider adding funds or reducing positions to improve margin situation")
	}

	if varMetrics.VaR > 10000 {
		recommendations = append(recommendations, "High VaR detected - consider portfolio hedging strategies")
	}

	return recommendations
}