from typing import List
from sqlalchemy.orm import Session

from app.db.models import Document, DocumentChunk
from app.etl.transform import chunk_text, get_embeddings


def load_document(db: Session, user_id: int, filename: str, text: str) -> Document:
    """Persist a document and its vector embeddings to PostgreSQL + PGVector."""
    doc = Document(user_id=user_id, filename=filename, status="processing")
    db.add(doc)
    db.flush()

    chunks = chunk_text(text)
    embeddings = get_embeddings(chunks)

    for chunk_text_val, embedding in zip(chunks, embeddings):
        chunk = DocumentChunk(
            document_id=doc.id,
            content=chunk_text_val,
            embedding=embedding,
        )
        db.add(chunk)

    doc.status = "complete"
    db.commit()
    db.refresh(doc)
    return doc
