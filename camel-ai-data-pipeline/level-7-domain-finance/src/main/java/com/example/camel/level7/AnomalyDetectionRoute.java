package com.example.camel.level7;

import org.apache.camel.builder.RouteBuilder;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

/**
 * Level 7 — Anomaly Detection Route.
 * Consumes market ticks from Kafka, runs AI anomaly detection,
 * and routes critical anomalies to an alert topic.
 */
@Component
public class AnomalyDetectionRoute extends RouteBuilder {

    @Autowired
    private AnomalyDetectorProcessor anomalyDetectorProcessor;

    @Override
    public void configure() {
        from("kafka:market.ticks?brokers={{kafka.brokers}}&groupId=anomaly-detector")
            .routeId("anomaly-detection")
            .unmarshal().json()
            .process(anomalyDetectorProcessor)
            .choice()
                .when(header("isAnomaly").isEqualTo(true))
                    .choice()
                        .when(header("severity").isEqualTo("critical"))
                            .to("kafka:market.alerts.critical?brokers={{kafka.brokers}}")
                            .log("🚨 CRITICAL anomaly detected: ${header.anomalyType} "
                               + "on ${header.symbol}")
                        .when(header("severity").isEqualTo("high"))
                            .to("kafka:market.alerts.high?brokers={{kafka.brokers}}")
                            .log("⚠️  HIGH severity anomaly: ${header.anomalyType}")
                        .otherwise()
                            .to("kafka:market.alerts.medium?brokers={{kafka.brokers}}")
                    .end()
                .otherwise()
                    .log("Normal tick for ${header.symbol}: price=${header.price}")
            .end();
    }
}
