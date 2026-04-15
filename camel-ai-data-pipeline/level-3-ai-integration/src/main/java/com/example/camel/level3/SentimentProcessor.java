package com.example.camel.level3;

import org.apache.camel.Exchange;
import org.apache.camel.Processor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.util.Map;

/**
 * Level 3 — AI Sentiment Processor.
 * Calls an LLM (OpenAI or Ollama) to classify news sentiment.
 * Sets headers: "sentiment" (positive/negative/neutral) and "confidence" (0.0–1.0).
 */
@Component
public class SentimentProcessor implements Processor {

    @Value("${ai.provider:openai}")
    private String aiProvider;

    private final AiClient aiClient;

    public SentimentProcessor(AiClient aiClient) {
        this.aiClient = aiClient;
    }

    @Override
    public void process(Exchange exchange) throws Exception {
        String newsBody = exchange.getIn().getBody(String.class);

        String prompt = String.format("""
            Analyze the sentiment of the following market news.
            Return ONLY valid JSON in this exact format:
            {"sentiment": "positive|negative|neutral", "confidence": 0.0}

            News: %s
            """, newsBody);

        Map<String, Object> result = aiClient.completeJson(prompt);

        String sentiment = (String) result.getOrDefault("sentiment", "neutral");
        double confidence = ((Number) result.getOrDefault("confidence", 0.5)).doubleValue();

        exchange.getIn().setHeader("sentiment", sentiment);
        exchange.getIn().setHeader("confidence", confidence);
    }
}
