"""
PyDiagram — System Architecture Diagram
========================================

Generates a production-infrastructure view of the Yelp-Style AI Assistant
using the `diagrams` library (https://diagrams.mingrammer.com/).

Run directly to render a PNG:
    python -m diagrams.pydiagram.architecture

Or call `build()` programmatically to construct the graph object without
saving/showing it (useful in tests).
"""

from __future__ import annotations

import os
from typing import Optional


def build(filename: str = "yelp_ai_architecture", output_dir: str = ".", show: bool = False) -> None:
    """
    Construct and render the system architecture diagram.

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
    from diagrams.onprem.monitoring import Prometheus, Grafana
    from diagrams.onprem.queue import Kafka
    from diagrams.onprem.database import MongoDB   # stand-in for FAISS/Pinecone (custom below)
    from diagrams.aws.ml import Sagemaker           # stand-in for LLM / RAG service

    out_path = os.path.join(output_dir, filename)

    graph_attr = {
        "fontsize": "13",
        "bgcolor": "white",
        "pad": "0.5",
        "splines": "ortho",
    }

    with Diagram(
        "Yelp-Style AI Assistant — Production Architecture",
        filename=out_path,
        show=show,
        direction="LR",
        graph_attr=graph_attr,
        outformat="png",
    ):
        user = User("Client (100k+ users)")

        with Cluster("API Layer"):
            gateway = Server("API Gateway\n(Nginx / Kong)")
            api = Server("Query Service\n(FastAPI / uvicorn)")
            cache = Redis("Redis Cache\n(L1 LRU + L2 TTL)")

        with Cluster("Processing"):
            classifier = Server("Intent Classifier\n(< 20 ms)")
            router = Server("Query Router")

        with Cluster("Search Services"):
            structured = PostgreSQL("Structured Search\n(PG + ES)")
            vector = MongoDB("Review Vector\nSearch (FAISS)")
            photo = Server("Photo Hybrid\nRetrieval (CLIP)")

        with Cluster("Orchestration & RAG"):
            orchestrator = Server("Answer Orchestrator\n(conflict resolution)")
            llm = Sagemaker("RAG / LLM\n(OpenAI / local)")

        with Cluster("Data Stores"):
            pg = PostgreSQL("PostgreSQL\n(authoritative)")
            kafka = Kafka("Kafka\n(CDC events)")
            vector_db = MongoDB("Vector DB\n(FAISS / Pinecone)")

        with Cluster("Observability"):
            prom = Prometheus("Prometheus")
            graf = Grafana("Grafana")

        # Main request flow
        user >> gateway >> api
        api >> cache
        api >> classifier >> router
        router >> structured >> orchestrator
        router >> vector >> orchestrator
        router >> photo >> orchestrator
        orchestrator >> llm >> api

        # Data store connections
        structured >> pg
        vector >> vector_db
        photo >> vector_db

        # Ingestion
        kafka >> structured
        kafka >> vector

        # Observability
        api >> prom >> graf


if __name__ == "__main__":
    import sys
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    build(output_dir=out_dir, show=False)
    print(f"Architecture diagram written to {os.path.join(out_dir, 'yelp_ai_architecture.png')}")
