# 🧩 Level 7 — Domain-Specific Intelligence (Finance Focus)

> **[← Level 6](../level-6-vector-semantic/)** | **[↑ Back to Project](../README.md)** | **[Level 8 →](../level-8-distributed-platform/)**

## 🎯 Goal

Apply the full pipeline stack to a real-world financial domain. Simulate market data feeds (FAST/FIX/ITCH protocols), detect anomalies using AI, and enrich trading signals with news correlation.

## ✅ Features

- Market data ingestion simulation (FAST/FIX/ITCH protocol formats)
- AI-based anomaly detection in price/volume data
- Trade signal enrichment with news sentiment
- News + price correlation engine
- Real-time alert system for significant market events
- Order book imbalance detection

## 🛠 Tech Stack

| Technology | Purpose |
|-----------|---------|
| Custom FIX/ITCH Parser | Market data protocol simulation |
| Camel Timer + Bean | Market data feed simulation |
| OpenAI API | Anomaly explanation and signal enrichment |
| Apache Kafka | Real-time market event streaming |
| Spring Boot | Application framework |

## 📁 Structure

```
level-7-domain-finance/
├── README.md
├── pom.xml
├── docker-compose.yml
└── src/
    └── main/
        ├── java/com/example/camel/level7/
        │   ├── Level7Application.java
        │   ├── MarketDataRoute.java            # ITCH/FIX simulation
        │   ├── AnomalyDetectionRoute.java      # AI anomaly detection
        │   ├── TradeSignalRoute.java           # Signal enrichment
        │   ├── NewsCorrelationRoute.java        # News + price correlation
        │   ├── AlertRoute.java                 # Alert generation
        │   ├── simulator/
        │   │   ├── MarketDataSimulator.java    # Generates fake market data
        │   │   ├── FixMessageParser.java       # FIX protocol parser
        │   │   └── ItchMessageParser.java      # ITCH protocol parser
        │   ├── processor/
        │   │   ├── AnomalyDetectorProcessor.java
        │   │   ├── SignalEnricherProcessor.java
        │   │   └── CorrelationProcessor.java
        │   └── model/
        │       ├── MarketTick.java
        │       ├── TradeSignal.java
        │       └── AnomalyAlert.java
        └── resources/
            └── application.yml
```

## 🚀 Run

```bash
docker-compose up -d

export OPENAI_API_KEY="your-key-here"
mvn spring-boot:run

# Watch alerts in real-time:
# http://localhost:8080/api/alerts
```

## 📌 Pipeline

```
Market Data Simulator (FAST/FIX/ITCH)
    ↓ (Camel Timer → MarketDataSimulator)
MarketTick { symbol, price, volume, timestamp, side }
    ↓ (AnomalyDetectorProcessor)
AI analysis → { isAnomaly: true, type: "price_spike", severity: "high" }
    ↓ (Camel Choice)
    ├── anomaly detected → AlertRoute → Kafka: market.alerts
    └── normal           → SignalEnricherProcessor
                                ↓
                         NewsCorrelationProcessor
                                ↓
                         EnrichedSignal { tick + sentiment + news_summary }
                                ↓
                         Kafka: market.signals
```

## 📌 Key Code Examples

### Market Data Simulation Route

```java
@Component
public class MarketDataRoute extends RouteBuilder {
    @Override
    public void configure() {
        // Simulate high-frequency market data feed
        from("timer:market-feed?period=100&delay=0")
            .routeId("market-data-feed")
            .bean(MarketDataSimulator.class, "generateTick")
            .marshal().json()
            .to("kafka:market.ticks?brokers=localhost:9092")
            .log(LoggingLevel.DEBUG, "Tick: ${body}");
    }
}
```

### AI Anomaly Detection Processor

```java
@Component
public class AnomalyDetectorProcessor implements Processor {

    @Override
    public void process(Exchange exchange) throws Exception {
        MarketTick tick = exchange.getIn().getBody(MarketTick.class);
        List<MarketTick> recentTicks = tickBuffer.getRecent(tick.getSymbol(), 100);

        String prompt = String.format("""
            You are a quantitative analyst. Analyze this market tick for anomalies.

            Current tick: %s
            Recent 100 ticks statistics:
              - Avg price: %.2f
              - Std dev:   %.2f
              - Avg volume: %.0f

            Is this tick anomalous? Respond with JSON:
            {
              "isAnomaly": true|false,
              "type": "price_spike|volume_spike|price_drop|flash_crash|normal",
              "severity": "critical|high|medium|low|none",
              "explanation": "brief explanation"
            }
            """,
            objectMapper.writeValueAsString(tick),
            stats.getMeanPrice(), stats.getStdDev(), stats.getMeanVolume());

        AnomalyResult result = aiClient.complete(prompt, AnomalyResult.class);

        exchange.getIn().setHeader("isAnomaly", result.isAnomaly());
        exchange.getIn().setHeader("anomalyType", result.getType());
        exchange.getIn().setHeader("severity", result.getSeverity());
    }
}
```

### Alert Route

```java
@Component
public class AlertRoute extends RouteBuilder {
    @Override
    public void configure() {
        from("kafka:market.ticks")
            .process(anomalyDetectorProcessor)
            .choice()
                .when(header("isAnomaly").isEqualTo(true))
                    .choice()
                        .when(header("severity").isEqualTo("critical"))
                            .to("kafka:market.alerts.critical")
                            .to("direct:notify-ops-team")
                        .when(header("severity").isEqualTo("high"))
                            .to("kafka:market.alerts.high")
                        .otherwise()
                            .to("kafka:market.alerts.medium")
                    .end()
                .otherwise()
                    .to("direct:normal-processing")
            .end();
    }
}
```

### News + Price Correlation

```java
@Component
public class CorrelationProcessor implements Processor {

    @Override
    public void process(Exchange exchange) throws Exception {
        MarketTick tick = exchange.getIn().getBody(MarketTick.class);

        // Find related news in last 30 minutes
        List<EnrichedNewsEvent> recentNews = newsRepository
            .findBySymbolAndTimestampAfter(tick.getSymbol(),
                Instant.now().minus(30, ChronoUnit.MINUTES));

        String newsContext = recentNews.stream()
            .map(n -> n.getTitle() + ": " + n.getSummary())
            .collect(Collectors.joining("\n"));

        String prompt = String.format("""
            Correlate this price movement with recent news for %s.
            Price change: %.2f%%
            Recent news: %s

            Return JSON: { "correlation": "strong|moderate|weak|none",
                           "explanation": "brief text" }
            """, tick.getSymbol(), tick.getPriceChangePct(), newsContext);

        CorrelationResult result = aiClient.complete(prompt, CorrelationResult.class);
        exchange.getIn().setHeader("newsCorrelation", result.getCorrelation());
    }
}
```

## 📖 Concepts Learned

1. **Market Data Protocols**: FIX (order routing), ITCH (market depth), FAST (compression)
2. **Statistical Anomaly Detection**: Z-score, rolling window analysis
3. **AI-Augmented Quant Analysis**: LLM explanation of statistical anomalies
4. **Event Correlation**: Linking price movements to news events
5. **Low-Latency Patterns**: Optimized Camel routes for high-frequency data

## ➡️ Next Level

Your domain system is complete. Scale it to the cloud in [Level 8 — Distributed AI Data Platform](../level-8-distributed-platform/).
