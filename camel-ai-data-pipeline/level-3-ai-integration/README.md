# 🧩 Level 3 — AI Integration (Core Layer)

> **[← Level 2](../level-2-streaming/)** | **[↑ Back to Project](../README.md)** | **[Level 4 →](../level-4-intelligent-routing/)**

## 🎯 Goal

Enhance Camel pipelines with AI intelligence. Use LLMs (Large Language Models) for text classification, summarization, and transformation — integrating AI as a first-class Camel processor.

## ✅ Features

- LLM-based text processing (classification, summarization, extraction)
- Prompt-based message transformations
- AI as a Camel `Processor` bean
- OpenAI API integration with local Ollama fallback
- Rate limiting and circuit-breaker for AI calls
- Async AI processing with result correlation

## 🛠 Tech Stack

| Technology | Purpose |
|-----------|---------|
| OpenAI API (GPT-4o) | Cloud LLM for text processing |
| Ollama (llama3.1) | Local LLM fallback (no API key required) |
| LangChain4j | Java LLM abstraction layer |
| Apache Camel | Pipeline orchestration |
| Camel Resilience4j | Circuit breaker for AI calls |

## 📁 Structure

```
level-3-ai-integration/
├── README.md
├── pom.xml
└── src/
    └── main/
        ├── java/com/example/camel/level3/
        │   ├── Level3Application.java
        │   ├── AiEnrichmentRoute.java        # Main AI enrichment route
        │   ├── processor/
        │   │   ├── SentimentProcessor.java   # AI sentiment classifier
        │   │   ├── SummaryProcessor.java     # AI text summarizer
        │   │   └── ClassificationProcessor.java # AI topic classifier
        │   ├── client/
        │   │   ├── OpenAiClient.java         # OpenAI API wrapper
        │   │   └── OllamaClient.java         # Local Ollama wrapper
        │   └── model/
        │       ├── NewsEvent.java            # Input model
        │       └── EnrichedNewsEvent.java    # Output model with AI fields
        └── resources/
            ├── application.yml
            └── prompts/
                ├── sentiment.txt             # Sentiment analysis prompt
                ├── summary.txt               # Summarization prompt
                └── classification.txt        # Topic classification prompt
```

## 🚀 Run

```bash
# Option A: Use OpenAI (requires API key)
export OPENAI_API_KEY="your-key-here"

# Option B: Use local Ollama
ollama pull llama3.1:8b
ollama serve

# Run
mvn spring-boot:run
```

## 📌 Use Case

```
Market news article (raw text)
    ↓ (Kafka Consumer)
NewsEvent { title, body, source }
    ↓ (SentimentProcessor)
AI call → { sentiment: "positive", confidence: 0.87 }
    ↓ (SummaryProcessor)
AI call → { summary: "Company beats earnings expectations..." }
    ↓ (ClassificationProcessor)
AI call → { topics: ["earnings", "tech", "growth"] }
    ↓
EnrichedNewsEvent { ...original + sentiment + summary + topics }
    ↓ (Kafka Producer)
Kafka topic: news.enriched
```

## 📌 Key Code Examples

### AI Processor (Sentiment Analysis)

```java
@Component
public class SentimentProcessor implements Processor {

    private final AiClient aiClient;

    @Override
    public void process(Exchange exchange) throws Exception {
        NewsEvent news = exchange.getIn().getBody(NewsEvent.class);

        String prompt = String.format("""
            Analyze the sentiment of the following market news.
            Respond with JSON: {"sentiment": "positive|negative|neutral", "confidence": 0.0-1.0}

            News: %s
            """, news.getBody());

        String response = aiClient.complete(prompt);
        SentimentResult result = objectMapper.readValue(response, SentimentResult.class);

        exchange.getIn().setHeader("sentiment", result.getSentiment());
        exchange.getIn().setHeader("confidence", result.getConfidence());
    }
}
```

### AI Enrichment Route

```java
@Component
public class AiEnrichmentRoute extends RouteBuilder {
    @Override
    public void configure() {
        from("kafka:news.raw?brokers=localhost:9092&groupId=ai-enricher")
            .routeId("ai-enrichment")
            .unmarshal().json(NewsEvent.class)
            .process(sentimentProcessor)
            .process(summaryProcessor)
            .process(classificationProcessor)
            .marshal().json()
            .to("kafka:news.enriched?brokers=localhost:9092")
            .log("Enriched: sentiment=${header.sentiment}, confidence=${header.confidence}");
    }
}
```

### Circuit Breaker for AI Calls

```java
from("direct:aiCall")
    .circuitBreaker()
        .resilience4jConfiguration()
            .failureRateThreshold(50)
            .waitDurationInOpenState(30000)
        .end()
        .to("direct:openAiCall")
    .onFallback()
        .to("direct:ollamaCall")
    .end();
```

## 📖 Concepts Learned

1. **AI as a Processor**: Treat LLM calls like any other Camel processing step
2. **Prompt Engineering**: Structured prompts with JSON output constraints
3. **Fallback Chain**: OpenAI → Ollama graceful degradation
4. **Circuit Breaker**: Prevent cascade failures when AI service is down
5. **Async AI Processing**: Non-blocking AI calls with correlation IDs

## ➡️ Next Level

Your pipeline is now AI-aware. Learn how to use AI output to drive routing decisions in [Level 4 — Intelligent Routing & Enrichment](../level-4-intelligent-routing/).
