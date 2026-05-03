package com.example.camel.level1;

import org.apache.camel.LoggingLevel;
import org.apache.camel.builder.RouteBuilder;
import org.springframework.stereotype.Component;

/**
 * Level 1 — CSV ingestion route with dead-letter channel and retry.
 * Reads CSV files, transforms each row to JSON, and persists to PostgreSQL.
 */
@Component
public class CsvIngestionRoute extends RouteBuilder {

    @Override
    public void configure() {
        errorHandler(deadLetterChannel("file:data/error-queue")
            .maximumRedeliveries(3)
            .redeliveryDelay(1000)
            .useExponentialBackOff()
            .logRetryAttempted(true)
            .logExhausted(true));

        from("file:data/input?include=.*\\.csv&move=processed")
            .routeId("csv-ingestor")
            .log("Ingesting CSV file: ${header.CamelFileName}")
            .unmarshal().csv()
            .split(body())
                .bean(DataTransformer.class, "transform")
                .marshal().json()
                .log(LoggingLevel.DEBUG, "Transformed record: ${body}")
                .to("direct:persist-record")
            .end()
            .log("Completed file: ${header.CamelFileName}");

        from("direct:persist-record")
            .routeId("db-persister")
            .to("sql:INSERT INTO records(payload, created_at) "
              + "VALUES(:?body, NOW()) "
              + "ON CONFLICT DO NOTHING");
    }
}
