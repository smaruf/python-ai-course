# Database Schema Diagrams

All data stores used by the Yelp-Style AI Assistant, with Mermaid ERD notation.

---

## 1. PostgreSQL — Structured (Authoritative) Store

This is the **single source of truth** for all canonical business fields.
No review or photo data is written here; writes are performed only by the
business-owner portal and the CDC event bus.

```mermaid
erDiagram
    BUSINESSES {
        varchar(36)  business_id  PK
        varchar(255) name
        text         address
        varchar(20)  phone
        char(4)      price_range
        float        rating
        int          review_count
        timestamptz  created_at
        timestamptz  updated_at
    }

    BUSINESS_HOURS {
        bigserial    id           PK
        varchar(36)  business_id  FK
        varchar(10)  day_of_week
        time         open_time
        time         close_time
        boolean      is_closed
    }

    AMENITIES {
        bigserial    id           PK
        varchar(36)  business_id  FK
        varchar(60)  amenity_key
        boolean      value
        timestamptz  updated_at
    }

    CATEGORIES {
        bigserial    id           PK
        varchar(36)  business_id  FK
        varchar(60)  category_name
    }

    BUSINESSES ||--o{ BUSINESS_HOURS : "has"
    BUSINESSES ||--o{ AMENITIES      : "has"
    BUSINESSES ||--o{ CATEGORIES     : "belongs to"
```

### Key indexes

| Table            | Index                                          | Purpose                          |
|------------------|------------------------------------------------|----------------------------------|
| `businesses`     | `PK (business_id)`                             | Direct lookup                    |
| `business_hours` | `(business_id, day_of_week)`                   | Hours-by-day fast path           |
| `amenities`      | `(business_id, amenity_key)` UNIQUE            | Point lookup per amenity         |
| `businesses`     | `GIN (to_tsvector(name \|\| ' ' \|\| address))`| Full-text search                 |

---

## 2. Elasticsearch — Hot Indices

Two separate indices follow the structured / unstructured data separation
rule (TDD §3).

### 2a. Structured Index (`businesses_structured`)

```mermaid
erDiagram
    BUSINESSES_STRUCTURED_DOC {
        keyword  business_id
        text     name
        keyword  address
        keyword  phone
        keyword  price_range
        float    rating
        integer  review_count
        nested   hours
        object   amenities
        keyword  categories
        date     updated_at
    }

    HOURS_NESTED {
        keyword  day
        keyword  open_time
        keyword  close_time
        boolean  is_closed
    }

    BUSINESSES_STRUCTURED_DOC ||--o{ HOURS_NESTED : "nested hours[]"
```

### 2b. Review Text Index (`reviews_text`)

```mermaid
erDiagram
    REVIEW_DOC {
        keyword     review_id
        keyword     business_id
        keyword     user_id
        float       rating
        text        text_content
        date        created_at
        dense_vector embedding
    }
```

> `embedding` is a 384-dimension `dense_vector` field (sentence-transformers
> `all-MiniLM-L6-v2`) used for kNN approximate nearest-neighbour search.

---

## 3. Vector Database (FAISS / Pinecone)

Two separate namespaces/collections keep review and photo embeddings isolated.

```mermaid
erDiagram
    REVIEW_EMBEDDINGS {
        string   vector_id   PK
        vector   embedding
        string   review_id
        string   business_id
        float    rating
        datetime created_at
    }

    PHOTO_CAPTION_EMBEDDINGS {
        string   vector_id   PK
        vector   caption_embedding
        string   photo_id
        string   business_id
        string   caption_text
    }

    PHOTO_IMAGE_EMBEDDINGS {
        string   vector_id   PK
        vector   image_embedding
        string   photo_id
        string   business_id
    }
```

> Review embeddings use a 384-d sentence model.  
> Photo caption embeddings use the same model for text.  
> Photo image embeddings use CLIP (`ViT-B/32`, 512-d) for visual similarity.

---

## 4. Redis — Cache Store

Three logical key spaces with separate TTLs (TDD §10.2).

```mermaid
erDiagram
    QUERY_RESULT_CACHE {
        string   key         PK
        string   value_json
        integer  ttl_seconds
    }

    BUSINESS_HOURS_CACHE {
        string   key         PK
        string   value_json
        integer  ttl_seconds
    }

    QUERY_EMBEDDING_CACHE {
        string   key         PK
        string   embedding_json
        integer  ttl_seconds
    }

    CIRCUIT_BREAKER_STATE {
        string   service_name  PK
        string   state
        integer  failure_count
        float    last_failure_ts
    }
```

### Key naming conventions

| Key space                | Pattern                                   | TTL         |
|--------------------------|-------------------------------------------|-------------|
| Query result cache       | `qr:{business_id}:{query_hash}`           | 5 min       |
| Business hours cache     | `hours:{business_id}`                     | 5 min       |
| Query embedding cache    | `emb:{query_hash}`                        | 30 min      |
| Circuit breaker state    | `cb:{service_name}`                       | No expiry   |

---

## 5. Object Storage (S3-compatible) — Unstructured Content

```mermaid
erDiagram
    PHOTO_OBJECTS {
        string   object_key   PK
        string   business_id
        string   photo_id
        string   content_type
        string   url
        string   caption
        bigint   size_bytes
        datetime uploaded_at
    }

    MENU_OBJECTS {
        string   object_key   PK
        string   business_id
        string   content_type
        datetime ingested_at
        string   version
    }
```

---

## 6. Kafka Topics — Streaming Event Bus

```mermaid
erDiagram
    TOPIC_REVIEWS {
        string   topic_name
        string   partition_key
        json     payload
        long     offset
        datetime event_time
    }

    TOPIC_BUSINESS_CHANGES {
        string   topic_name
        string   partition_key
        json     payload
        long     offset
        datetime event_time
    }

    TOPIC_PHOTOS {
        string   topic_name
        string   partition_key
        json     payload
        long     offset
        datetime event_time
    }
```

| Topic                  | Partitions | Replication | Retention |
|------------------------|-----------|-------------|-----------|
| `reviews`              | 32        | 3           | 7 days    |
| `business-changes`     | 16        | 3           | 30 days   |
| `photos`               | 16        | 3           | 7 days    |
