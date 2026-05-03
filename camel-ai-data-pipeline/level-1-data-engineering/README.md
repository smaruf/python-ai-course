# 🧩 Level 1 — Data Engineering Basics

> **[← Level 0](../level-0-fundamentals/)** | **[↑ Back to Project](../README.md)** | **[Level 2 →](../level-2-streaming/)**

## 🎯 Goal

Build structured data pipelines that ingest raw data, transform it into clean JSON, and persist it to a database with proper error handling and retries.

## ✅ Features

- Ingest data from REST APIs and CSV files
- Transform data into structured JSON
- Store enriched records in PostgreSQL and MongoDB
- Error handling with dead-letter queue and configurable retries
- Scheduled polling routes

## 🛠 Tech Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| Apache Camel | 4.x | Integration & routing |
| Spring Boot | 3.x | Application framework |
| PostgreSQL | 15+ | Relational data storage |
| MongoDB | 6+ | Document storage |
| Camel SQL Component | 4.x | DB operations |
| Camel Jackson | 4.x | JSON marshalling |

## 📁 Structure

```
level-1-data-engineering/
├── README.md
├── pom.xml
├── docker-compose.yml            # PostgreSQL + MongoDB
└── src/
    └── main/
        ├── java/com/example/camel/level1/
        │   ├── Level1Application.java
        │   ├── CsvIngestionRoute.java       # CSV → Transform → DB
        │   ├── ApiIngestionRoute.java       # REST API polling route
        │   ├── DataTransformer.java         # CSV → JSON transformer
        │   ├── DatabasePersistRoute.java    # JSON → PostgreSQL
        │   └── ErrorHandlingRoute.java      # DLQ + retry config
        └── resources/
            ├── application.yml
            ├── db/
            │   └── schema.sql               # DB schema
            └── data/
                └── sample.csv
```

## 🚀 Run

```bash
# Start databases
docker-compose up -d postgres mongo

# Run the pipeline
mvn spring-boot:run
```

## 📌 Use Case

```
Raw CSV file
    ↓ (Camel File Consumer)
Parsed CSV records
    ↓ (DataTransformer Bean)
Structured JSON { id, name, value, timestamp }
    ↓ (Camel SQL / MongoDB Component)
PostgreSQL / MongoDB
```

## 📌 Key Code Examples

### CSV Ingestion Route

```java
@Component
public class CsvIngestionRoute extends RouteBuilder {
    @Override
    public void configure() {
        errorHandler(deadLetterChannel("file:error-queue")
            .maximumRedeliveries(3)
            .redeliveryDelay(1000)
            .logRetryAttempted(true));

        from("file:data/input?include=.*\\.csv&move=processed")
            .routeId("csv-ingestor")
            .log("Ingesting file: ${header.CamelFileName}")
            .unmarshal().csv()
            .split(body())
                .bean(DataTransformer.class, "transform")
                .marshal().json()
                .to("sql:INSERT INTO records(data) VALUES(:#data)")
            .end()
            .log("File processed: ${header.CamelFileName}");
    }
}
```

### API Polling Route

```java
from("timer:api-poll?period=60000")
    .to("https://api.example.com/data")
    .unmarshal().json(Map.class)
    .bean(DataTransformer.class, "fromApi")
    .to("mongodb:myDb?database=pipeline&collection=records&operation=insert");
```

### Error Handling with DLQ

```java
errorHandler(deadLetterChannel("direct:errorHandler")
    .maximumRedeliveries(3)
    .redeliveryDelay(2000)
    .useExponentialBackOff()
    .maximumRedeliveryDelay(30000));
```

## 📖 Concepts Learned

1. **Dead-Letter Channel**: Route failed messages to a safe location
2. **Retry Policy**: Configurable redelivery with exponential backoff
3. **Data Marshalling**: Convert between CSV, JSON, Java objects
4. **Scheduled Routes**: Timer-based polling with configurable periods
5. **Database Integration**: SQL and MongoDB Camel components

## ➡️ Next Level

Ready for event-driven architecture? Move to [Level 2 — Streaming & Real-Time Processing](../level-2-streaming/).
