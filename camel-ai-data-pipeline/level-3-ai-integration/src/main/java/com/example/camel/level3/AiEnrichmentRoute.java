package com.example.camel.level3;

import org.apache.camel.builder.RouteBuilder;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

/**
 * Level 3 — AI Enrichment Route.
 * Consumes raw news from Kafka, enriches with AI sentiment + summary,
 * and publishes enriched records to the news.enriched topic.
 */
@Component
public class AiEnrichmentRoute extends RouteBuilder {

    @Autowired
    private SentimentProcessor sentimentProcessor;

    @Autowired
    private SummaryProcessor summaryProcessor;

    @Override
    public void configure() {
        from("kafka:news.raw?brokers={{kafka.brokers}}&groupId=ai-enricher")
            .routeId("ai-enrichment")
            .log("Enriching news with AI: ${body}")
            .process(sentimentProcessor)
            .process(summaryProcessor)
            .log("AI enrichment complete: sentiment=${header.sentiment}, "
               + "confidence=${header.confidence}")
            .marshal().json()
            .to("kafka:news.enriched?brokers={{kafka.brokers}}");
    }
}
