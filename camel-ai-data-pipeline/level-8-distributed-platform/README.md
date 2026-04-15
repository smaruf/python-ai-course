# 🧩 Level 8 — Distributed AI Data Platform (Expert Level)

> **[← Level 7](../level-7-domain-finance/)** | **[↑ Back to Project](../README.md)** | **[Level 9 →](../level-9-realtime-ai/)**

## 🎯 Goal

Build a scalable, cloud-ready intelligent data platform. Deploy Camel routes as serverless microservices on Kubernetes using Camel K, with auto-scaling consumers and a fault-tolerant distributed architecture.

## ✅ Features

- Microservices architecture with independent Camel K routes
- Multi-model AI orchestration (GPT-4o + local fallback)
- Streaming + batch hybrid pipelines
- Auto-scaling consumers via KEDA
- Fault-tolerant distributed system with circuit breakers
- Helm charts for one-command deployment
- GitOps-ready configuration

## 🛠 Tech Stack

| Technology | Purpose |
|-----------|---------|
| Camel K | Serverless Apache Camel on Kubernetes |
| Kubernetes | Container orchestration |
| Docker | Containerization |
| KEDA | Kubernetes Event-Driven Autoscaling |
| Strimzi | Kafka on Kubernetes |
| Istio (optional) | Service mesh, mTLS |
| Helm | Kubernetes package manager |

## 📁 Structure

```
level-8-distributed-platform/
├── README.md
├── docker-compose.yml            # Local simulation
├── helm/
│   └── camel-pipeline/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│           ├── deployment.yaml
│           ├── service.yaml
│           ├── configmap.yaml
│           └── hpa.yaml
├── k8s/
│   ├── namespace.yaml
│   ├── kafka.yaml                # Strimzi Kafka CR
│   ├── keda-scaledobject.yaml    # Auto-scaling config
│   └── camel-k/
│       ├── ingestor.yaml         # CamelIntegration CR
│       ├── ai-enricher.yaml
│       └── publisher.yaml
└── src/
    └── main/
        ├── java/com/example/camel/level8/
        │   ├── Level8Application.java
        │   ├── IngestorRoute.java              # Data ingestion microservice
        │   ├── AiEnricherRoute.java            # AI enrichment microservice
        │   ├── PublisherRoute.java             # Output publishing microservice
        │   └── MultiModelOrchestrator.java     # Multi-AI model routing
        └── resources/
            └── application.yml
```

## 🚀 Deploy

### Local (Docker Compose)

```bash
docker-compose up -d
mvn spring-boot:run
```

### Kubernetes (Camel K)

```bash
# Install Camel K operator
kubectl apply -f https://github.com/apache/camel-k/releases/download/v2.2.0/camel-k.yaml

# Deploy routes as serverless integrations
kamel run src/main/java/com/example/camel/level8/IngestorRoute.java \
  --trait knative.enabled=true \
  --trait autoscaling.enabled=true

kamel run src/main/java/com/example/camel/level8/AiEnricherRoute.java
kamel run src/main/java/com/example/camel/level8/PublisherRoute.java
```

### Helm Deploy

```bash
helm install camel-pipeline ./helm/camel-pipeline \
  --set kafka.brokers=kafka:9092 \
  --set openai.apiKey=$OPENAI_API_KEY \
  --set replicas.aiEnricher=3
```

## 📌 Key Code Examples

### Camel K Integration (Kubernetes-native)

```java
// IngestorRoute.java — deployed as a Camel K Integration CRD
// camel-k: dependency=camel:kafka
// camel-k: dependency=camel:http
// camel-k: trait=knative.enabled=true

public class IngestorRoute extends RouteBuilder {
    @Override
    public void configure() {
        from("timer:ingestor?period=1000")
            .to("https://api.marketdata.com/feed")
            .unmarshal().json()
            .to("kafka:market.raw?brokers={{kafka.brokers}}");
    }
}
```

### Multi-Model AI Orchestrator

```java
@Component
public class MultiModelOrchestrator extends RouteBuilder {
    @Override
    public void configure() {
        from("direct:ai-process")
            .routeId("multi-model-orchestrator")
            .choice()
                .when(header("taskType").isEqualTo("sentiment"))
                    .to("direct:openai-gpt4o")      // Best for sentiment
                .when(header("taskType").isEqualTo("extraction"))
                    .to("direct:openai-gpt4o-mini")  // Cost-effective
                .when(header("taskType").isEqualTo("summarize"))
                    .to("direct:ollama-llama3")       // Local, fast
                .otherwise()
                    .to("direct:openai-gpt4o")
            .end()
            .circuitBreaker()
                .to("direct:primary-model")
            .onFallback()
                .to("direct:fallback-model")
            .end();
    }
}
```

### KEDA Auto-Scaling Config

```yaml
# keda-scaledobject.yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: ai-enricher-scaler
spec:
  scaleTargetRef:
    name: ai-enricher
  minReplicaCount: 1
  maxReplicaCount: 20
  triggers:
    - type: kafka
      metadata:
        bootstrapServers: kafka:9092
        consumerGroup: ai-enricher-group
        topic: market.raw
        lagThreshold: "100"      # Scale up when lag > 100 messages
```

### Helm Values

```yaml
# values.yaml
kafka:
  brokers: kafka:9092
  topics:
    input: market.raw
    output: market.enriched
    alerts: market.alerts

replicas:
  ingestor: 1
  aiEnricher: 3
  publisher: 2

resources:
  aiEnricher:
    requests:
      memory: "512Mi"
      cpu: "500m"
    limits:
      memory: "1Gi"
      cpu: "1000m"
```

## 📖 Concepts Learned

1. **Camel K**: Deploy routes as Kubernetes-native serverless integrations
2. **KEDA**: Event-driven autoscaling based on Kafka consumer lag
3. **Multi-Model Orchestration**: Route AI calls to best model per task type
4. **Helm Charts**: Templated Kubernetes deployments for repeatability
5. **Fault Tolerance**: Circuit breakers + fallbacks at the infrastructure level

## ➡️ Next Level

You have a cloud-scale platform. Build the autonomous decision layer in [Level 9 — Real-Time AI Decision System](../level-9-realtime-ai/).
