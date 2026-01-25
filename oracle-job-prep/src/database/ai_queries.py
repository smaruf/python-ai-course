"""
AI-Specific SQL Queries for Oracle Database 23ai/26ai

This module contains AI-enhanced SQL queries demonstrating Oracle's
vector search, semantic similarity, and AI/ML capabilities.
"""

from typing import List, Dict, Any
from dataclasses import dataclass


# AI-Enhanced SQL Queries for Oracle 23ai/26ai
AI_SQL_QUERIES = {
    "create_vector_table": """
        -- Create table with VECTOR column for embeddings
        CREATE TABLE documents (
            doc_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            title VARCHAR2(200),
            content CLOB,
            category VARCHAR2(50),
            publish_date DATE,
            embedding VECTOR(1536, FLOAT32),  -- For OpenAI text-embedding-3-small embeddings
            created_at TIMESTAMP DEFAULT SYSTIMESTAMP
        );
        
        -- Create vector index for fast similarity search
        CREATE VECTOR INDEX idx_doc_vector ON documents(embedding)
        ORGANIZATION INMEMORY NEIGHBOR GRAPH
        DISTANCE COSINE
        WITH TARGET ACCURACY 95;
    """,
    
    "semantic_search": """
        -- Semantic similarity search using vector distance
        SELECT 
            doc_id,
            title,
            content,
            category,
            VECTOR_DISTANCE(embedding, :query_vector, COSINE) as similarity_score
        FROM documents
        WHERE category = :category  -- Traditional filter
        ORDER BY VECTOR_DISTANCE(embedding, :query_vector, COSINE)
        FETCH FIRST 10 ROWS ONLY;
        
        -- Alternative: Using vector distance in WHERE clause
        SELECT 
            doc_id,
            title,
            VECTOR_DISTANCE(embedding, :query_vector, COSINE) as similarity
        FROM documents
        WHERE VECTOR_DISTANCE(embedding, :query_vector, COSINE) < 0.3
        ORDER BY similarity;
    """,
    
    "hybrid_search": """
        -- Hybrid search: Combine vector similarity with full-text search
        SELECT 
            doc_id,
            title,
            content,
            -- Vector similarity score (0-1, lower is better for cosine)
            VECTOR_DISTANCE(embedding, :query_vector, COSINE) as vector_score,
            -- Traditional relevance score
            SCORE(1) as text_score,
            -- Combined score (weighted)
            (0.7 * VECTOR_DISTANCE(embedding, :query_vector, COSINE) + 
             0.3 * (1 - SCORE(1)/100)) as combined_score
        FROM documents
        WHERE CONTAINS(content, :search_text, 1) > 0  -- Text search
            OR VECTOR_DISTANCE(embedding, :query_vector, COSINE) < 0.5
        ORDER BY combined_score
        FETCH FIRST 20 ROWS ONLY;
    """,
    
    "vector_distance_functions": """
        -- Compare different distance metrics
        SELECT 
            doc_id,
            title,
            -- Cosine similarity (range: 0-2, lower is more similar)
            VECTOR_DISTANCE(embedding, :query_vector, COSINE) as cosine_dist,
            -- Euclidean distance
            VECTOR_DISTANCE(embedding, :query_vector, EUCLIDEAN) as euclidean_dist,
            -- Dot product (for normalized vectors)
            VECTOR_DISTANCE(embedding, :query_vector, DOT) as dot_product,
            -- Manhattan distance
            VECTOR_DISTANCE(embedding, :query_vector, MANHATTAN) as manhattan_dist
        FROM documents
        ORDER BY cosine_dist
        FETCH FIRST 5 ROWS ONLY;
    """,
    
    "vector_aggregations": """
        -- Aggregate vector operations for analytics
        SELECT 
            category,
            COUNT(*) as doc_count,
            -- Average similarity to reference vector
            AVG(VECTOR_DISTANCE(embedding, :reference_vector, COSINE)) as avg_similarity,
            -- Find most representative document (centroid-like)
            MIN(VECTOR_DISTANCE(embedding, :reference_vector, COSINE)) as best_match_score
        FROM documents
        GROUP BY category
        HAVING COUNT(*) > 10
        ORDER BY avg_similarity;
    """,
    
    "json_duality_view": """
        -- Create JSON Relational Duality View for AI applications
        CREATE OR REPLACE JSON RELATIONAL DUALITY VIEW documents_dv AS
        SELECT JSON {
            '_id': d.doc_id,
            'title': d.title,
            'content': d.content,
            'category': d.category,
            'publishDate': d.publish_date,
            'embedding': d.embedding,
            'metadata': {
                'wordCount': LENGTH(d.content) - LENGTH(REPLACE(d.content, ' ', '')) + 1,
                'createdAt': d.created_at
            }
        }
        FROM documents d
        WITH INSERT UPDATE DELETE;
        
        -- Query the duality view as JSON document
        SELECT * FROM documents_dv 
        WHERE JSON_VALUE(data, '$.category') = 'technology';
    """,
    
    "vector_with_window_functions": """
        -- Use window functions with vector operations
        SELECT 
            doc_id,
            title,
            category,
            VECTOR_DISTANCE(embedding, :query_vector, COSINE) as similarity,
            -- Rank within category
            RANK() OVER (
                PARTITION BY category 
                ORDER BY VECTOR_DISTANCE(embedding, :query_vector, COSINE)
            ) as category_rank,
            -- Overall percentile
            PERCENT_RANK() OVER (
                ORDER BY VECTOR_DISTANCE(embedding, :query_vector, COSINE)
            ) as similarity_percentile,
            -- Top 3 most similar in each category
            ROW_NUMBER() OVER (
                PARTITION BY category 
                ORDER BY VECTOR_DISTANCE(embedding, :query_vector, COSINE)
            ) as rn
        FROM documents
        QUALIFY rn <= 3;  -- Oracle 23ai feature: QUALIFY clause
    """,
    
    "vector_normalization": """
        -- Vector normalization and operations
        SELECT 
            doc_id,
            title,
            -- Normalize vector to unit length
            VECTOR_NORM(embedding) as vector_magnitude,
            -- Serialize vector for storage/transmission
            VECTOR_SERIALIZE(embedding) as serialized_embedding
        FROM documents
        WHERE doc_id = :doc_id;
        
        -- Deserialize and insert vector
        INSERT INTO documents (title, content, embedding)
        VALUES (
            :title,
            :content,
            VECTOR_DESERIALIZE(:serialized_vector)
        );
    """,
    
    "semantic_clustering": """
        -- Find clusters of similar documents
        WITH document_pairs AS (
            SELECT 
                d1.doc_id as doc1_id,
                d1.title as doc1_title,
                d2.doc_id as doc2_id,
                d2.title as doc2_title,
                VECTOR_DISTANCE(d1.embedding, d2.embedding, COSINE) as similarity
            FROM documents d1
            CROSS JOIN documents d2
            WHERE d1.doc_id < d2.doc_id  -- Avoid duplicates and self-joins
                AND VECTOR_DISTANCE(d1.embedding, d2.embedding, COSINE) < 0.2
        )
        SELECT 
            doc1_id,
            doc1_title,
            COUNT(*) as similar_docs_count,
            LISTAGG(doc2_title, ', ') WITHIN GROUP (ORDER BY similarity) as similar_titles
        FROM document_pairs
        GROUP BY doc1_id, doc1_title
        HAVING COUNT(*) >= 3
        ORDER BY similar_docs_count DESC;
    """,
    
    "rag_context_retrieval": """
        -- RAG pattern: Retrieve relevant context for LLM prompt
        WITH relevant_chunks AS (
            SELECT 
                doc_id,
                title,
                content,
                VECTOR_DISTANCE(embedding, :query_vector, COSINE) as relevance_score,
                -- Calculate chunk size for context window management
                LENGTH(content) as chunk_size,
                -- Running total of chunk sizes
                SUM(LENGTH(content)) OVER (
                    ORDER BY VECTOR_DISTANCE(embedding, :query_vector, COSINE)
                ) as cumulative_size
            FROM documents
            WHERE VECTOR_DISTANCE(embedding, :query_vector, COSINE) < 0.4
            ORDER BY relevance_score
        )
        SELECT 
            doc_id,
            title,
            content,
            relevance_score,
            chunk_size
        FROM relevant_chunks
        WHERE cumulative_size <= :max_context_tokens  -- e.g., 4000 tokens
        ORDER BY relevance_score;
    """,
    
    "multi_vector_search": """
        -- Search across multiple vector types (multi-modal)
        SELECT 
            m.media_id,
            m.title,
            m.description,
            -- Text embedding similarity
            VECTOR_DISTANCE(m.text_embedding, :text_query_vector, COSINE) as text_similarity,
            -- Image embedding similarity
            VECTOR_DISTANCE(m.image_embedding, :image_query_vector, COSINE) as image_similarity,
            -- Combined multi-modal score
            (0.6 * VECTOR_DISTANCE(m.text_embedding, :text_query_vector, COSINE) +
             0.4 * VECTOR_DISTANCE(m.image_embedding, :image_query_vector, COSINE)) as combined_score
        FROM multi_modal_content m
        ORDER BY combined_score
        FETCH FIRST 10 ROWS ONLY;
    """,
    
    "vector_batch_operations": """
        -- Batch vector operations for performance
        -- Using FORALL for bulk inserts
        DECLARE
            TYPE vector_array IS TABLE OF VECTOR(1536, FLOAT32);
            TYPE title_array IS TABLE OF VARCHAR2(200);
            
            l_vectors vector_array;
            l_titles title_array;
        BEGIN
            -- Assume vectors and titles are populated
            l_vectors := vector_array(...);
            l_titles := title_array(...);
            
            FORALL i IN 1..l_vectors.COUNT
                INSERT INTO documents (title, embedding)
                VALUES (l_titles(i), l_vectors(i));
            
            COMMIT;
        END;
    """,
    
    "similarity_threshold_query": """
        -- Find documents above similarity threshold with re-ranking
        WITH initial_candidates AS (
            SELECT 
                doc_id,
                title,
                content,
                embedding,
                VECTOR_DISTANCE(embedding, :query_vector, COSINE) as vector_score
            FROM documents
            WHERE VECTOR_DISTANCE(embedding, :query_vector, COSINE) < 0.5
            FETCH FIRST 100 ROWS ONLY  -- Initial candidates
        ),
        reranked AS (
            SELECT 
                doc_id,
                title,
                content,
                vector_score,
                -- Re-rank using additional features
                CASE 
                    WHEN UPPER(content) LIKE '%' || UPPER(:keyword) || '%' THEN 0.1
                    ELSE 0
                END as keyword_boost,
                -- Recency boost
                CASE 
                    WHEN created_at > SYSDATE - 30 THEN 0.05
                    ELSE 0
                END as recency_boost
            FROM initial_candidates
        )
        SELECT 
            doc_id,
            title,
            SUBSTR(content, 1, 200) as preview,
            vector_score,
            (vector_score - keyword_boost - recency_boost) as final_score
        FROM reranked
        ORDER BY final_score
        FETCH FIRST 10 ROWS ONLY;
    """
}


# PL/SQL procedures for AI operations
AI_PLSQL_PROCEDURES = {
    "vector_search_procedure": """
        CREATE OR REPLACE PROCEDURE semantic_search_docs(
            p_query_vector IN VECTOR,
            p_category IN VARCHAR2 DEFAULT NULL,
            p_limit IN NUMBER DEFAULT 10,
            p_results OUT SYS_REFCURSOR
        ) AS
        BEGIN
            OPEN p_results FOR
                SELECT 
                    doc_id,
                    title,
                    content,
                    VECTOR_DISTANCE(embedding, p_query_vector, COSINE) as similarity
                FROM documents
                WHERE (p_category IS NULL OR category = p_category)
                ORDER BY VECTOR_DISTANCE(embedding, p_query_vector, COSINE)
                FETCH FIRST p_limit ROWS ONLY;
        END;
    """,
    
    "embedding_generation_function": """
        CREATE OR REPLACE FUNCTION generate_embedding(
            p_text IN CLOB,
            p_model IN VARCHAR2 DEFAULT 'all-MiniLM-L6-v2'
        ) RETURN VECTOR
        IS
            l_embedding VECTOR(384, FLOAT32);
        BEGIN
            -- In practice, this would call an external embedding service
            -- Using DBMS_VECTOR or external API
            
            -- Placeholder: Actual implementation would use OCI AI or external service
            -- Example using DBMS_CLOUD for OCI integration:
            -- l_embedding := DBMS_CLOUD.get_embedding(p_text, p_model);
            
            RETURN l_embedding;
        END;
    """,
    
    "batch_embedding_update": """
        CREATE OR REPLACE PROCEDURE update_document_embeddings(
            p_batch_size IN NUMBER DEFAULT 100
        ) AS
            CURSOR doc_cursor IS
                SELECT doc_id, content
                FROM documents
                WHERE embedding IS NULL
                FETCH FIRST p_batch_size ROWS ONLY;
            
            TYPE doc_array IS TABLE OF doc_cursor%ROWTYPE;
            l_docs doc_array;
        BEGIN
            OPEN doc_cursor;
            FETCH doc_cursor BULK COLLECT INTO l_docs;
            CLOSE doc_cursor;
            
            FOR i IN 1..l_docs.COUNT LOOP
                -- Generate and update embedding
                UPDATE documents
                SET embedding = generate_embedding(l_docs(i).content)
                WHERE doc_id = l_docs(i).doc_id;
            END LOOP;
            
            COMMIT;
        END;
    """
}


def print_ai_query_examples():
    """Print all AI-specific SQL query examples"""
    print("Oracle Database 23ai/26ai - AI-Specific SQL Queries")
    print("=" * 80)
    
    for query_name, query in AI_SQL_QUERIES.items():
        print(f"\n{query_name.upper().replace('_', ' ')}")
        print("-" * 80)
        print(query.strip())
        print()


if __name__ == "__main__":
    print_ai_query_examples()
