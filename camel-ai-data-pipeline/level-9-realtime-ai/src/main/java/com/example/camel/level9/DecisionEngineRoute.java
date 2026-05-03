package com.example.camel.level9;

import org.apache.camel.builder.RouteBuilder;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

/**
 * Level 9 — Decision Engine Route.
 * Orchestrates multi-agent AI analysis and routes based on decision confidence.
 * Includes audit logging and real-time dashboard updates.
 */
@Component
public class DecisionEngineRoute extends RouteBuilder {

    @Autowired
    private DecisionEngine decisionEngine;

    @Autowired
    private AuditLogger auditLogger;

    @Override
    public void configure() {
        from("kafka:market.signals?brokers={{kafka.brokers}}&groupId=decision-engine")
            .routeId("decision-engine")
            .unmarshal().json()
            .process(decisionEngine)
            .choice()
                .when(header("confidence").isGreaterThan(0.85))
                    .log("HIGH confidence decision: ${header.selectedAction}")
                    .to("direct:execute-action")
                .when(header("confidence").isGreaterThan(0.60))
                    .log("MEDIUM confidence — queuing for review")
                    .to("direct:queue-for-review")
                .otherwise()
                    .log("LOW confidence — requesting human approval")
                    .to("direct:request-approval")
            .end()
            .process(auditLogger)
            .to("direct:dashboard-update");

        from("direct:execute-action")
            .log("Executing action: ${header.selectedAction} for ${header.symbol}");

        from("direct:queue-for-review")
            .to("kafka:decisions.review?brokers={{kafka.brokers}}");

        from("direct:request-approval")
            .to("kafka:decisions.approval?brokers={{kafka.brokers}}");
    }
}
