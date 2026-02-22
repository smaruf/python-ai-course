"""
PyDiagram — Data Flow Diagram
===============================

Generates a data-flow view showing how information moves through the
Yelp-Style AI Assistant: from ingestion through search, orchestration,
and back to the user.

Run directly to render a PNG:
    python -m diagrams.pydiagram.data_flow

Or call `build()` programmatically (useful in tests).
"""

from __future__ import annotations

import os


def build(filename: str = "yelp_ai_data_flow", output_dir: str = ".", show: bool = False) -> None:
    """
    Construct and render the data flow diagram.

    Parameters
    ----------
    filename   : output file base name (no extension)
    output_dir : directory where the PNG will be written
    show       : open the rendered image automatically (default False)
    """
    from diagrams import Cluster, Diagram, Edge
    from diagrams.onprem.client import User
    from diagrams.onprem.compute import Server
    from diagrams.onprem.database import PostgreSQL
    from diagrams.onprem.inmemory import Redis
    from diagrams.onprem.queue import Kafka
    from diagrams.onprem.database import MongoDB   # stand-in for Vector DB
    from diagrams.aws.ml import Sagemaker           # stand-in for LLM

    out_path = os.path.join(output_dir, filename)

    graph_attr = {
        "fontsize": "12",
        "bgcolor": "white",
        "pad": "0.6",
        "splines": "curved",
        "rankdir": "TB",
    }

    with Diagram(
        "Yelp-Style AI Assistant — Data Flow",
        filename=out_path,
        show=show,
        direction="TB",
        graph_attr=graph_attr,
        outformat="png",
    ):
        user = User("User Query")

        with Cluster("Freshness: Streaming (< 10 min)"):
            kafka = Kafka("Kafka CDC\n(reviews / hours)")
            stream = Server("Stream Processor\n+ Embedder")

        with Cluster("Freshness: Batch (weekly)"):
            etl = Server("Batch ETL")

        with Cluster("Storage — Structured (authoritative)"):
            pg = PostgreSQL("PostgreSQL\nbusinesses / hours")

        with Cluster("Storage — Unstructured"):
            vector_db = MongoDB("Vector DB\n(review embeddings)")
            es = PostgreSQL("Elasticsearch\n(review text + captions)")

        with Cluster("Query Pipeline"):
            cache = Redis("Redis Cache\n(L1 LRU + L2 TTL)")
            api = Server("Query Service")
            classifier = Server("Intent\nClassifier")
            router = Server("Query Router")

        with Cluster("Search (parallel, 40–80 ms each)"):
            structured_svc = PostgreSQL("Structured Search")
            review_svc = MongoDB("Review Vector\nSearch")
            photo_svc = Server("Photo Hybrid\nRetrieval")

        with Cluster("Answer Generation"):
            orchestrator = Server("Answer\nOrchestrator")
            llm = Sagemaker("RAG / LLM\n(300–800 ms)")

        # Streaming ingestion path (left side)
        kafka >> stream
        stream >> Edge(label="upsert") >> vector_db
        stream >> Edge(label="upsert") >> es
        stream >> Edge(label="invalidate") >> cache
        etl >> es

        # Authoritative source feeds structured search
        pg >> structured_svc

        # Query path (right side, top to bottom)
        user >> api
        api >> cache
        api >> classifier >> router

        router >> structured_svc
        router >> review_svc
        router >> photo_svc

        review_svc >> vector_db
        review_svc >> es
        photo_svc >> es

        structured_svc >> orchestrator
        review_svc >> orchestrator
        photo_svc >> orchestrator

        orchestrator >> llm >> api


if __name__ == "__main__":
    import sys
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    build(output_dir=out_dir, show=False)
    print(f"Data flow diagram written to {os.path.join(out_dir, 'yelp_ai_data_flow.png')}")
