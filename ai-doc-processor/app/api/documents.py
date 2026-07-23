import json
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse

from app.workers.celery_app import process_document_task

router = APIRouter()


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Accept a document and enqueue it for ETL processing. Returns a task ID."""
    contents = await file.read()
    task = process_document_task.delay(file.filename, contents)
    return {"task_id": task.id, "filename": file.filename}


@router.post("/process-stream")
async def process_document_stream(file: UploadFile = File(...), prompt: str = Form("")):
    """Upload a document and stream LLM output token-by-token via SSE."""
    contents = await file.read()

    async def event_generator():
        yield f"data: {json.dumps({'status': 'extracting'})}\n\n"

        from app.etl.extract import extract_text
        text = extract_text(contents, file.filename)
        yield f"data: {json.dumps({'status': 'transforming'})}\n\n"

        from app.etl.transform import stream_summary
        async for token in stream_summary(text, prompt):
            yield f"data: {json.dumps({'token': token})}\n\n"

        yield f"data: {json.dumps({'status': 'complete'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """Poll Celery task status by ID."""
    from celery.result import AsyncResult
    result = AsyncResult(task_id)
    return {"task_id": task_id, "status": result.status, "result": result.result}
