from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "ai_doc_processor",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(bind=True, max_retries=3)
def process_document_task(self, filename: str, contents: bytes):
    """ETL pipeline: Extract → Transform → Load for a single document."""
    try:
        from app.etl.extract import extract_text
        from app.etl.transform import chunk_text, get_embeddings

        text = extract_text(contents, filename)
        chunks = chunk_text(text)
        embeddings = get_embeddings(chunks)

        # TODO: persist via load.load_document with a real DB session
        return {"filename": filename, "chunks": len(chunks), "status": "complete"}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)
