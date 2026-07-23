from typing import AsyncGenerator, List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.schema import HumanMessage

from app.core.config import settings

_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)


def chunk_text(text: str) -> List[str]:
    """Split text into overlapping chunks for embedding."""
    return _splitter.split_text(text)


def get_embeddings(chunks: List[str]) -> List[List[float]]:
    """Generate embeddings for a list of text chunks."""
    embeddings_model = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
    return embeddings_model.embed_documents(chunks)


async def stream_summary(text: str, prompt: str = "") -> AsyncGenerator[str, None]:
    """Stream an LLM summary of the given text, token by token."""
    llm = ChatOpenAI(
        api_key=settings.OPENAI_API_KEY,
        model="gpt-4o-mini",
        streaming=True,
    )
    user_prompt = prompt or "Summarize this document concisely:"
    message = HumanMessage(content=f"{user_prompt}\n\n{text[:4000]}")
    async for chunk in llm.astream([message]):
        if chunk.content:
            yield chunk.content
