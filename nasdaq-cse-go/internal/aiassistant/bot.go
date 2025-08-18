// Package aiassistant provides AI-powered trading assistance and analysis
package aiassistant

import (
	"fmt"
	"math"
	"math/rand"
	"strings"
	"time"

	"github.com/smaruf/python-ai-course/nasdaq-cse-go/internal/core"
)

// TechnicalIndicators holds calculated technical indicators
type TechnicalIndicators struct {
	RSI               float64 `json:"rsi"`
	Volatility        float64 `json:"volatility"`
	MovingAverageRatio float64 `json:"moving_avg_ratio"`
}

// TradeAnalysis represents AI analysis for trade opportunities
type TradeAnalysis struct {
	Timestamp          string              `json:"timestamp"`
	AnalysisType       string              `json:"analysis_type"`
	CurrentPrice       float64             `json:"current_price"`
	PredictedDirection string              `json:"predicted_direction"`
	ConfidenceScore    float64             `json:"confidence_score"`
	TechnicalIndicators TechnicalIndicators `json:"technical_indicators"`
	Suggestion         string              `json:"suggestion"`
	RiskLevel          string              `json:"risk_level"`
}

// RiskAnalysis represents risk assessment analysis
type RiskAnalysis struct {
	Timestamp          string    `json:"timestamp"`
	AnalysisType       string    `json:"analysis_type"`
	RiskLevel          string    `json:"risk_level"`
	ExposureRatio      float64   `json:"exposure_ratio"`
	ConcentrationRatio float64   `json:"concentration_ratio"`
	TotalUnrealizedPnL float64   `json:"total_unrealized_pnl"`
	TotalRealizedPnL   float64   `json:"total_realized_pnl"`
	RiskWarnings       []string  `json:"risk_warnings"`
	Recommendations    []string  `json:"recommendations"`
	ConfidenceScore    float64   `json:"confidence_score"`
}

// HedgingStrategy represents hedging suggestions
type HedgingStrategy struct {
	Timestamp           string                   `json:"timestamp"`
	AnalysisType        string                   `json:"analysis_type"`
	NetExposure         float64                  `json:"net_exposure"`
	CurrentVolatility   float64                  `json:"current_volatility"`
	HedgingSuggestions  []HedgingSuggestion      `json:"hedging_suggestions"`
	ConfidenceScore     float64                  `json:"confidence_score"`
}

// HedgingSuggestion represents a single hedging suggestion
type HedgingSuggestion struct {
	Action   string  `json:"action"`
	Quantity float64 `json:"quantity"`
	Reason   string  `json:"reason"`
	Contract string  `json:"contract"`
}

// TradingBot provides AI-powered trading assistance
type TradingBot struct {
	analysisHistory []interface{}
	riskThresholds  map[string]float64
}

// NewTradingBot creates a new trading bot instance
func NewTradingBot() *TradingBot {
	return &TradingBot{
		analysisHistory: make([]interface{}, 0),
		riskThresholds: map[string]float64{
			"high_exposure":       0.7,   // 70% of account
			"high_concentration":  0.5,   // 50% in single position
			"volatility_threshold": 0.05, // 5% daily volatility
			"margin_warning":      0.8,   // 80% margin utilization
		},
	}
}

// AnalyzeTradeOpportunity analyzes current market conditions and suggests trading opportunities
func (tb *TradingBot) AnalyzeTradeOpportunity(marketData core.MarketDataResponse, userPositions []map[string]interface{}) TradeAnalysis {
	currentPrice := marketData.Price
	volume := float64(marketData.Volume)

	// Calculate technical indicators
	rsi := tb.calculateRSI(marketData)
	volatility := tb.calculateVolatility(marketData)
	movingAvgRatio := tb.calculateMovingAverageRatio(marketData)

	// Simple ML prediction simulation (replacing scikit-learn)
	priceMovementPrediction := tb.predictPriceMovement(marketData, rsi, volatility, volume)

	// Generate trading suggestion
	suggestion := tb.generateTradingSuggestion(currentPrice, priceMovementPrediction, rsi, volatility, userPositions)

	// Determine predicted direction and confidence
	predictedDirection := "NEUTRAL"
	confidenceScore := 50.0

	if priceMovementPrediction > 0.01 {
		predictedDirection = "BULLISH"
		confidenceScore = math.Min(math.Abs(priceMovementPrediction)*1000, 95)
	} else if priceMovementPrediction < -0.01 {
		predictedDirection = "BEARISH"
		confidenceScore = math.Min(math.Abs(priceMovementPrediction)*1000, 95)
	}

	analysis := TradeAnalysis{
		Timestamp:          time.Now().Format(time.RFC3339),
		AnalysisType:       "trade_suggestion",
		CurrentPrice:       currentPrice,
		PredictedDirection: predictedDirection,
		ConfidenceScore:    confidenceScore,
		TechnicalIndicators: TechnicalIndicators{
			RSI:                rsi,
			Volatility:         volatility,
			MovingAverageRatio: movingAvgRatio,
		},
		Suggestion: suggestion,
		RiskLevel:  tb.assessRiskLevel(userPositions, marketData),
	}

	tb.analysisHistory = append(tb.analysisHistory, analysis)
	return analysis
}

// AnalyzeRisk analyzes risk exposure and provides warnings/suggestions
func (tb *TradingBot) AnalyzeRisk(userPositions []map[string]interface{}, accountBalance float64) RiskAnalysis {
	totalExposure := 0.0
	totalUnrealizedPnL := 0.0
	totalRealizedPnL := 0.0

	for _, pos := range userPositions {
		if qty, ok := pos["quantity"].(float64); ok {
			if avgPrice, ok := pos["avg_entry_price"].(float64); ok {
				totalExposure += math.Abs(qty * avgPrice)
			}
		}
		if unrealizedPnL, ok := pos["unrealized_pnl"].(float64); ok {
			totalUnrealizedPnL += unrealizedPnL
		}
		if realizedPnL, ok := pos["realized_pnl"].(float64); ok {
			totalRealizedPnL += realizedPnL
		}
	}

	var exposureRatio float64
	if accountBalance > 0 {
		exposureRatio = totalExposure / accountBalance
	}

	// Calculate position concentration
	concentrationRatio := 0.0
	if len(userPositions) > 0 && totalExposure > 0 {
		maxPosition := 0.0
		for _, pos := range userPositions {
			if qty, ok := pos["quantity"].(float64); ok {
				if avgPrice, ok := pos["avg_entry_price"].(float64); ok {
					exposure := math.Abs(qty * avgPrice)
					if exposure > maxPosition {
						maxPosition = exposure
					}
				}
			}
		}
		concentrationRatio = maxPosition / totalExposure
	}

	var riskWarnings []string
	var recommendations []string

	// Check various risk conditions
	if exposureRatio > tb.riskThresholds["high_exposure"] {
		riskWarnings = append(riskWarnings, fmt.Sprintf("High exposure: %.1f%% of account balance", exposureRatio*100))
		recommendations = append(recommendations, "Consider reducing position sizes or adding hedges")
	}

	if concentrationRatio > tb.riskThresholds["high_concentration"] {
		riskWarnings = append(riskWarnings, fmt.Sprintf("High concentration: %.1f%% in single position", concentrationRatio*100))
		recommendations = append(recommendations, "Diversify positions across multiple contracts")
	}

	if totalUnrealizedPnL < -accountBalance*0.1 {
		riskWarnings = append(riskWarnings, "Unrealized losses exceed 10% of account balance")
		recommendations = append(recommendations, "Consider stop-loss orders or position reduction")
	}

	riskLevel := "LOW"
	if len(riskWarnings) >= 3 {
		riskLevel = "HIGH"
	} else if len(riskWarnings) >= 1 {
		riskLevel = "MEDIUM"
	}

	analysis := RiskAnalysis{
		Timestamp:          time.Now().Format(time.RFC3339),
		AnalysisType:       "risk_analysis",
		RiskLevel:          riskLevel,
		ExposureRatio:      exposureRatio,
		ConcentrationRatio: concentrationRatio,
		TotalUnrealizedPnL: totalUnrealizedPnL,
		TotalRealizedPnL:   totalRealizedPnL,
		RiskWarnings:       riskWarnings,
		Recommendations:    recommendations,
		ConfidenceScore:    85.0,
	}

	tb.analysisHistory = append(tb.analysisHistory, analysis)
	return analysis
}

// SuggestHedgingStrategy suggests hedging strategies based on current positions
func (tb *TradingBot) SuggestHedgingStrategy(userPositions []map[string]interface{}, marketData core.MarketDataResponse) HedgingStrategy {
	if len(userPositions) == 0 {
		return HedgingStrategy{
			Timestamp:       time.Now().Format(time.RFC3339),
			AnalysisType:    "hedging_strategy",
			ConfidenceScore: 0.0,
		}
	}

	// Calculate net exposure
	netLongExposure := 0.0
	netShortExposure := 0.0

	for _, pos := range userPositions {
		if qty, ok := pos["quantity"].(float64); ok {
			if qty > 0 {
				netLongExposure += qty
			} else {
				netShortExposure += math.Abs(qty)
			}
		}
	}

	netExposure := netLongExposure - netShortExposure
	volatility := tb.calculateVolatility(marketData)

	var hedgingSuggestions []HedgingSuggestion

	if math.Abs(netExposure) > 0 {
		hedgeRatio := math.Min(math.Abs(netExposure)*0.5, math.Abs(netExposure)) // 50% hedge

		if netExposure > 0 { // Net long, suggest short hedge
			hedgingSuggestions = append(hedgingSuggestions, HedgingSuggestion{
				Action:   "SELL",
				Quantity: hedgeRatio,
				Reason:   "Hedge against long exposure",
				Contract: "GOLD2024DEC",
			})
		} else { // Net short, suggest long hedge
			hedgingSuggestions = append(hedgingSuggestions, HedgingSuggestion{
				Action:   "BUY",
				Quantity: hedgeRatio,
				Reason:   "Hedge against short exposure",
				Contract: "GOLD2024DEC",
			})
		}
	}

	if volatility > tb.riskThresholds["volatility_threshold"] {
		hedgingSuggestions = append(hedgingSuggestions, HedgingSuggestion{
			Action:   "REDUCE_POSITION",
			Quantity: math.Abs(netExposure) * 0.3,
			Reason:   "High volatility detected, reduce exposure",
			Contract: "ALL",
		})
	}

	analysis := HedgingStrategy{
		Timestamp:          time.Now().Format(time.RFC3339),
		AnalysisType:       "hedging_strategy",
		NetExposure:        netExposure,
		CurrentVolatility:  volatility,
		HedgingSuggestions: hedgingSuggestions,
		ConfidenceScore:    80.0,
	}

	tb.analysisHistory = append(tb.analysisHistory, analysis)
	return analysis
}

// ChatResponse generates a chat response based on user message and trading context
func (tb *TradingBot) ChatResponse(userMessage string, context map[string]interface{}) string {
	userMessageLower := strings.ToLower(userMessage)

	// Simple keyword-based responses
	if strings.Contains(userMessageLower, "price") || strings.Contains(userMessageLower, "gold") || strings.Contains(userMessageLower, "current") {
		if marketData, ok := context["market_data"].(core.MarketDataResponse); ok {
			sentiment := "bearish"
			if marketData.ChangePercent > 0 {
				sentiment = "bullish"
			}
			return fmt.Sprintf("The current gold price is $%.2f per ounce. The market is showing %s sentiment today.", marketData.Price, sentiment)
		}
		return "Current market data is not available at the moment."
	}

	if strings.Contains(userMessageLower, "risk") || strings.Contains(userMessageLower, "exposure") || strings.Contains(userMessageLower, "danger") {
		if positions, ok := context["positions"].([]map[string]interface{}); ok && len(positions) > 0 {
			accountBalance := 100000.0 // Default
			if balance, ok := context["account_balance"].(float64); ok {
				accountBalance = balance
			}
			riskAnalysis := tb.AnalyzeRisk(positions, accountBalance)
			recommendation := "Risk levels are acceptable."
			if len(riskAnalysis.Recommendations) > 0 {
				recommendation = riskAnalysis.Recommendations[0]
			}
			return fmt.Sprintf("Your current risk level is %s. Exposure ratio: %.1f%%. %s", riskAnalysis.RiskLevel, riskAnalysis.ExposureRatio*100, recommendation)
		}
		return "You currently have no open positions, so your risk exposure is minimal."
	}

	if strings.Contains(userMessageLower, "buy") || strings.Contains(userMessageLower, "sell") || strings.Contains(userMessageLower, "trade") || strings.Contains(userMessageLower, "suggest") {
		if marketData, ok := context["market_data"].(core.MarketDataResponse); ok {
			positions := []map[string]interface{}{}
			if pos, ok := context["positions"].([]map[string]interface{}); ok {
				positions = pos
			}
			analysis := tb.AnalyzeTradeOpportunity(marketData, positions)
			return fmt.Sprintf("Based on current analysis, I suggest a %s outlook with %.0f%% confidence. %s", analysis.PredictedDirection, analysis.ConfidenceScore, analysis.Suggestion)
		}
		return "Unable to analyze current market conditions for trading suggestions."
	}

	if strings.Contains(userMessageLower, "hedge") || strings.Contains(userMessageLower, "protect") || strings.Contains(userMessageLower, "cover") {
		if positions, ok := context["positions"].([]map[string]interface{}); ok {
			if marketData, ok := context["market_data"].(core.MarketDataResponse); ok {
				hedging := tb.SuggestHedgingStrategy(positions, marketData)
				if len(hedging.HedgingSuggestions) > 0 {
					suggestion := hedging.HedgingSuggestions[0]
					return fmt.Sprintf("For hedging, consider %s %.0f units. Reason: %s", suggestion.Action, suggestion.Quantity, suggestion.Reason)
				}
			}
		}
		return "No hedging required at this time based on your current positions."
	}

	if strings.Contains(userMessageLower, "help") || strings.Contains(userMessageLower, "guide") || strings.Contains(userMessageLower, "how") {
		return "I can help you with: 1) Current gold prices and market analysis, 2) Risk assessment of your positions, 3) Trading suggestions based on technical indicators, 4) Hedging strategies to protect your portfolio. Just ask me about any of these topics!"
	}

	return "I'm here to help with your gold derivatives trading. Ask me about current prices, risk analysis, trading suggestions, or hedging strategies. What would you like to know?"
}

// calculateRSI calculates RSI indicator (simplified version)
func (tb *TradingBot) calculateRSI(marketData core.MarketDataResponse) float64 {
	// Simplified RSI calculation for demonstration
	changePercent := marketData.ChangePercent
	// Convert to 0-100 scale with some randomness for demonstration
	rsi := 50 + (changePercent*1000) + (rand.Float64()*20 - 10)
	return math.Max(0, math.Min(100, rsi))
}

// calculateVolatility calculates price volatility
func (tb *TradingBot) calculateVolatility(marketData core.MarketDataResponse) float64 {
	// Simplified volatility calculation
	return math.Abs(marketData.ChangePercent) + rand.Float64()*0.02 + 0.01
}

// calculateMovingAverageRatio calculates ratio of current price to moving average
func (tb *TradingBot) calculateMovingAverageRatio(marketData core.MarketDataResponse) float64 {
	currentPrice := marketData.Price
	// Simulated moving average
	maPrice := currentPrice * (rand.Float64()*0.04 + 0.98) // ±2% from current price
	return currentPrice / maPrice
}

// predictPriceMovement predicts price movement using simplified ML logic
func (tb *TradingBot) predictPriceMovement(marketData core.MarketDataResponse, rsi, volatility, volume float64) float64 {
	// Simplified prediction logic (replacing scikit-learn)
	
	// Features: change_percent, volume_normalized, volatility, rsi_normalized, price_trend
	features := []float64{
		marketData.ChangePercent,
		volume / 1000.0, // Normalize volume
		volatility,
		(rsi - 50) / 50, // Normalize RSI to -1 to 1
		math.Tanh(marketData.ChangePercent * 10), // Price trend indicator
	}

	// Simple weighted prediction (replacing RandomForest)
	weights := []float64{0.3, 0.1, 0.2, 0.3, 0.1}
	prediction := 0.0
	
	for i, feature := range features {
		prediction += feature * weights[i]
	}

	// Add some noise and bounds
	prediction += (rand.Float64() - 0.5) * 0.02
	return math.Max(-0.1, math.Min(0.1, prediction))
}

// generateTradingSuggestion generates human-readable trading suggestion
func (tb *TradingBot) generateTradingSuggestion(currentPrice, prediction, rsi, volatility float64, positions []map[string]interface{}) string {
	var suggestions []string

	if prediction > 0.01 {
		suggestions = append(suggestions, "Consider LONG position - bullish signals detected")
	} else if prediction < -0.01 {
		suggestions = append(suggestions, "Consider SHORT position - bearish signals detected")
	} else {
		suggestions = append(suggestions, "HOLD - market showing neutral signals")
	}

	if rsi > 70 {
		suggestions = append(suggestions, "RSI indicates overbought conditions")
	} else if rsi < 30 {
		suggestions = append(suggestions, "RSI indicates oversold conditions")
	}

	if volatility > 0.05 {
		suggestions = append(suggestions, "High volatility - consider smaller position sizes")
	}

	if len(positions) > 3 {
		suggestions = append(suggestions, "Consider position consolidation")
	}

	return strings.Join(suggestions, "; ")
}

// assessRiskLevel assesses overall risk level
func (tb *TradingBot) assessRiskLevel(positions []map[string]interface{}, marketData core.MarketDataResponse) string {
	riskFactors := 0

	if len(positions) > 5 {
		riskFactors++
	}

	if math.Abs(marketData.ChangePercent) > 0.05 {
		riskFactors++
	}

	totalExposure := 0.0
	for _, pos := range positions {
		if qty, ok := pos["quantity"].(float64); ok {
			totalExposure += math.Abs(qty)
		}
	}
	if totalExposure > 1000 {
		riskFactors++
	}

	switch {
	case riskFactors >= 2:
		return "HIGH"
	case riskFactors == 1:
		return "MEDIUM"
	default:
		return "LOW"
	}
}