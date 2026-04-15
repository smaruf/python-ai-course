# 🧩 Level 4 — Intelligent Routing & Enrichment

> **[← Level 3](../level-3-ai-integration/)** | **[↑ Back to Project](../README.md)** | **[Level 5 →](../level-5-advanced-engineering/)**

## 🎯 Goal

Use AI output to drive dynamic routing and multi-step enrichment workflows. Build context-aware pipelines where AI makes decisions about message destinations and transformations.

## ✅ Features

- AI-based dynamic content routing
- Data enrichment using AI (metadata, tagging, scoring)
- Context-aware multi-step AI workflows
- Header-based routing from AI classification results
- Parallel AI enrichment with aggregation
- Confidence-threshold based routing logic

## 🛠 Tech Stack

| Technology | Purpose |
|-----------|---------|
| Apache Camel Choice EIP | Dynamic routing based on AI output |
| Camel Multicast | Parallel AI processing |
| Camel Aggregator EIP | Combine parallel results |
| Spring Boot | Application framework |
| OpenAI / Ollama | AI classification engine |

## 📁 Structure

```
level-4-intelligent-routing/
├── README.md
├── pom.xml
└── src/
    └── main/
        ├── java/com/example/camel/level4/
        │   ├── Level4Application.java
        │   ├── IntelligentRoutingRoute.java   # Main AI-driven routing
        │   ├── ParallelEnrichmentRoute.java   # Multicast enrichment
        │   ├── processor/
        │   │   ├── AiClassifierProcessor.java # Multi-class AI classifier
        │   │   ├── RiskScoringProcessor.java  # AI risk assessment
        │   │   └── TaggingProcessor.java      # AI metadata tagging
        │   └── aggregator/
        │       └── EnrichmentAggregator.java  # Merge parallel results
        └── resources/
            └── application.yml
```

## 🚀 Run

```bash
export OPENAI_API_KEY="your-key-here"
cd level-4-intelligent-routing
mvn spring-boot:run
```

## 📌 Key Code Examples

### AI-Driven Content Router

```java
@Component
public class IntelligentRoutingRoute extends RouteBuilder {
    @Override
    public void configure() {
        from("kafka:news.enriched?brokers=localhost:9092&groupId=router")
            .routeId("intelligent-router")
            .unmarshal().json(EnrichedNewsEvent.class)
            .process(aiClassifierProcessor)
            .choice()
                .when(header("sentiment").isEqualTo("positive"))
                    .to("kafka:market.news.bullish?brokers=localhost:9092")
                .when(header("sentiment").isEqualTo("negative"))
                    .to("kafka:market.news.bearish?brokers=localhost:9092")
                .when(header("confidence").isLessThan(0.5))
                    .to("kafka:market.news.review?brokers=localhost:9092")
                .otherwise()
                    .to("kafka:market.news.neutral?brokers=localhost:9092")
            .end()
            .log("Routed to ${header.sentiment} channel");
    }
}
```

### Parallel AI Enrichment

```java
@Component
public class ParallelEnrichmentRoute extends RouteBuilder {
    @Override
    public void configure() {
        from("kafka:news.raw?brokers=localhost:9092")
            .routeId("parallel-enrichment")
            .multicast(new EnrichmentAggregator())
                .parallelProcessing()
                .timeout(5000)
                .to("direct:sentiment-enrichment",
                    "direct:topic-enrichment",
                    "direct:risk-scoring")
            .end()
            .marshal().json()
            .to("kafka:news.fully-enriched?brokers=localhost:9092");

        from("direct:sentiment-enrichment")
            .process(sentimentProcessor);

        from("direct:topic-enrichment")
            .process(taggingProcessor);

        from("direct:risk-scoring")
            .process(riskScoringProcessor);
    }
}
```

### AI Classifier Processor

```java
@Component
public class AiClassifierProcessor implements Processor {

    @Override
    public void process(Exchange exchange) throws Exception {
        EnrichedNewsEvent event = exchange.getIn().getBody(EnrichedNewsEvent.class);

        String prompt = String.format("""
            Classify this market news for trading signal routing.
            Consider sentiment, topic, and market impact.

            Return JSON:
            {
              "sentiment": "positive|negative|neutral",
              "confidence": 0.0-1.0,
              "market_impact": "high|medium|low",
              "sectors": ["sector1", "sector2"],
              "trading_signal": "buy|sell|hold|watch"
            }

            News: %s
            Summary: %s
            """, event.getTitle(), event.getSummary());

        ClassificationResult result = aiClient.complete(prompt, ClassificationResult.class);

        exchange.getIn().setHeader("sentiment", result.getSentiment());
        exchange.getIn().setHeader("confidence", result.getConfidence());
        exchange.getIn().setHeader("tradingSignal", result.getTradingSignal());
        exchange.getIn().setHeader("marketImpact", result.getMarketImpact());
    }
}
```

### Confidence-Threshold Router

```java
from("kafka:news.classified")
    .choice()
        .when(and(
            header("sentiment").isEqualTo("positive"),
            header("confidence").isGreaterThan(0.8)))
            .to("kafka:high-confidence.bullish")
        .when(and(
            header("sentiment").isEqualTo("positive"),
            header("confidence").isGreaterThan(0.5)))
            .to("kafka:medium-confidence.bullish")
        .otherwise()
            .to("kafka:low-confidence.review");
```

## 📖 Concepts Learned

1. **Content-Based Router (CBR)**: Route messages based on content/headers
2. **AI-Driven Decisions**: Use AI output headers as routing conditions
3. **Multicast EIP**: Send to multiple routes in parallel
4. **Aggregator EIP**: Combine results from parallel processing
5. **Confidence Thresholds**: Route differently based on AI certainty levels

## ➡️ Next Level

Your pipeline is intelligent and routes dynamically. Now build production-grade reliability in [Level 5 — Advanced Data Engineering](../level-5-advanced-engineering/).
