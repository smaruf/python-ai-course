# Architecture Documentation

## System Architecture Overview

The WhatsApp Medical Report Vault uses a **modern, scalable, event-driven architecture** based on the **Webhook/Pub-Sub** and **Push-Pull** patterns. This architecture ensures reliability, scalability, and maintainability.

## Architecture Patterns

### 1. Webhook Pattern (Push from WhatsApp)

WhatsApp pushes messages to our webhook endpoint via HTTP POST requests.

**Flow**:
```
User → WhatsApp API → Webhook Endpoint (POST)
```

**Benefits**:
- Real-time message delivery
- No polling required
- Efficient use of resources

**Implementation**:
- FastAPI endpoint receives webhooks
- Signature verification for security
- Immediate acknowledgment (< 10s)

### 2. Pub-Sub Pattern (Decoupling)

Webhook publishes messages to a queue for asynchronous processing.

**Flow**:
```
Webhook → Redis/RabbitMQ Queue → Workers (subscribe)
```

**Benefits**:
- Decouples ingestion from processing
- Handles traffic spikes
- Enables horizontal scaling
- Fault tolerance

### 3. Pull Pattern (Worker Processing)

Workers pull messages from the queue and process them.

**Flow**:
```
Queue ← Workers (pull) → Process → Store
```

**Benefits**:
- Workers process at their own pace
- Auto-scaling based on queue depth
- Graceful degradation
- Backpressure handling

### 4. Push Pattern (Outbound Messages)

System pushes responses back to WhatsApp API.

**Flow**:
```
Worker → Outbound Queue → Delivery Worker → WhatsApp API (POST)
```

**Benefits**:
- Asynchronous delivery
- Retry logic
- Rate limiting
- Delivery tracking

## Component Architecture

### 1. API Layer (FastAPI)

**Responsibilities**:
- Receive WhatsApp webhooks
- Validate webhook signatures
- Acknowledge requests quickly (< 10s)
- Publish to message queue
- Provide health check endpoints

**Endpoints**:
```
POST   /webhook/whatsapp    # Receive messages
GET    /webhook/whatsapp    # Webhook verification
GET    /health              # Health check
GET    /metrics             # Prometheus metrics
```

### 2. Worker Layer (Celery/RQ)

**Responsibilities**:
- Pull messages from queue
- Process messages asynchronously
- Manage conversation sessions
- Download and validate media
- Execute business logic
- Queue outbound messages

**Workers**:
- **Message Processor**: Main message handler
- **Media Processor**: Media download & validation
- **Delivery Worker**: Send messages to WhatsApp
- **Cleanup Worker**: Session timeout handling

### 3. Business Logic Layer

**Services**:

#### Session Manager
- Maintains conversation state
- Handles multi-step flows
- Manages timeouts
- Caches in Redis

#### Media Service
- Downloads files from WhatsApp
- Validates format and size
- Performs virus scanning (optional)
- Uploads to S3

#### Metadata Collector
- Guides conversation flow
- Validates user input
- Collects report metadata
- Triggers confirmations

#### Retrieval Service
- Searches reports
- Generates signed URLs
- Enforces access control
- Logs access

#### Command Processor
- Parses commands
- Routes to appropriate handler
- Validates permissions
- Formats responses

### 4. Storage Layer

#### PostgreSQL (Metadata)
- User accounts
- Report metadata
- Session state (persistent)
- Audit logs

**Why PostgreSQL**:
- ACID transactions
- Strong consistency
- Rich query capabilities
- Proven reliability

#### Redis (Cache & Queue)
- Session cache (fast access)
- Message queues
- Rate limiting
- Temporary data

**Why Redis**:
- Sub-millisecond latency
- Pub/Sub capabilities
- TTL support
- Atomic operations

#### S3/Spaces (File Storage)
- Encrypted file storage
- High durability (99.999999999%)
- Scalable storage
- Cost-effective

**Why S3**:
- Industry standard
- Built-in encryption
- Versioning support
- Lifecycle policies

### 5. Monitoring & Observability

**Components**:
- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **CloudWatch/ELK**: Centralized logging
- **Sentry**: Error tracking

**Key Metrics**:
- Messages received/processed
- Processing latency
- Queue depth
- Error rates
- API response times

## Data Flow

### Upload Flow

```
1. User sends PDF via WhatsApp
2. WhatsApp → Webhook (POST with media_id)
3. Webhook validates signature
4. Webhook publishes to queue
5. Webhook returns 200 OK to WhatsApp (< 10s)
6. Worker pulls message from queue
7. Worker downloads media from WhatsApp
8. Worker validates file (format, size, virus scan)
9. Worker uploads to S3 (temp location)
10. Worker starts metadata collection flow
11. Worker prompts user for date
12. User responds with date
13. Repeat for hospital, report type
14. Worker confirms with user
15. User confirms
16. Worker moves file to final S3 location
17. Worker saves metadata to PostgreSQL
18. Worker logs action to audit_logs
19. Worker queues success message
20. Delivery worker sends confirmation to user
```

### Retrieval Flow

```
1. User sends "LIST" command
2. WhatsApp → Webhook
3. Webhook → Queue
4. Worker pulls command
5. Worker parses "LIST" command
6. Worker checks authorization
7. Worker queries PostgreSQL for user's reports
8. Worker formats results
9. Worker queues response message
10. Delivery worker sends list to user
11. User sends "GET 1"
12. Worker retrieves report metadata
13. Worker verifies ownership
14. Worker downloads from S3
15. Worker uploads to WhatsApp media API
16. Worker sends media message to user
17. Worker logs access to audit_logs
```

## Security Architecture

### Defense in Depth

**Layer 1: Network Security**
- VPC isolation
- Private subnets for app/db
- Security groups (firewall rules)
- NAT gateway for outbound

**Layer 2: Application Security**
- Webhook signature verification
- Phone-based authorization
- Input validation & sanitization
- Rate limiting

**Layer 3: Data Security**
- Encryption at rest (S3, database)
- Encryption in transit (TLS)
- No sensitive data in logs
- Phone number masking

**Layer 4: Access Control**
- IAM roles (least privilege)
- Database connection pools
- API token rotation
- Environment variable secrets

**Layer 5: Audit & Compliance**
- Complete audit trail
- Access logging
- Failed access attempts
- Immutable logs

## Scalability

### Horizontal Scaling

**API Layer**:
- Multiple FastAPI instances behind load balancer
- Stateless design (no session affinity needed)
- Auto-scaling based on CPU/memory

**Worker Layer**:
- Multiple worker instances
- Auto-scaling based on queue depth
- Graceful shutdown for rolling updates

**Database Layer**:
- Read replicas for queries
- Connection pooling
- Query optimization with indexes

### Vertical Scaling

**When to scale up**:
- Database becomes CPU-bound
- Redis memory usage high
- Individual worker needs more memory

### Caching Strategy

**Session Cache**:
- Cache active sessions in Redis
- TTL: 30 minutes
- Write-through on updates

**Media Cache** (optional):
- Cache recently accessed files
- CloudFront/CDN for downloads
- Signed URLs with expiration

## High Availability

### API Layer
- Multi-AZ deployment
- Health checks (every 30s)
- Auto-recovery on failure
- Minimum 2 instances

### Worker Layer
- Multiple workers (minimum 2)
- Dead letter queue for failures
- Retry logic with exponential backoff
- Graceful degradation

### Database Layer
- Primary-standby replication
- Automated failover (< 60s)
- Point-in-time recovery
- Daily automated backups

### Storage Layer
- S3: 99.999999999% durability
- Versioning enabled
- Cross-region replication (optional)
- Lifecycle policies

## Disaster Recovery

### RTO (Recovery Time Objective): 1 hour
### RPO (Recovery Point Objective): 15 minutes

**Backup Strategy**:
- Database: Automated daily backups, 30-day retention
- S3: Versioning + cross-region replication
- Configurations: Git repository

**Recovery Procedures**:
1. Restore database from backup
2. Redeploy application from Git
3. Verify S3 bucket accessibility
4. Test webhook connectivity
5. Resume worker processing

## Cost Optimization

### Compute
- Auto-scaling (scale down during low traffic)
- Spot instances for workers (60-70% savings)
- Reserved instances for baseline (30-40% savings)

### Storage
- S3 Intelligent Tiering
- Lifecycle policies (archive old files)
- Compression for large files

### Database
- Right-size instances
- Delete old sessions/logs
- Index optimization

### Monitoring
- Set up cost alerts
- Review usage monthly
- Optimize based on metrics

## Technology Decisions

### Why FastAPI?
- **Async Support**: Built-in async/await
- **Performance**: One of fastest Python frameworks
- **Documentation**: Auto-generated OpenAPI docs
- **Type Safety**: Pydantic validation
- **Modern**: Active development, great ecosystem

### Why Celery/RQ?
- **Mature**: Battle-tested in production
- **Scalable**: Horizontal scaling
- **Reliable**: Built-in retry logic
- **Monitoring**: Flower dashboard
- **Flexible**: Multiple queue backends

### Why PostgreSQL?
- **ACID**: Guaranteed data consistency
- **JSONB**: Flexible schema for context_data
- **Performance**: Excellent query optimizer
- **Extensions**: PostGIS, full-text search, etc.
- **Community**: Large ecosystem

### Why Redis?
- **Speed**: In-memory operations
- **Versatile**: Cache, queue, pub/sub
- **Simple**: Easy to deploy and manage
- **Reliable**: Persistence options
- **Popular**: Wide adoption

### Why S3/Spaces?
- **Durability**: 11 nines (99.999999999%)
- **Scalability**: Unlimited storage
- **Security**: Encryption, IAM, versioning
- **Cost**: Pay per use
- **Ecosystem**: Wide tool support

## Alternatives Considered

### Message Queue
- **RabbitMQ**: More features, but Redis is simpler
- **SQS**: AWS-only, Redis is provider-agnostic
- **Kafka**: Overkill for this use case

### Database
- **MongoDB**: Considered, but ACID not guaranteed
- **MySQL**: PostgreSQL has better JSON support
- **DynamoDB**: AWS-only, more complex

### Storage
- **Local Filesystem**: Not scalable
- **Database**: Too expensive for large files
- **Google Cloud Storage**: Similar to S3

## Future Improvements

### Phase 2
- GraphQL API (for web dashboard)
- WebSocket support (real-time updates)
- Multi-region deployment
- Advanced analytics

### Phase 3
- Machine learning (OCR, classification)
- Elasticsearch (full-text search)
- Blockchain (audit trail immutability)
- Mobile app (native iOS/Android)

## Conclusion

This architecture balances:
- **Scalability**: Handles growth from 10 to 10,000+ users
- **Reliability**: 99.9% uptime with proper deployment
- **Security**: HIPAA-conscious design
- **Cost**: Efficient use of cloud resources
- **Maintainability**: Clean separation of concerns

The webhook/pub-sub/push-pull pattern ensures the system is:
- ✅ Responsive (fast webhook acknowledgment)
- ✅ Resilient (fault-tolerant workers)
- ✅ Scalable (horizontal scaling)
- ✅ Observable (comprehensive monitoring)

---

For detailed implementation, see:
- [Component Diagram](diagrams/component-diagram.puml)
- [Sequence Diagrams](diagrams/)
- [Data Model](diagrams/data-model.puml)
- [Deployment Architecture](diagrams/deployment-architecture.puml)
