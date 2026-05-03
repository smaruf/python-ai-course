package com.example.camel.level6;

import org.apache.camel.Exchange;
import org.apache.camel.Processor;
import org.springframework.stereotype.Component;

/**
 * Level 6 — Embedding Processor.
 * Generates a vector embedding for incoming text using an embedding API.
 * Sets the "embedding" header with the float[] vector representation.
 */
@Component
public class EmbeddingProcessor implements Processor {

    private final EmbeddingClient embeddingClient;

    public EmbeddingProcessor(EmbeddingClient embeddingClient) {
        this.embeddingClient = embeddingClient;
    }

    @Override
    public void process(Exchange exchange) throws Exception {
        String text = exchange.getIn().getBody(String.class);
        String documentId = exchange.getIn().getHeader("messageId", String.class);

        float[] embedding = embeddingClient.embed(text);

        exchange.getIn().setHeader("embedding", embedding);
        exchange.getIn().setHeader("documentId", documentId);
        exchange.getIn().setHeader("embeddingDimensions", embedding.length);
    }
}
