"""
Vector Search Example using Oracle Database 23ai

This example demonstrates:
1. Connecting to Oracle Database 23ai
2. Creating tables with VECTOR columns
3. Generating and storing embeddings
4. Performing semantic similarity searches
5. Optimizing vector queries with indexes
"""

import numpy as np
from typing import List, Tuple
import json


class VectorSearchExample:
    """
    Demonstrates vector search capabilities in Oracle Database 23ai
    
    Note: This is a teaching example. In production, use actual Oracle
    connection libraries like python-oracledb.
    """
    
    def __init__(self, connection_string: str = None):
        """
        Initialize vector search example
        
        Args:
            connection_string: Oracle database connection string
        """
        self.connection_string = connection_string or "oracle://user:pass@localhost:1521/FREEPDB1"
        self.embedding_dimension = 384  # Example: all-MiniLM-L6-v2 dimension
        
    def create_vector_table(self) -> str:
        """
        Create a table with VECTOR column for storing embeddings
        
        Returns:
            SQL CREATE TABLE statement
        """
        sql = f"""
        CREATE TABLE IF NOT EXISTS knowledge_base (
            kb_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            title VARCHAR2(500),
            content CLOB,
            source VARCHAR2(200),
            embedding VECTOR({self.embedding_dimension}, FLOAT32),
            metadata JSON,
            created_at TIMESTAMP DEFAULT SYSTIMESTAMP
        )
        """
        return sql
    
    def create_vector_index(self) -> str:
        """
        Create a vector index for fast similarity search
        
        Returns:
            SQL CREATE INDEX statement
        """
        sql = """
        CREATE VECTOR INDEX idx_kb_vector ON knowledge_base(embedding)
        ORGANIZATION INMEMORY NEIGHBOR GRAPH
        DISTANCE COSINE
        WITH TARGET ACCURACY 95
        """
        return sql
    
    def generate_mock_embedding(self, text: str) -> List[float]:
        """
        Generate a mock embedding for demonstration
        
        In production, use actual embedding models like:
        - sentence-transformers
        - OpenAI embeddings API
        - Cohere embeddings API
        - OCI Generative AI embeddings
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        # Mock embedding: In reality, use actual embedding model
        # For demo purposes, create a deterministic vector based on text
        np.random.seed(hash(text) % (2**32))
        embedding = np.random.randn(self.embedding_dimension).tolist()
        
        # Normalize to unit length (important for cosine similarity)
        magnitude = np.linalg.norm(embedding)
        normalized = [x / magnitude for x in embedding]
        
        return normalized
    
    def insert_document_with_embedding(
        self, 
        title: str, 
        content: str, 
        source: str
    ) -> str:
        """
        Insert a document with its vector embedding
        
        Args:
            title: Document title
            content: Document content
            source: Document source
            
        Returns:
            SQL INSERT statement
        """
        embedding = self.generate_mock_embedding(content)
        
        # Convert Python list to Oracle VECTOR format
        vector_str = f"[{','.join(map(str, embedding))}]"
        
        sql = f"""
        INSERT INTO knowledge_base (title, content, source, embedding, metadata)
        VALUES (
            '{title}',
            '{content}',
            '{source}',
            TO_VECTOR('{vector_str}', {self.embedding_dimension}, FLOAT32),
            JSON('{{"word_count": {len(content.split())}}}')
        )
        """
        return sql
    
    def semantic_search(
        self, 
        query: str, 
        top_k: int = 5,
        similarity_threshold: float = 0.5
    ) -> str:
        """
        Perform semantic similarity search
        
        Args:
            query: Search query text
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score (0-2 for cosine)
            
        Returns:
            SQL SELECT statement for similarity search
        """
        query_embedding = self.generate_mock_embedding(query)
        vector_str = f"[{','.join(map(str, query_embedding))}]"
        
        sql = f"""
        SELECT 
            kb_id,
            title,
            SUBSTR(content, 1, 200) as content_preview,
            source,
            VECTOR_DISTANCE(
                embedding, 
                TO_VECTOR('{vector_str}', {self.embedding_dimension}, FLOAT32),
                COSINE
            ) as similarity_score
        FROM knowledge_base
        WHERE VECTOR_DISTANCE(
            embedding,
            TO_VECTOR('{vector_str}', {self.embedding_dimension}, FLOAT32),
            COSINE
        ) < {similarity_threshold}
        ORDER BY similarity_score
        FETCH FIRST {top_k} ROWS ONLY
        """
        return sql
    
    def hybrid_search(
        self,
        query: str,
        keyword: str = None,
        source_filter: str = None,
        top_k: int = 10
    ) -> str:
        """
        Hybrid search combining vector similarity and traditional filters
        
        Args:
            query: Semantic search query
            keyword: Optional keyword for full-text search
            source_filter: Optional source filter
            top_k: Number of results
            
        Returns:
            SQL query combining vector and traditional search
        """
        query_embedding = self.generate_mock_embedding(query)
        vector_str = f"[{','.join(map(str, query_embedding))}]"
        
        where_clauses = []
        if keyword:
            where_clauses.append(f"UPPER(content) LIKE '%{keyword.upper()}%'")
        if source_filter:
            where_clauses.append(f"source = '{source_filter}'")
        
        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        sql = f"""
        WITH ranked_results AS (
            SELECT 
                kb_id,
                title,
                content,
                source,
                VECTOR_DISTANCE(
                    embedding,
                    TO_VECTOR('{vector_str}', {self.embedding_dimension}, FLOAT32),
                    COSINE
                ) as vector_score,
                -- Keyword match boost
                CASE 
                    WHEN UPPER(content) LIKE '%{keyword.upper()}%' THEN 0.1
                    ELSE 0
                END as keyword_boost
            FROM knowledge_base
            WHERE {where_clause}
        )
        SELECT 
            kb_id,
            title,
            SUBSTR(content, 1, 300) as preview,
            source,
            vector_score,
            (vector_score - keyword_boost) as final_score
        FROM ranked_results
        ORDER BY final_score
        FETCH FIRST {top_k} ROWS ONLY
        """
        return sql
    
    def find_similar_documents(self, doc_id: int, top_k: int = 5) -> str:
        """
        Find documents similar to a given document
        
        Args:
            doc_id: ID of the reference document
            top_k: Number of similar documents to find
            
        Returns:
            SQL query to find similar documents
        """
        sql = f"""
        WITH reference_doc AS (
            SELECT embedding
            FROM knowledge_base
            WHERE kb_id = {doc_id}
        )
        SELECT 
            kb.kb_id,
            kb.title,
            kb.source,
            VECTOR_DISTANCE(kb.embedding, ref.embedding, COSINE) as similarity
        FROM knowledge_base kb
        CROSS JOIN reference_doc ref
        WHERE kb.kb_id != {doc_id}
        ORDER BY similarity
        FETCH FIRST {top_k} ROWS ONLY
        """
        return sql
    
    def clustering_analysis(self, max_distance: float = 0.3) -> str:
        """
        Perform clustering analysis to find groups of similar documents
        
        Args:
            max_distance: Maximum distance for documents to be in same cluster
            
        Returns:
            SQL query for clustering analysis
        """
        sql = f"""
        WITH document_pairs AS (
            SELECT 
                d1.kb_id as doc1_id,
                d1.title as doc1_title,
                d2.kb_id as doc2_id,
                d2.title as doc2_title,
                VECTOR_DISTANCE(d1.embedding, d2.embedding, COSINE) as distance
            FROM knowledge_base d1
            CROSS JOIN knowledge_base d2
            WHERE d1.kb_id < d2.kb_id
                AND VECTOR_DISTANCE(d1.embedding, d2.embedding, COSINE) < {max_distance}
        )
        SELECT 
            doc1_id,
            doc1_title,
            COUNT(*) as cluster_size,
            ROUND(AVG(distance), 4) as avg_distance,
            LISTAGG(doc2_title, '; ') WITHIN GROUP (ORDER BY distance) as similar_docs
        FROM document_pairs
        GROUP BY doc1_id, doc1_title
        HAVING COUNT(*) >= 2
        ORDER BY cluster_size DESC, avg_distance
        """
        return sql


def demo_vector_search():
    """
    Demonstration of vector search operations
    """
    print("Oracle Database 23ai - Vector Search Example")
    print("=" * 80)
    
    # Initialize vector search
    vs = VectorSearchExample()
    
    # Step 1: Create table
    print("\n1. CREATE TABLE WITH VECTOR COLUMN")
    print("-" * 80)
    print(vs.create_vector_table())
    
    # Step 2: Create index
    print("\n2. CREATE VECTOR INDEX")
    print("-" * 80)
    print(vs.create_vector_index())
    
    # Step 3: Insert sample documents
    print("\n3. INSERT DOCUMENTS WITH EMBEDDINGS")
    print("-" * 80)
    
    sample_docs = [
        ("Introduction to AI", "Artificial Intelligence is transforming technology", "AI Book"),
        ("Machine Learning Basics", "ML algorithms learn patterns from data", "ML Guide"),
        ("Oracle Database Features", "Oracle 23ai introduces vector search capabilities", "Oracle Docs"),
    ]
    
    for title, content, source in sample_docs:
        print(f"\nInserting: {title}")
        print(vs.insert_document_with_embedding(title, content, source)[:200] + "...")
    
    # Step 4: Semantic search
    print("\n4. SEMANTIC SEARCH")
    print("-" * 80)
    query = "artificial intelligence and machine learning"
    print(f"Query: '{query}'")
    print(vs.semantic_search(query, top_k=3))
    
    # Step 5: Hybrid search
    print("\n5. HYBRID SEARCH (Vector + Keyword)")
    print("-" * 80)
    print(vs.hybrid_search(query, keyword="Oracle", top_k=5))
    
    # Step 6: Find similar documents
    print("\n6. FIND SIMILAR DOCUMENTS")
    print("-" * 80)
    print(vs.find_similar_documents(doc_id=1, top_k=3))
    
    # Step 7: Clustering
    print("\n7. CLUSTERING ANALYSIS")
    print("-" * 80)
    print(vs.clustering_analysis(max_distance=0.3))
    
    print("\n" + "=" * 80)
    print("Vector search demonstration complete!")
    print("\nIn production:")
    print("- Use actual embedding models (sentence-transformers, OpenAI, Cohere)")
    print("- Connect to real Oracle Database 23ai instance")
    print("- Handle errors and edge cases")
    print("- Optimize vector dimensions and index parameters")
    print("- Implement caching and batch processing")


if __name__ == "__main__":
    demo_vector_search()
