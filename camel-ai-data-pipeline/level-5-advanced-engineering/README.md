# 🧩 Level 5 — Advanced Data Engineering

> **[← Level 4](../level-4-intelligent-routing/)** | **[↑ Back to Project](../README.md)** | **[Level 6 →](../level-6-vector-semantic/)**

## 🎯 Goal

Build production-grade data pipelines with schema evolution, data validation, idempotent consumers, delivery guarantees, and full observability.

## ✅ Features

- Schema evolution handling with Avro + Schema Registry
- Data validation pipelines with structured error reporting
- Idempotent consumers (prevent duplicate processing)
- Exactly-once / at-least-once processing semantics
- Distributed tracing with OpenTelemetry
- Metrics and monitoring with Prometheus + Grafana
- Dead-letter queue with replay capability

## 🛠 Tech Stack

| Technology | Purpose |
|-----------|---------|
| Confluent Schema Registry | Avro schema versioning |
| Apache Avro | Binary schema-defined serialization |
| Prometheus + Micrometer | Metrics collection |
| Grafana | Dashboards and alerting |
| OpenTelemetry | Distributed tracing |
| Camel JPA | Idempotent consumer repository |

## 📁 Structure

```
level-5-advanced-engineering/
├── README.md
├── pom.xml
├── docker-compose.yml            # Kafka + Schema Registry + Prometheus + Grafana
├── monitoring/
│   ├── prometheus.yml
│   └── grafana/
│       └── dashboards/
│           └── camel-pipeline.json
└── src/
    └── main/
        ├── java/com/example/camel/level5/
        │   ├── Level5Application.java
        │   ├── ProductionPipelineRoute.java   # Production route config
        │   ├── validation/
        │   │   ├── SchemaValidator.java       # Avro schema validation
        │   │   └── BusinessRuleValidator.java # Business logic validation
        │   ├── idempotency/
        │   │   └── IdempotentConsumerRoute.java
        │   └── observability/
        │       ├── MetricsConfig.java         # Prometheus metrics
        │       └── TracingConfig.java         # OpenTelemetry config
        └── resources/
            ├── application.yml
            └── avro/
                └── NewsEvent.avsc             # Avro schema definition
```

## 🚀 Run

```bash
# Start full observability stack
docker-compose up -d

# Access monitoring
# Prometheus: http://localhost:9090
# Grafana:    http://localhost:3000 (admin/admin)
# Schema Registry: http://localhost:8081

mvn spring-boot:run
```

## 📌 Key Code Examples

### Idempotent Consumer Route

```java
@Component
public class IdempotentConsumerRoute extends RouteBuilder {
    @Autowired
    private IdempotentRepository idempotentRepository;

    @Override
    public void configure() {
        from("kafka:news.enriched?brokers=localhost:9092")
            .idempotentConsumer(header("messageId"), idempotentRepository)
                .skipDuplicate(true)
            .log("Processing unique message: ${header.messageId}")
            .to("direct:processNews");
    }
}
```

### Schema Validation Route

```java
@Component
public class SchemaValidatorRoute extends RouteBuilder {
    @Override
    public void configure() {
        from("kafka:news.raw?brokers=localhost:9092")
            .routeId("schema-validator")
            .doTry()
                .unmarshal(avroDataFormat)
                .bean(BusinessRuleValidator.class, "validate")
                .to("kafka:news.validated?brokers=localhost:9092")
            .doCatch(AvroTypeException.class)
                .log("Schema validation failed: ${exception.message}")
                .to("kafka:news.schema-errors?brokers=localhost:9092")
            .doCatch(ValidationException.class)
                .log("Business rule failed: ${exception.message}")
                .to("kafka:news.business-errors?brokers=localhost:9092")
            .end();
    }
}
```

### Prometheus Metrics

```java
@Configuration
public class MetricsConfig {

    @Bean
    public RoutePolicy metricsPolicy(MeterRegistry registry) {
        return new RoutePolicy() {
            private final Counter processed = Counter.builder("camel.messages.processed")
                .description("Total messages processed")
                .register(registry);

            @Override
            public void onExchangeDone(Route route, Exchange exchange) {
                processed.increment();
            }
        };
    }
}
```

### Avro Schema (NewsEvent.avsc)

```json
{
  "type": "record",
  "name": "NewsEvent",
  "namespace": "com.example.camel.level5",
  "fields": [
    {"name": "id",        "type": "string"},
    {"name": "title",     "type": "string"},
    {"name": "body",      "type": "string"},
    {"name": "source",    "type": "string"},
    {"name": "timestamp", "type": "long",   "logicalType": "timestamp-millis"},
    {"name": "sentiment", "type": ["null", "string"], "default": null},
    {"name": "tags",      "type": {"type": "array", "items": "string"}, "default": []}
  ]
}
```

## 📖 Concepts Learned

1. **Schema Registry**: Centralized schema management with version control
2. **Avro**: Compact, fast, schema-defined binary format
3. **Idempotent Consumer**: Exactly-once semantics via message ID tracking
4. **Distributed Tracing**: End-to-end request tracing across services
5. **SLO/SLA Metrics**: Latency, throughput, and error rate dashboards

## ➡️ Next Level

Your pipeline is production-ready. Now add semantic intelligence in [Level 6 — Vector & Semantic Layer](../level-6-vector-semantic/).
