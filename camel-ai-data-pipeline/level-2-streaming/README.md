# 🧩 Level 2 — Streaming & Real-Time Processing

> **[← Level 1](../level-1-data-engineering/)** | **[↑ Back to Project](../README.md)** | **[Level 3 →](../level-3-ai-integration/)**

## 🎯 Goal

Introduce event-driven architecture using Apache Kafka. Build scalable, real-time pipelines that can handle high-throughput data streams with fault tolerance.

## ✅ Features

- Kafka-based streaming pipelines
- Real-time ingestion and processing
- Partitioned and scalable consumers
- Dead-letter queue (DLQ) handling for failed messages
- Consumer group management
- Back-pressure handling

## 🛠 Tech Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| Apache Kafka | 3.6+ | Event streaming platform |
| Camel Kafka Component | 4.x | Kafka integration |
| Spring Boot | 3.x | Application framework |
| Docker Compose | — | Local Kafka cluster |
| Kafdrop | — | Kafka UI for monitoring |

## 📁 Structure

```
level-2-streaming/
├── README.md
├── pom.xml
├── docker-compose.yml            # Kafka + Zookeeper + Kafdrop
└── src/
    └── main/
        ├── java/com/example/camel/level2/
        │   ├── Level2Application.java
        │   ├── KafkaProducerRoute.java      # Data → Kafka topic
        │   ├── KafkaConsumerRoute.java      # Kafka topic → Processor
        │   ├── StreamProcessorRoute.java    # Transform & re-publish
        │   ├── DeadLetterRoute.java         # DLQ handling
        │   └── KafkaConfig.java             # Kafka configuration beans
        └── resources/
            └── application.yml
```

## 🚀 Run

```bash
# Start Kafka + Zookeeper + UI
docker-compose up -d

# Run the streaming pipeline
mvn spring-boot:run

# View Kafka topics at: http://localhost:9000
```

## 📌 Pipeline

```
Data Producer
    ↓
Kafka Topic: raw.events
    ↓ (Camel Kafka Consumer)
Stream Processor (Camel Route)
    ↓ (Transform + Enrich)
Kafka Topic: processed.events
    ↓ (Camel Kafka Consumer)
Downstream Consumer (DB / API)

On error:
    ↓
Kafka Topic: dead.letter.queue
```

## 📌 Key Code Examples

### Kafka Producer Route

```java
@Component
public class KafkaProducerRoute extends RouteBuilder {
    @Override
    public void configure() {
        from("timer:data-generator?period=1000")
            .routeId("kafka-producer")
            .bean(EventGenerator.class, "generate")
            .marshal().json()
            .to("kafka:raw.events?brokers=localhost:9092")
            .log("Published event to Kafka: ${body}");
    }
}
```

### Kafka Consumer Route

```java
@Component
public class KafkaConsumerRoute extends RouteBuilder {
    @Override
    public void configure() {
        from("kafka:raw.events"
            + "?brokers=localhost:9092"
            + "&groupId=pipeline-group"
            + "&autoOffsetReset=earliest"
            + "&maxPollRecords=100")
            .routeId("kafka-consumer")
            .unmarshal().json(Map.class)
            .bean(StreamProcessor.class, "process")
            .marshal().json()
            .to("kafka:processed.events?brokers=localhost:9092");
    }
}
```

### Dead-Letter Queue Route

```java
@Component
public class DeadLetterRoute extends RouteBuilder {
    @Override
    public void configure() {
        errorHandler(deadLetterChannel("kafka:dead.letter.queue?brokers=localhost:9092")
            .maximumRedeliveries(3)
            .redeliveryDelay(500)
            .useExponentialBackOff()
            .logExhausted(true));
    }
}
```

## 📖 Concepts Learned

1. **Event-Driven Architecture**: Decouple producers from consumers via Kafka topics
2. **Consumer Groups**: Horizontal scaling with shared partition ownership
3. **Offset Management**: Exactly-once and at-least-once delivery semantics
4. **Back-Pressure**: Rate limiting and max poll record controls
5. **Dead-Letter Queue**: Isolate poison messages without stopping the pipeline

## ➡️ Next Level

Your pipelines can now handle high-throughput real-time data. Time to add intelligence! Move to [Level 3 — AI Integration](../level-3-ai-integration/).
