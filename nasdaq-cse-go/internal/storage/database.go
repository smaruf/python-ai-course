// Package storage handles database operations and JSON persistence
package storage

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"time"

	"github.com/smaruf/python-ai-course/nasdaq-cse-go/internal/core"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

// DatabaseManager manages database connections and operations
type DatabaseManager struct {
	db *gorm.DB
}

// NewDatabaseManager creates a new database manager
func NewDatabaseManager(databasePath string) (*DatabaseManager, error) {
	db, err := gorm.Open(sqlite.Open(databasePath), &gorm.Config{
		Logger: logger.Default.LogMode(logger.Info),
	})
	if err != nil {
		return nil, fmt.Errorf("failed to connect to database: %w", err)
	}

	// Auto-migrate the schema
	err = db.AutoMigrate(
		&core.User{},
		&core.Contract{},
		&core.Order{},
		&core.Trade{},
		&core.Position{},
		&core.MarketData{},
		&core.AIAnalysis{},
	)
	if err != nil {
		return nil, fmt.Errorf("failed to migrate database: %w", err)
	}

	dm := &DatabaseManager{db: db}
	
	// Initialize sample data
	if err := dm.initSampleData(); err != nil {
		return nil, fmt.Errorf("failed to initialize sample data: %w", err)
	}

	return dm, nil
}

// GetDB returns the database instance
func (dm *DatabaseManager) GetDB() *gorm.DB {
	return dm.db
}

// Close closes the database connection
func (dm *DatabaseManager) Close() error {
	sqlDB, err := dm.db.DB()
	if err != nil {
		return err
	}
	return sqlDB.Close()
}

// initSampleData initializes the database with sample data
func (dm *DatabaseManager) initSampleData() error {
	// Check if sample data already exists
	var count int64
	dm.db.Model(&core.Contract{}).Count(&count)
	if count > 0 {
		return nil // Sample data already exists
	}

	// Create sample contracts
	contracts := []core.Contract{
		{
			Symbol:            "GOLD2024DEC",
			ContractType:      core.ContractTypeGoldFutures,
			ExpiryDate:        time.Date(2024, 12, 31, 0, 0, 0, 0, time.UTC),
			ContractSize:      100.0, // 100 troy ounces
			TickSize:          0.01,
			InitialMargin:     5000.0,
			MaintenanceMargin: 3500.0,
			IsActive:          true,
		},
		{
			Symbol:            "GOLD2025MAR",
			ContractType:      core.ContractTypeGoldFutures,
			ExpiryDate:        time.Date(2025, 3, 31, 0, 0, 0, 0, time.UTC),
			ContractSize:      100.0,
			TickSize:          0.01,
			InitialMargin:     5200.0,
			MaintenanceMargin: 3700.0,
			IsActive:          true,
		},
		{
			Symbol:            "GOLD2025JUN",
			ContractType:      core.ContractTypeGoldFutures,
			ExpiryDate:        time.Date(2025, 6, 30, 0, 0, 0, 0, time.UTC),
			ContractSize:      100.0,
			TickSize:          0.01,
			InitialMargin:     5400.0,
			MaintenanceMargin: 3900.0,
			IsActive:          true,
		},
	}

	for _, contract := range contracts {
		if err := dm.db.Create(&contract).Error; err != nil {
			return fmt.Errorf("failed to create contract %s: %w", contract.Symbol, err)
		}
	}

	// Create sample user
	user := core.User{
		Username:        "demo_trader",
		Email:           "demo@example.com",
		AccountBalance:  100000.0,
		MarginAvailable: 100000.0,
		IsActive:        true,
	}

	if err := dm.db.Create(&user).Error; err != nil {
		return fmt.Errorf("failed to create sample user: %w", err)
	}

	return nil
}

// JSONStorage handles JSON file-based persistence
type JSONStorage struct {
	storageDir string
}

// NewJSONStorage creates a new JSON storage manager
func NewJSONStorage(storageDir string) (*JSONStorage, error) {
	if err := os.MkdirAll(storageDir, 0755); err != nil {
		return nil, fmt.Errorf("failed to create storage directory: %w", err)
	}

	return &JSONStorage{storageDir: storageDir}, nil
}

// SaveTrades saves trades to JSON file
func (js *JSONStorage) SaveTrades(trades map[string]interface{}) error {
	return js.saveToFile("trades.json", trades)
}

// LoadTrades loads trades from JSON file
func (js *JSONStorage) LoadTrades() (map[string]interface{}, error) {
	var trades map[string]interface{}
	err := js.loadFromFile("trades.json", &trades)
	if err != nil {
		return make(map[string]interface{}), nil // Return empty map if file doesn't exist
	}
	return trades, nil
}

// SavePositions saves positions to JSON file
func (js *JSONStorage) SavePositions(positions map[string]interface{}) error {
	return js.saveToFile("positions.json", positions)
}

// LoadPositions loads positions from JSON file
func (js *JSONStorage) LoadPositions() (map[string]interface{}, error) {
	var positions map[string]interface{}
	err := js.loadFromFile("positions.json", &positions)
	if err != nil {
		return make(map[string]interface{}), nil
	}
	return positions, nil
}

// SaveUserDecisions saves user decisions to JSON file
func (js *JSONStorage) SaveUserDecisions(decisions map[string]interface{}) error {
	return js.saveToFile("user_decisions.json", decisions)
}

// LoadUserDecisions loads user decisions from JSON file
func (js *JSONStorage) LoadUserDecisions() (map[string]interface{}, error) {
	var decisions map[string]interface{}
	err := js.loadFromFile("user_decisions.json", &decisions)
	if err != nil {
		return make(map[string]interface{}), nil
	}
	return decisions, nil
}

// SaveAIAnalysis saves AI analysis to JSON file
func (js *JSONStorage) SaveAIAnalysis(analysis map[string]interface{}) error {
	return js.saveToFile("ai_analysis.json", analysis)
}

// LoadAIAnalysis loads AI analysis from JSON file
func (js *JSONStorage) LoadAIAnalysis() (map[string]interface{}, error) {
	var analysis map[string]interface{}
	err := js.loadFromFile("ai_analysis.json", &analysis)
	if err != nil {
		return make(map[string]interface{}), nil
	}
	return analysis, nil
}

// saveToFile saves data to a JSON file
func (js *JSONStorage) saveToFile(filename string, data interface{}) error {
	filePath := filepath.Join(js.storageDir, filename)
	
	jsonData, err := json.MarshalIndent(data, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal data to JSON: %w", err)
	}

	if err := os.WriteFile(filePath, jsonData, 0644); err != nil {
		return fmt.Errorf("failed to write JSON file %s: %w", filename, err)
	}

	return nil
}

// loadFromFile loads data from a JSON file
func (js *JSONStorage) loadFromFile(filename string, target interface{}) error {
	filePath := filepath.Join(js.storageDir, filename)
	
	if _, err := os.Stat(filePath); os.IsNotExist(err) {
		return fmt.Errorf("file %s does not exist", filename)
	}

	data, err := os.ReadFile(filePath)
	if err != nil {
		return fmt.Errorf("failed to read JSON file %s: %w", filename, err)
	}

	if err := json.Unmarshal(data, target); err != nil {
		return fmt.Errorf("failed to unmarshal JSON from %s: %w", filename, err)
	}

	return nil
}

// Storage interface defines the contract for storage operations
type Storage interface {
	SaveTrades(trades map[string]interface{}) error
	LoadTrades() (map[string]interface{}, error)
	SavePositions(positions map[string]interface{}) error
	LoadPositions() (map[string]interface{}, error)
	SaveUserDecisions(decisions map[string]interface{}) error
	LoadUserDecisions() (map[string]interface{}, error)
	SaveAIAnalysis(analysis map[string]interface{}) error
	LoadAIAnalysis() (map[string]interface{}, error)
}

// Ensure JSONStorage implements Storage interface
var _ Storage = (*JSONStorage)(nil)