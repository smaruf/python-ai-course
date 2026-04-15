package com.example.camel.level6;

import org.apache.camel.builder.RouteBuilder;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

/**
 * Level 6 — RAG Pipeline Route.
 * Accepts user queries via REST, retrieves semantically similar documents
 * from the vector database, and returns an AI-generated answer.
 */
@Component
public class RagPipelineRoute extends RouteBuilder {

    @Autowired
    private EmbeddingProcessor embeddingProcessor;

    @Autowired
    private VectorSearchProcessor vectorSearchProcessor;

    @Autowired
    private RagContextProcessor ragContextProcessor;

    @Override
    public void configure() {
        rest("/api")
            .post("/ask")
                .consumes("application/json")
                .produces("application/json")
                .to("direct:rag-pipeline");

        from("direct:rag-pipeline")
            .routeId("rag-pipeline")
            .log("RAG query: ${body}")
            .setHeader("userQuery", body())
            .process(embeddingProcessor)      // Embed the query
            .process(vectorSearchProcessor)   // Find similar documents
            .process(ragContextProcessor)     // Build prompt + call LLM
            .log("RAG response generated")
            .transform().header("ragAnswer");
    }
}
