package com.example.camel.level4;

import org.apache.camel.builder.RouteBuilder;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

/**
 * Level 4 — Intelligent Routing Route.
 * Uses AI classification headers to dynamically route enriched news
 * to topic-specific Kafka channels.
 */
@Component
public class IntelligentRoutingRoute extends RouteBuilder {

    @Autowired
    private AiClassifierProcessor aiClassifierProcessor;

    @Override
    public void configure() {
        from("kafka:news.enriched?brokers={{kafka.brokers}}&groupId=intelligent-router")
            .routeId("intelligent-router")
            .unmarshal().json()
            .process(aiClassifierProcessor)
            .choice()
                .when(header("sentiment").isEqualTo("positive")
                    .and(header("confidence").isGreaterThan(0.7)))
                    .to("kafka:market.news.bullish?brokers={{kafka.brokers}}")
                    .log("Routed to BULLISH: confidence=${header.confidence}")
                .when(header("sentiment").isEqualTo("negative")
                    .and(header("confidence").isGreaterThan(0.7)))
                    .to("kafka:market.news.bearish?brokers={{kafka.brokers}}")
                    .log("Routed to BEARISH: confidence=${header.confidence}")
                .when(header("confidence").isLessThan(0.5))
                    .to("kafka:market.news.review?brokers={{kafka.brokers}}")
                    .log("Low confidence — sent for human review")
                .otherwise()
                    .to("kafka:market.news.neutral?brokers={{kafka.brokers}}")
                    .log("Routed to NEUTRAL")
            .end();
    }
}
