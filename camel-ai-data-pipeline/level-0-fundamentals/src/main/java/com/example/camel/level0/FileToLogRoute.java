package com.example.camel.level0;

import org.apache.camel.builder.RouteBuilder;
import org.springframework.stereotype.Component;

/**
 * Level 0 — Fundamentals: File to Log route.
 * Reads files from the input directory, logs their content, and writes to output.
 */
@Component
public class FileToLogRoute extends RouteBuilder {

    @Override
    public void configure() {
        from("file:input?noop=true")
            .routeId("file-to-log")
            .log("Processing file: ${header.CamelFileName}")
            .log("File content: ${body}")
            .to("file:output");
    }
}
