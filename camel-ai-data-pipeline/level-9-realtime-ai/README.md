# 🧩 Level 9 — Real-Time AI Decision System (Elite)

> **[← Level 8](../level-8-distributed-platform/)** | **[↑ Back to Project](../README.md)**

## 🎯 Goal

Build an autonomous intelligent system with AI-driven decision engines, feedback loops for continuous learning, event-driven AI agents, and real-time dashboards — the pinnacle of the pipeline progression.

## ✅ Features

- AI-driven decision engine with rule + model fusion
- Feedback loops (online learning from decision outcomes)
- Event-driven AI agents with tool use
- Multi-agent orchestration with Camel routing
- Real-time WebSocket dashboards
- A/B testing framework for AI model evaluation
- Audit trail for all AI decisions

## 🛠 Tech Stack

| Technology | Purpose |
|-----------|---------|
| Apache Camel | Agent orchestration and event routing |
| OpenAI Function Calling | Structured AI agent tool use |
| LangChain4j Agents | Java agent framework |
| Spring WebSocket | Real-time dashboard streaming |
| Redis | Decision cache and feedback store |
| Kafka | Event bus for agent communication |

## 📁 Structure

```
level-9-realtime-ai/
├── README.md
├── pom.xml
├── docker-compose.yml
└── src/
    └── main/
        ├── java/com/example/camel/level9/
        │   ├── Level9Application.java
        │   ├── DecisionEngineRoute.java        # Main decision pipeline
        │   ├── AgentOrchestrationRoute.java    # Multi-agent coordination
        │   ├── FeedbackLoopRoute.java          # Learning feedback pipeline
        │   ├── DashboardRoute.java             # WebSocket streaming
        │   ├── agent/
        │   │   ├── MarketAnalysisAgent.java    # AI agent with tools
        │   │   ├── RiskAssessmentAgent.java    # Risk evaluation agent
        │   │   └── ActionExecutionAgent.java   # Executes decisions
        │   ├── decision/
        │   │   ├── DecisionEngine.java         # Rule + AI fusion engine
        │   │   ├── FeedbackStore.java          # Outcome tracking
        │   │   └── AuditLogger.java            # Decision audit trail
        │   └── dashboard/
        │       ├── DashboardWebSocketHandler.java
        │       └── MetricsAggregator.java
        └── resources/
            ├── application.yml
            └── static/
                └── dashboard.html              # Real-time dashboard UI
```

## 🚀 Run

```bash
docker-compose up -d

export OPENAI_API_KEY="your-key-here"
mvn spring-boot:run

# Real-time dashboard: http://localhost:8080
# Decision audit log:  http://localhost:8080/api/decisions
# Agent status:        http://localhost:8080/api/agents
```

## 📌 Architecture

```
Live Market Data
    ↓
DecisionEngineRoute
    │
    ├── MarketAnalysisAgent (tools: fetch_price, get_news, calc_stats)
    │       ↓ analysis result
    ├── RiskAssessmentAgent (tools: check_exposure, calc_var, get_limits)
    │       ↓ risk score
    └── Decision Fusion (rules + AI confidence)
            ↓
    ActionExecutionAgent
    │   ├── HIGH confidence → Execute action
    │   ├── MEDIUM confidence → Queue for review
    │   └── LOW confidence → Request human approval
            ↓
    Outcome Tracking → FeedbackLoopRoute
            ↓
    Model Performance Update → Dashboard WebSocket
```

## 📌 Key Code Examples

### Decision Engine Route

```java
@Component
public class DecisionEngineRoute extends RouteBuilder {
    @Override
    public void configure() {
        from("kafka:market.signals?brokers=localhost:9092")
            .routeId("decision-engine")
            .unmarshal().json(TradingSignal.class)
            .process(decisionEngine)             // Rule + AI fusion
            .choice()
                .when(header("confidence").isGreaterThan(0.85))
                    .to("direct:execute-action")
                .when(header("confidence").isGreaterThan(0.60))
                    .to("direct:queue-for-review")
                .otherwise()
                    .to("direct:request-approval")
            .end()
            .to("direct:audit-log")
            .to("direct:dashboard-update");
    }
}
```

### Event-Driven AI Agent

```java
@Component
public class MarketAnalysisAgent implements Processor {

    private final AiAgentClient agentClient;

    @Override
    public void process(Exchange exchange) throws Exception {
        TradingSignal signal = exchange.getIn().getBody(TradingSignal.class);

        // Agent with tool use (OpenAI function calling)
        AgentResult result = agentClient.run(
            "Analyze " + signal.getSymbol() + " for a trading decision.",
            List.of(
                Tool.of("get_current_price",   priceService::getCurrentPrice),
                Tool.of("get_recent_news",     newsService::getRecentNews),
                Tool.of("get_technical_stats", statsService::getTechnicalStats),
                Tool.of("get_sector_sentiment", sectorService::getSentiment)
            )
        );

        exchange.getIn().setHeader("agentAnalysis", result.getConclusion());
        exchange.getIn().setHeader("agentConfidence", result.getConfidence());
        exchange.getIn().setHeader("agentActions", result.getRecommendedActions());
    }
}
```

### Feedback Loop Route

```java
@Component
public class FeedbackLoopRoute extends RouteBuilder {
    @Override
    public void configure() {
        // Collect outcomes after decisions are executed
        from("kafka:decision.outcomes?brokers=localhost:9092")
            .routeId("feedback-loop")
            .unmarshal().json(DecisionOutcome.class)
            .process(feedbackProcessor)           // Update performance metrics
            .choice()
                .when(header("outcomeAccuracy").isLessThan(0.6))
                    .log("WARNING: Model accuracy degrading, triggering review")
                    .to("direct:trigger-model-review")
                .otherwise()
                    .to("direct:update-model-stats")
            .end()
            .to("direct:dashboard-update");
    }
}
```

### Real-Time Dashboard WebSocket

```java
@Component
public class DashboardRoute extends RouteBuilder {
    @Override
    public void configure() {
        from("direct:dashboard-update")
            .routeId("dashboard-broadcaster")
            .marshal().json()
            .to("websocket://localhost:8080/dashboard?sendToAll=true");
    }
}
```

### Multi-Agent Orchestration

```java
@Component
public class AgentOrchestrationRoute extends RouteBuilder {
    @Override
    public void configure() {
        from("direct:agent-orchestration")
            .routeId("agent-orchestrator")
            // Run analysis agents in parallel
            .multicast(new DecisionAggregator())
                .parallelProcessing()
                .timeout(10000)
                .to("direct:market-analysis-agent",
                    "direct:risk-assessment-agent",
                    "direct:sentiment-agent")
            .end()
            // Fuse all agent outputs into final decision
            .process(decisionFusionProcessor)
            .to("kafka:market.decisions?brokers=localhost:9092");
    }
}
```

### Audit Logger

```java
@Component
public class AuditLogger implements Processor {

    @Override
    public void process(Exchange exchange) throws Exception {
        DecisionRecord record = DecisionRecord.builder()
            .decisionId(UUID.randomUUID().toString())
            .timestamp(Instant.now())
            .symbol(exchange.getIn().getHeader("symbol", String.class))
            .signal(exchange.getIn().getBody(TradingSignal.class))
            .agentAnalysis(exchange.getIn().getHeader("agentAnalysis", String.class))
            .confidence(exchange.getIn().getHeader("confidence", Double.class))
            .action(exchange.getIn().getHeader("selectedAction", String.class))
            .modelVersion(exchange.getIn().getHeader("modelVersion", String.class))
            .build();

        auditRepository.save(record);
        exchange.getIn().setHeader("decisionId", record.getDecisionId());
    }
}
```

## 📌 Full Pipeline Summary

```
Live Data → AI Agent Analysis → Decision Fusion → Action → Outcome
    ↑                                                          │
    └──────────── Feedback Loop (Model Updates) ←─────────────┘
```

## 📖 Concepts Learned

1. **AI Agents**: Autonomous units that use tools to gather information and reason
2. **Decision Fusion**: Combine rule-based and AI outputs for robust decisions
3. **Feedback Loops**: Track outcomes and detect model drift over time
4. **Multi-Agent Orchestration**: Coordinate parallel agents with Camel Multicast
5. **Audit Trails**: Immutable decision logs for compliance and debugging
6. **A/B Model Testing**: Route a percentage of traffic to experimental models

---

## 🏆 Congratulations!

You have completed the full journey from **Level 0** (basic file routing) to **Level 9** (autonomous AI decision system).

**What you've built:**
- A complete data engineering platform
- Real-time streaming with Apache Kafka
- AI-powered enrichment and classification
- Vector search and RAG pipelines
- Finance-domain anomaly detection
- Cloud-native deployment on Kubernetes
- Autonomous AI agents with feedback loops

**[← Back to Project Overview](../README.md)**
