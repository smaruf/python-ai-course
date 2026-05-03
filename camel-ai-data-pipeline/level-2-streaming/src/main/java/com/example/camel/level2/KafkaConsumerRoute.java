package com.example.camel.level2;

import org.apache.camel.builder.RouteBuilder;
import org.springframework.stereotype.Component;

/**
 * Level 2 — Kafka Consumer Route.
 * Consumes from raw.events topic, processes, and republishes to processed.events.
 */
@Component
public class KafkaConsumerRoute extends RouteBuilder {

    @Override
    public void configure() {
        errorHandler(deadLetterChannel(
            "kafka:dead.letter.queue?brokers={{kafka.brokers}}")
            .maximumRedeliveries(3)
            .redeliveryDelay(500)
            .useExponentialBackOff()
            .logExhausted(true));

        from("kafka:raw.events"
            + "?brokers={{kafka.brokers}}"
            + "&groupId=pipeline-consumer-group"
            + "&autoOffsetReset=earliest"
            + "&maxPollRecords=100"
            + "&autoCommitEnable=true")
            .routeId("kafka-consumer")
            .log("Received event from Kafka: ${body}")
            .unmarshal().json()
            .bean(StreamProcessor.class, "process")
            .marshal().json()
            .to("kafka:processed.events?brokers={{kafka.brokers}}");
    }
}
