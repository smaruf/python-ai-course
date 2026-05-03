package com.example.camel.level0;

import org.apache.camel.builder.RouteBuilder;
import org.springframework.stereotype.Component;

/**
 * Level 0 — Fundamentals: REST endpoint that echoes messages to console.
 * POST to /api/message with a JSON body to see it logged.
 */
@Component
public class RestToConsoleRoute extends RouteBuilder {

    @Override
    public void configure() {
        restConfiguration()
            .component("servlet")
            .bindingMode(org.apache.camel.model.rest.RestBindingMode.json);

        rest("/api")
            .post("/message")
                .consumes("application/json")
                .produces("application/json")
                .to("direct:processMessage");

        from("direct:processMessage")
            .routeId("rest-to-console")
            .log("Received message: ${body}")
            .transform().simple("{ \"status\": \"received\", \"echo\": \"${body}\" }");
    }
}
