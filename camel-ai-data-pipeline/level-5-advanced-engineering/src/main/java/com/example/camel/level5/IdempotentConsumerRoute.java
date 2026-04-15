package com.example.camel.level5;

import org.apache.camel.builder.RouteBuilder;
import org.apache.camel.processor.idempotent.MemoryIdempotentRepository;
import org.springframework.stereotype.Component;

/**
 * Level 5 — Idempotent Consumer Route.
 * Ensures each message is processed exactly once using a message ID header.
 */
@Component
public class IdempotentConsumerRoute extends RouteBuilder {

    @Override
    public void configure() {
        from("kafka:news.enriched?brokers={{kafka.brokers}}&groupId=idempotent-consumer")
            .routeId("idempotent-consumer")
            .idempotentConsumer(header("messageId"),
                MemoryIdempotentRepository.memoryIdempotentRepository(10000))
                .skipDuplicate(true)
            .log("Processing unique message: ${header.messageId}")
            .to("direct:process-validated-news");

        from("direct:process-validated-news")
            .log("Validated and persisting: ${body}");
    }
}
