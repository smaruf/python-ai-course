# Multi-stage Docker build — Trading AI Platform
# Stage 1: Build fat JAR with Maven or Gradle
# Stage 2: Minimal JRE runtime image

# ── Stage 1: Build ─────────────────────────────────────────────
FROM eclipse-temurin:21-jdk-alpine AS builder

WORKDIR /build

# Cache dependency layer
COPY pom.xml .
COPY app/shared-kernel/pom.xml       app/shared-kernel/
COPY app/fix-nasdaq-engine/pom.xml   app/fix-nasdaq-engine/
COPY app/payment-ledger/pom.xml      app/payment-ledger/
COPY app/ai-gateway/pom.xml          app/ai-gateway/
COPY app/bootstrap/pom.xml           app/bootstrap/

# Download dependencies (cached unless POM changes)
RUN mvn dependency:go-offline -B 2>/dev/null || true

# Build the application
COPY . .
RUN mvn clean package -pl app/bootstrap -am -DskipTests -B

# ── Stage 2: Runtime ───────────────────────────────────────────
FROM eclipse-temurin:21-jre-alpine AS runtime

LABEL maintainer="trading-ai-platform"
LABEL description="AI-powered payment and Nasdaq FIX trading platform"

# Create non-root user
RUN addgroup -S tradingai && adduser -S tradingai -G tradingai

WORKDIR /app

# Copy fat JAR from build stage
COPY --from=builder /build/app/bootstrap/target/trading-ai-platform.jar app.jar

# Adjust ownership
RUN chown tradingai:tradingai app.jar

USER tradingai

EXPOSE 8080

ENTRYPOINT ["java", \
  "-XX:+UseContainerSupport", \
  "-XX:MaxRAMPercentage=75.0", \
  "-jar", "app.jar"]
