// Package marketdata provides market data functionality for gold prices and charts
package marketdata

import (
	"encoding/json"
	"fmt"
	"math"
	"math/rand"
	"net/http"
	"sync"
	"time"

	"github.com/smaruf/python-ai-course/nasdaq-cse-go/internal/core"
)

// GoldPriceProvider provides real-time gold price data
type GoldPriceProvider struct {
	basePrice    float64
	currentPrice float64
	priceHistory []core.MarketDataResponse
	lastUpdate   time.Time
	mutex        sync.RWMutex
}

// NewGoldPriceProvider creates a new gold price provider
func NewGoldPriceProvider() *GoldPriceProvider {
	return &GoldPriceProvider{
		basePrice:    2050.0,
		currentPrice: 2050.0,
		priceHistory: make([]core.MarketDataResponse, 0),
		lastUpdate:   time.Now(),
	}
}

// ExternalGoldPrice represents response from external gold price API
type ExternalGoldPrice struct {
	Price float64 `json:"price"`
}

// FetchRealGoldPrice attempts to fetch real gold price from external API
func (gpp *GoldPriceProvider) FetchRealGoldPrice() (float64, error) {
	// Try to fetch from a free gold price API
	client := &http.Client{Timeout: 5 * time.Second}
	resp, err := client.Get("https://api.metals.live/v1/spot/gold")
	if err != nil {
		return 0, fmt.Errorf("failed to fetch gold price: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return 0, fmt.Errorf("API returned status code: %d", resp.StatusCode)
	}

	var goldPrice ExternalGoldPrice
	if err := json.NewDecoder(resp.Body).Decode(&goldPrice); err != nil {
		return 0, fmt.Errorf("failed to decode API response: %w", err)
	}

	return goldPrice.Price, nil
}

// SimulatePriceMovement simulates realistic gold price movements
func (gpp *GoldPriceProvider) SimulatePriceMovement() float64 {
	gpp.mutex.Lock()
	defer gpp.mutex.Unlock()

	now := time.Now()
	timeDiff := now.Sub(gpp.lastUpdate).Seconds()

	// Random walk with mean reversion
	volatility := 0.02 // 2% volatility
	meanReversion := 0.001
	drift := -meanReversion * (gpp.currentPrice - gpp.basePrice) / gpp.basePrice

	// Random component
	randomComponent := rand.NormFloat64() * volatility * math.Sqrt(timeDiff/3600)

	// Calculate price change
	priceChange := drift + randomComponent
	gpp.currentPrice *= (1 + priceChange)

	// Add some noise for intraday movements
	gpp.currentPrice += rand.NormFloat64() * 0.5

	// Keep price within reasonable bounds
	if gpp.currentPrice < 1800 {
		gpp.currentPrice = 1800
	}
	if gpp.currentPrice > 2500 {
		gpp.currentPrice = 2500
	}

	gpp.lastUpdate = now
	return gpp.currentPrice
}

// GetCurrentPrice returns current gold price with bid/ask spread
func (gpp *GoldPriceProvider) GetCurrentPrice() core.MarketDataResponse {
	// Try to fetch real price, fallback to simulation
	price, err := gpp.FetchRealGoldPrice()
	if err != nil {
		price = gpp.SimulatePriceMovement()
	} else {
		gpp.mutex.Lock()
		gpp.currentPrice = price
		gpp.mutex.Unlock()
	}

	// Calculate bid-ask spread
	spread := rand.Float64()*1.0 + 0.5 // 0.5 to 1.5 spread

	priceData := core.MarketDataResponse{
		Timestamp:     time.Now(),
		Price:         math.Round(price*100) / 100,
		Bid:           math.Round((price-spread/2)*100) / 100,
		Ask:           math.Round((price+spread/2)*100) / 100,
		Volume:        int64(rand.Intn(900) + 100), // 100-1000 volume
		Change24h:     math.Round((rand.Float64()*4.0-2.0)*100) / 100, // -2.0 to +2.0
		ChangePercent: math.Round((rand.Float64()*0.2-0.1)*10000) / 10000, // -0.1 to +0.1
	}

	// Store in history
	gpp.mutex.Lock()
	gpp.priceHistory = append(gpp.priceHistory, priceData)
	
	// Keep only last 1000 price points
	if len(gpp.priceHistory) > 1000 {
		gpp.priceHistory = gpp.priceHistory[len(gpp.priceHistory)-1000:]
	}
	gpp.mutex.Unlock()

	return priceData
}

// GetPriceHistory returns historical price data for specified duration
func (gpp *GoldPriceProvider) GetPriceHistory(hours int) []core.MarketDataResponse {
	gpp.mutex.RLock()
	defer gpp.mutex.RUnlock()

	cutoffTime := time.Now().Add(-time.Duration(hours) * time.Hour)
	var result []core.MarketDataResponse

	for _, price := range gpp.priceHistory {
		if price.Timestamp.After(cutoffTime) {
			result = append(result, price)
		}
	}

	return result
}

// ChartGenerator generates chart data for market visualization
type ChartGenerator struct {
	priceProvider *GoldPriceProvider
}

// NewChartGenerator creates a new chart generator
func NewChartGenerator(provider *GoldPriceProvider) *ChartGenerator {
	return &ChartGenerator{priceProvider: provider}
}

// CreatePriceChartData creates price chart data
func (cg *ChartGenerator) CreatePriceChartData(hours int) core.ChartDataResponse {
	priceHistory := cg.priceProvider.GetPriceHistory(hours)
	
	if len(priceHistory) == 0 {
		return core.ChartDataResponse{
			Data: []core.ChartDataPoint{},
			Type: "price",
		}
	}

	// Convert to chart data points
	var chartData []core.ChartDataPoint
	for _, price := range priceHistory {
		chartData = append(chartData, core.ChartDataPoint{
			Timestamp: price.Timestamp,
			Price:     price.Price,
			Volume:    price.Volume,
		})
	}

	return core.ChartDataResponse{
		Data: chartData,
		Type: "price",
	}
}

// CreatePnLChartData creates P&L chart data for positions
func (cg *ChartGenerator) CreatePnLChartData(positionsData []map[string]interface{}) core.ChartDataResponse {
	if len(positionsData) == 0 {
		return core.ChartDataResponse{
			Data: []core.ChartDataPoint{},
			Type: "pnl",
		}
	}

	var chartData []core.ChartDataPoint
	for _, pos := range positionsData {
		timestamp, _ := time.Parse(time.RFC3339, pos["timestamp"].(string))
		unrealizedPnL, _ := pos["unrealized_pnl"].(float64)
		
		chartData = append(chartData, core.ChartDataPoint{
			Timestamp: timestamp,
			Price:     unrealizedPnL,
			Volume:    0, // Not applicable for P&L
		})
	}

	return core.ChartDataResponse{
		Data: chartData,
		Type: "pnl",
	}
}

// CreateExposureChartData creates exposure analysis chart data
func (cg *ChartGenerator) CreateExposureChartData(exposureData map[string]float64) map[string]interface{} {
	contracts := make([]string, 0)
	exposures := make([]float64, 0)

	for contract, exposure := range exposureData {
		contracts = append(contracts, contract)
		exposures = append(exposures, exposure)
	}

	return map[string]interface{}{
		"contracts": contracts,
		"exposures": exposures,
		"type":      "exposure",
	}
}

// MarketDataService provides market data functionality
type MarketDataService struct {
	priceProvider  *GoldPriceProvider
	chartGenerator *ChartGenerator
}

// NewMarketDataService creates a new market data service
func NewMarketDataService() *MarketDataService {
	provider := NewGoldPriceProvider()
	generator := NewChartGenerator(provider)

	return &MarketDataService{
		priceProvider:  provider,
		chartGenerator: generator,
	}
}

// GetCurrentPrice returns current market price
func (mds *MarketDataService) GetCurrentPrice() core.MarketDataResponse {
	return mds.priceProvider.GetCurrentPrice()
}

// GetPriceHistory returns price history
func (mds *MarketDataService) GetPriceHistory(hours int) []core.MarketDataResponse {
	return mds.priceProvider.GetPriceHistory(hours)
}

// GetPriceChartData returns chart data for prices
func (mds *MarketDataService) GetPriceChartData(hours int) core.ChartDataResponse {
	return mds.chartGenerator.CreatePriceChartData(hours)
}

// GetPnLChartData returns chart data for P&L
func (mds *MarketDataService) GetPnLChartData(positionsData []map[string]interface{}) core.ChartDataResponse {
	return mds.chartGenerator.CreatePnLChartData(positionsData)
}

// GetExposureChartData returns chart data for exposure analysis
func (mds *MarketDataService) GetExposureChartData(exposureData map[string]float64) map[string]interface{} {
	return mds.chartGenerator.CreateExposureChartData(exposureData)
}