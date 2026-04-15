# 🧩 Level 0 — Fundamentals (Getting Started)

> **[← Back to Project](../README.md)** | **Next: [Level 1 — Data Engineering Basics →](../level-1-data-engineering/)**

## 🎯 Goal

Understand Apache Camel basics and build simple data flows. No external dependencies required — runs out of the box.

## ✅ Features

- Basic Camel routes (file → log, REST → console)
- Message transformation (JSON ↔ String)
- Simple filtering and content-based routing
- Understanding of Exchange, Message, and Body concepts

## 🛠 Tech Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| Java | 17+ | Primary language |
| Spring Boot | 3.x | Application framework |
| Apache Camel | 4.x | Integration framework |
| Maven | 3.8+ | Build tool |

## 📁 Structure

```
level-0-fundamentals/
├── README.md
├── pom.xml
└── src/
    └── main/
        ├── java/com/example/camel/level0/
        │   ├── Level0Application.java       # Spring Boot entry point
        │   ├── FileToLogRoute.java          # File → Log route
        │   ├── RestToConsoleRoute.java      # REST → Console route
        │   └── MessageTransformer.java      # JSON ↔ String transformer
        └── resources/
            ├── application.yml
            └── input/
                └── sample.json              # Sample input file
```

## 🚀 Run

```bash
cd level-0-fundamentals
mvn spring-boot:run
```

Drop a file into `src/main/resources/input/` and watch the log output.

## 📌 Key Code Examples

### File to Log Route

```java
@Component
public class FileToLogRoute extends RouteBuilder {
    @Override
    public void configure() {
        from("file:input?noop=true")
            .log("Processing file: ${header.CamelFileName}")
            .log("Content: ${body}")
            .to("file:output");
    }
}
```

### REST to Console Route

```java
@Component
public class RestToConsoleRoute extends RouteBuilder {
    @Override
    public void configure() {
        rest("/api")
            .post("/message")
            .to("direct:processMessage");

        from("direct:processMessage")
            .log("Received: ${body}")
            .transform().simple("Processed: ${body}");
    }
}
```

### Content-Based Router

```java
from("direct:route")
    .choice()
        .when(jsonpath("$.type").isEqualTo("alert"))
            .to("log:alerts")
        .when(jsonpath("$.type").isEqualTo("info"))
            .to("log:info")
        .otherwise()
            .to("log:unknown");
```

## 📖 Concepts Learned

1. **Route**: The fundamental unit in Camel — defines from/to/transform
2. **Exchange**: The message container travelling through a route
3. **Message**: Contains body, headers, and attachments
4. **Component**: Adapter for a protocol or technology (file, http, log, etc.)
5. **EIP**: Enterprise Integration Patterns — reusable integration solutions

## ➡️ Next Level

Once comfortable with routing basics, move to [Level 1 — Data Engineering Basics](../level-1-data-engineering/) to build structured pipelines with databases.
