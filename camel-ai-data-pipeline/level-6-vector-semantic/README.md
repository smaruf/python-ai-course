# 🧩 Level 6 — AI + Vector & Semantic Layer

> **[← Level 5](../level-5-advanced-engineering/)** | **[↑ Back to Project](../README.md)** | **[Level 7 →](../level-7-domain-finance/)**

## 🎯 Goal

Enable semantic intelligence by integrating vector databases and embedding models. Build RAG (Retrieval-Augmented Generation) pipelines that ground AI responses in your own data.

## ✅ Features

- Embedding generation for incoming documents
- Vector database integration (Pinecone / Weaviate / FAISS)
- Semantic search pipelines
- RAG (Retrieval-Augmented Generation) with Camel
- Similarity-based routing and deduplication
- Semantic clustering of events

## 🛠 Tech Stack

| Technology | Purpose |
|-----------|---------|
| OpenAI Embeddings API | text-embedding-ada-002 vector generation |
| Pinecone / Weaviate | Managed vector database |
| FAISS (local) | Local vector search (no cloud needed) |
| LangChain4j | Java vector store abstraction |
| Apache Camel | Pipeline orchestration |

## 📁 Structure

```
level-6-vector-semantic/
├── README.md
├── pom.xml
├── docker-compose.yml            # Weaviate / FAISS service
└── src/
    └── main/
        ├── java/com/example/camel/level6/
        │   ├── Level6Application.java
        │   ├── EmbeddingRoute.java             # Generate + store embeddings
        │   ├── SemanticSearchRoute.java        # Query vector DB
        │   ├── RagPipelineRoute.java           # Full RAG pipeline
        │   ├── processor/
        │   │   ├── EmbeddingProcessor.java     # Generate embeddings
        │   │   ├── VectorStoreProcessor.java   # Store in vector DB
        │   │   └── RagContextProcessor.java    # Retrieve context + generate
        │   └── client/
        │       ├── EmbeddingClient.java        # OpenAI embeddings wrapper
        │       └── VectorStoreClient.java      # Vector DB wrapper
        └── resources/
            └── application.yml
```

## 🚀 Run

```bash
# Option A: Weaviate (managed local)
docker-compose up -d weaviate

# Option B: FAISS (fully local, no docker)
# FAISS runs in-process — no setup needed

export OPENAI_API_KEY="your-key-here"
mvn spring-boot:run
```

## 📌 Use Case

```
User query: "What happened with AAPL earnings?"
    ↓ (EmbeddingProcessor)
Query vector: [0.23, -0.14, 0.87, ...]
    ↓ (VectorStoreProcessor - similarity search)
Top 3 relevant news articles (from vector DB)
    ↓ (RagContextProcessor - LLM call with context)
AI answer: "Apple reported Q3 earnings beating estimates by 12%,
            driven by iPhone 15 and services growth..."
    ↓
REST API response
```

## 📌 Key Code Examples

### Embedding Generation Route

```java
@Component
public class EmbeddingRoute extends RouteBuilder {
    @Override
    public void configure() {
        from("kafka:news.enriched?brokers=localhost:9092")
            .routeId("embedding-generator")
            .unmarshal().json(EnrichedNewsEvent.class)
            .process(embeddingProcessor)    // Adds embedding vector to exchange
            .process(vectorStoreProcessor)  // Stores in vector DB
            .log("Stored embedding for: ${body.title}");
    }
}
```

### Embedding Processor

```java
@Component
public class EmbeddingProcessor implements Processor {

    private final EmbeddingClient embeddingClient;

    @Override
    public void process(Exchange exchange) throws Exception {
        EnrichedNewsEvent event = exchange.getIn().getBody(EnrichedNewsEvent.class);

        String textToEmbed = event.getTitle() + " " + event.getSummary();
        float[] embedding = embeddingClient.embed(textToEmbed);

        exchange.getIn().setHeader("embedding", embedding);
        exchange.getIn().setHeader("documentId", event.getId());
    }
}
```

### RAG Pipeline Route

```java
@Component
public class RagPipelineRoute extends RouteBuilder {
    @Override
    public void configure() {
        rest("/api/ask")
            .post()
            .to("direct:rag-pipeline");

        from("direct:rag-pipeline")
            .routeId("rag-pipeline")
            .process(queryEmbeddingProcessor)    // Embed the user query
            .process(vectorSearchProcessor)       // Find similar documents
            .process(ragContextProcessor)         // Build prompt with context
            .process(llmGeneratorProcessor)       // Generate AI response
            .marshal().json();
    }
}
```

### RAG Context Processor

```java
@Component
public class RagContextProcessor implements Processor {

    @Override
    public void process(Exchange exchange) throws Exception {
        String userQuery = exchange.getIn().getHeader("userQuery", String.class);
        List<String> contextDocs = exchange.getIn().getHeader("similarDocs", List.class);

        String contextText = String.join("\n\n", contextDocs);

        String prompt = String.format("""
            You are a financial news analyst. Answer the user's question based
            ONLY on the following context documents. If the answer is not in
            the context, say "I don't have enough information."

            Context:
            %s

            Question: %s

            Answer:
            """, contextText, userQuery);

        exchange.getIn().setBody(prompt);
    }
}
```

## 📖 Concepts Learned

1. **Embeddings**: Dense vector representations of text for semantic similarity
2. **Vector Database**: Store and query vectors by similarity (cosine, dot product)
3. **RAG Pattern**: Augment LLM prompts with retrieved context documents
4. **Semantic Search**: Find relevant documents by meaning, not keywords
5. **Grounding**: Prevent AI hallucinations by anchoring responses to real data

## ➡️ Next Level

Your pipeline has semantic intelligence. Apply it to a real-world domain in [Level 7 — Domain-Specific Intelligence (Finance)](../level-7-domain-finance/).
