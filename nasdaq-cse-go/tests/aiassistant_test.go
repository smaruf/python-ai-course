// Package tests provides unit tests for the AI Assistant
package tests

import (
	"strings"
	"testing"

	"github.com/smaruf/python-ai-course/nasdaq-cse-go/internal/aiassistant"
	"github.com/smaruf/python-ai-course/nasdaq-cse-go/internal/core"
)

func TestTradingBot_AnalyzeTradeOpportunity(t *testing.T) {
	bot := aiassistant.NewTradingBot()

	marketData := core.MarketDataResponse{
		Price:         2050.0,
		Bid:           2049.5,
		Ask:           2050.5,
		Volume:        500,
		ChangePercent: 0.02, // 2% positive change
	}

	userPositions := []map[string]interface{}{
		{
			"quantity":         5.0,
			"avg_entry_price":  2040.0,
			"unrealized_pnl":   50.0,
		},
	}

	analysis := bot.AnalyzeTradeOpportunity(marketData, userPositions)

	// Test analysis structure
	if analysis.AnalysisType != "trade_suggestion" {
		t.Errorf("Expected analysis_type 'trade_suggestion' but got '%s'", analysis.AnalysisType)
	}

	if analysis.CurrentPrice != marketData.Price {
		t.Errorf("Expected current_price %f but got %f", marketData.Price, analysis.CurrentPrice)
	}

	if analysis.ConfidenceScore < 0 || analysis.ConfidenceScore > 100 {
		t.Errorf("Expected confidence_score between 0-100 but got %f", analysis.ConfidenceScore)
	}

	// Test predicted direction is valid
	validDirections := []string{"BULLISH", "BEARISH", "NEUTRAL"}
	found := false
	for _, dir := range validDirections {
		if analysis.PredictedDirection == dir {
			found = true
			break
		}
	}
	if !found {
		t.Errorf("Invalid predicted direction: %s", analysis.PredictedDirection)
	}

	// Test technical indicators
	indicators := analysis.TechnicalIndicators
	if indicators.RSI < 0 || indicators.RSI > 100 {
		t.Errorf("RSI should be between 0-100 but got %f", indicators.RSI)
	}

	if indicators.Volatility < 0 {
		t.Errorf("Volatility should be non-negative but got %f", indicators.Volatility)
	}

	if indicators.MovingAverageRatio <= 0 {
		t.Errorf("Moving average ratio should be positive but got %f", indicators.MovingAverageRatio)
	}
}

func TestTradingBot_AnalyzeRisk(t *testing.T) {
	bot := aiassistant.NewTradingBot()

	userPositions := []map[string]interface{}{
		{
			"quantity":         10.0,
			"avg_entry_price":  2000.0,
			"unrealized_pnl":   -500.0,
			"realized_pnl":     100.0,
		},
		{
			"quantity":         -5.0,
			"avg_entry_price":  2100.0,
			"unrealized_pnl":   250.0,
			"realized_pnl":     50.0,
		},
	}

	accountBalance := 50000.0

	analysis := bot.AnalyzeRisk(userPositions, accountBalance)

	// Test analysis structure
	if analysis.AnalysisType != "risk_analysis" {
		t.Errorf("Expected analysis_type 'risk_analysis' but got '%s'", analysis.AnalysisType)
	}

	// Test risk level is valid
	validRiskLevels := []string{"LOW", "MEDIUM", "HIGH"}
	found := false
	for _, level := range validRiskLevels {
		if analysis.RiskLevel == level {
			found = true
			break
		}
	}
	if !found {
		t.Errorf("Invalid risk level: %s", analysis.RiskLevel)
	}

	// Test exposure ratio calculation
	if analysis.ExposureRatio < 0 {
		t.Errorf("Exposure ratio should be non-negative but got %f", analysis.ExposureRatio)
	}

	// Test concentration ratio
	if analysis.ConcentrationRatio < 0 || analysis.ConcentrationRatio > 1 {
		t.Errorf("Concentration ratio should be between 0-1 but got %f", analysis.ConcentrationRatio)
	}

	// Test P&L calculations
	expectedUnrealizedPnL := -500.0 + 250.0
	if analysis.TotalUnrealizedPnL != expectedUnrealizedPnL {
		t.Errorf("Expected total unrealized P&L %f but got %f", expectedUnrealizedPnL, analysis.TotalUnrealizedPnL)
	}

	expectedRealizedPnL := 100.0 + 50.0
	if analysis.TotalRealizedPnL != expectedRealizedPnL {
		t.Errorf("Expected total realized P&L %f but got %f", expectedRealizedPnL, analysis.TotalRealizedPnL)
	}
}

func TestTradingBot_SuggestHedgingStrategy(t *testing.T) {
	bot := aiassistant.NewTradingBot()

	marketData := core.MarketDataResponse{
		Price:         2050.0,
		ChangePercent: 0.03, // High volatility scenario
	}

	// Net long position
	userPositions := []map[string]interface{}{
		{
			"quantity": 10.0,
		},
		{
			"quantity": -3.0,
		},
	}

	strategy := bot.SuggestHedgingStrategy(userPositions, marketData)

	// Test strategy structure
	if strategy.AnalysisType != "hedging_strategy" {
		t.Errorf("Expected analysis_type 'hedging_strategy' but got '%s'", strategy.AnalysisType)
	}

	// Should suggest hedging for net long position
	expectedNetExposure := 10.0 - 3.0
	if strategy.NetExposure != expectedNetExposure {
		t.Errorf("Expected net exposure %f but got %f", expectedNetExposure, strategy.NetExposure)
	}

	// Should have hedging suggestions for non-zero net exposure
	if len(strategy.HedgingSuggestions) == 0 {
		t.Errorf("Expected hedging suggestions but got none")
	}

	// For net long position, should suggest SELL action
	foundSellSuggestion := false
	for _, suggestion := range strategy.HedgingSuggestions {
		if suggestion.Action == "SELL" {
			foundSellSuggestion = true
			if suggestion.Quantity <= 0 {
				t.Errorf("Expected positive hedge quantity but got %f", suggestion.Quantity)
			}
		}
	}
	if !foundSellSuggestion {
		t.Errorf("Expected SELL suggestion for net long position")
	}
}

func TestTradingBot_ChatResponse(t *testing.T) {
	bot := aiassistant.NewTradingBot()

	marketData := core.MarketDataResponse{
		Price:         2050.0,
		ChangePercent: 0.01,
	}

	context := map[string]interface{}{
		"market_data": marketData,
		"positions": []map[string]interface{}{
			{
				"quantity":        5.0,
				"avg_entry_price": 2040.0,
			},
		},
		"account_balance": 100000.0,
	}

	tests := []struct {
		message     string
		expectWords []string
	}{
		{
			message:     "What's the current gold price?",
			expectWords: []string{"gold", "price", "$2050.00"},
		},
		{
			message:     "How is my risk exposure?",
			expectWords: []string{"risk", "level"},
		},
		{
			message:     "Should I buy or sell?",
			expectWords: []string{"suggest", "analysis"},
		},
		{
			message:     "How can I hedge my positions?",
			expectWords: []string{"hedging", "consider"},
		},
		{
			message:     "Help me understand trading",
			expectWords: []string{"help", "trading"},
		},
		{
			message:     "Random question about weather",
			expectWords: []string{"trading", "help"},
		},
	}

	for _, tt := range tests {
		t.Run(tt.message, func(t *testing.T) {
			response := bot.ChatResponse(tt.message, context)

			if response == "" {
				t.Errorf("Expected non-empty response")
			}

			// Check for expected words in response (case insensitive)
			responseLower := strings.ToLower(response)
			for _, word := range tt.expectWords {
				if !strings.Contains(responseLower, strings.ToLower(word)) {
					t.Errorf("Expected response to contain '%s' but got: %s", word, response)
				}
			}
		})
	}
}

func TestTradingBot_TechnicalIndicators(t *testing.T) {
	bot := aiassistant.NewTradingBot()

	marketData := core.MarketDataResponse{
		Price:         2050.0,
		ChangePercent: 0.02,
		Volume:        500,
	}

	// Test RSI calculation (simplified)
	for i := 0; i < 10; i++ {
		analysis := bot.AnalyzeTradeOpportunity(marketData, []map[string]interface{}{})
		rsi := analysis.TechnicalIndicators.RSI

		if rsi < 0 || rsi > 100 {
			t.Errorf("RSI should be between 0-100 but got %f", rsi)
		}
	}

	// Test volatility calculation
	analysis := bot.AnalyzeTradeOpportunity(marketData, []map[string]interface{}{})
	volatility := analysis.TechnicalIndicators.Volatility

	if volatility < 0 {
		t.Errorf("Volatility should be non-negative but got %f", volatility)
	}

	// Volatility should be related to price change
	if volatility < 0.01 { // Should be at least as much as the change percent
		t.Errorf("Volatility seems too low for the given price change: %f", volatility)
	}
}