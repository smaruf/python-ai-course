"""
AI Edge — Lightweight Standalone AI Server with Caching and RAG
===============================================================

A self-contained, single-file AI server that runs as either an HTTP service
or an interactive CLI.  It provides a subset of the functionality found in
``ai_gateway.py`` (FastAPI / multi-file) but requires no additional framework
beyond the Python standard library.

Routing priority (2-tier + cache):

    ┌─────────┐    hit     ┌─────────────────────────┐
    │  prompt │──────────► │  SQLite response cache  │ ──► return cached
    └────┬────┘            └─────────────────────────┘
         │ miss
         ▼
    RAG context-injection (embedding similarity over ./docs/*.txt)
         │
         ▼
    ┌──────────────────┐  failure / circuit open
    │  Cloud (OpenAI)  │──────────────────────────►  Local Ollama (fallback)
    │   (primary)      │                             (tertiary / offline)
    └──────────────────┘

GitHub Copilot is the **primary** AI tool for developing and extending this
codebase (see ``ai_gateway.py`` and ``copilot_client.py``).  ``ai_edge.py``
itself uses OpenAI as its cloud tier; integrate ``CopilotClient`` as the
first tier when a GitHub Copilot token is available.

Modes:
    Server (default)::

        python ai_edge.py
        # Listens on http://0.0.0.0:8080
        # POST {"prompt": "..."} to receive {"source": "...", "response": "..."}

    CLI::

        python ai_edge.py cli

Configuration (environment variables):

    ``OPENAI_API_KEY``   OpenAI API key used for the cloud tier.

Dependencies:
    sentence-transformers, requests, numpy
"""

import os
import time
import json
import hashlib
import sqlite3
import requests
import numpy as np
from http.server import BaseHTTPRequestHandler, HTTPServer
from sentence_transformers import SentenceTransformer

# =========================
# CONFIG
# =========================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PORT = 8080
CLOUD_TIMEOUT = 3
FAIL_THRESHOLD = 3
COOLDOWN_SECONDS = 300
LOCAL_MODEL = "phi3:mini"
DOC_FOLDER = "./docs"
DB_FILE = "ai_cache.db"

# =========================
# STATE
# =========================
cloud_failures = 0
cloud_disabled_until = 0
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# =========================
# SQLITE CACHE
# =========================
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS cache (
    prompt_hash TEXT PRIMARY KEY,
    response TEXT
)
""")
conn.commit()

# =========================
# UTIL
# =========================
def hash_prompt(prompt):
    """Return the SHA-256 hex digest of *prompt*.

    Used as the cache key so that identical prompts always resolve to the
    same lookup value regardless of their length.

    Args:
        prompt (str): The raw prompt string to hash.

    Returns:
        str: 64-character lowercase hexadecimal SHA-256 digest.
    """
    return hashlib.sha256(prompt.encode()).hexdigest()

def get_cache(key):
    """Retrieve a cached AI response by its prompt hash.

    Args:
        key (str): SHA-256 hex digest of the original prompt (see
            :func:`hash_prompt`).

    Returns:
        str | None: The previously stored response string, or ``None`` if no
        entry exists for *key*.
    """
    cursor.execute("SELECT response FROM cache WHERE prompt_hash=?", (key,))
    row = cursor.fetchone()
    return row[0] if row else None

def set_cache(key, value):
    """Persist an AI response in the SQLite cache.

    Uses ``INSERT OR REPLACE`` so that a repeated prompt always reflects the
    most recent response.

    Args:
        key (str): SHA-256 hex digest of the original prompt.
        value (str): The AI response text to store.
    """
    cursor.execute("INSERT OR REPLACE INTO cache VALUES (?,?)", (key, value))
    conn.commit()

def cloud_available():
    """Return whether the cloud tier is currently available.

    The cloud tier is disabled for ``COOLDOWN_SECONDS`` after accumulating
    ``FAIL_THRESHOLD`` consecutive failures.  This simple time-based circuit
    breaker prevents hammering a degraded endpoint.

    Returns:
        bool: ``True`` if the cooldown period has elapsed (or was never
        triggered), ``False`` if the cloud tier is still in cooldown.
    """
    return time.time() > cloud_disabled_until

def register_failure():
    """Record a cloud-tier failure and open the circuit if the threshold is reached.

    Increments the global ``cloud_failures`` counter.  When the counter
    reaches ``FAIL_THRESHOLD`` the cloud tier is disabled until
    ``time.time() + COOLDOWN_SECONDS``, and the counter is reset.
    """
    global cloud_failures, cloud_disabled_until
    cloud_failures += 1
    if cloud_failures >= FAIL_THRESHOLD:
        cloud_disabled_until = time.time() + COOLDOWN_SECONDS
        cloud_failures = 0

def register_success():
    """Reset the cloud-tier failure counter after a successful request.

    Clears ``cloud_failures`` so that a single successful call stops the
    circuit from opening, even if previous calls failed.
    """
    global cloud_failures
    cloud_failures = 0

# =========================
# EMBEDDING RAG
# =========================
doc_embeddings = []
doc_texts = []

def load_docs():
    """Load all ``.txt`` documents from ``DOC_FOLDER`` and compute their embeddings.

    Walks the ``DOC_FOLDER`` directory (``./docs`` by default), reads every
    ``.txt`` file and appends the raw text to :data:`doc_texts` and its
    sentence-transformer embedding vector to :data:`doc_embeddings`.

    If ``DOC_FOLDER`` does not exist the function returns silently so the
    server can start even without pre-loaded documents.
    """
    if not os.path.exists(DOC_FOLDER):
        return

    for file in os.listdir(DOC_FOLDER):
        if file.endswith(".txt"):
            with open(os.path.join(DOC_FOLDER, file), "r", encoding="utf-8") as f:
                text = f.read()
                doc_texts.append(text)
                doc_embeddings.append(embedding_model.encode(text))

load_docs()

def search_docs(prompt):
    """Find the most relevant loaded document for *prompt* using cosine similarity.

    Encodes *prompt* with the same sentence-transformer model used during
    :func:`load_docs`, computes dot-product similarity against every stored
    document embedding, and returns up to the first 2 000 characters of the
    best-matching document.

    Args:
        prompt (str): The user query to search against the document store.

    Returns:
        str: The first 2 000 characters of the most relevant document, or an
        empty string if no documents have been loaded.
    """
    if not doc_embeddings:
        return ""

    query_emb = embedding_model.encode(prompt)
    sims = [np.dot(query_emb, emb) for emb in doc_embeddings]
    best_index = int(np.argmax(sims))
    return doc_texts[best_index][:2000]

# =========================
# CLOUD
# =========================
def ask_cloud(prompt):
    """Send *prompt* to the OpenAI Chat Completions API and return the response.

    This is the **primary** cloud tier of the edge server.  For a full
    3-tier setup (GitHub Copilot → Cloud → Local) use ``ai_gateway.py`` with
    ``copilot_client.py`` instead.

    Args:
        prompt (str): The user prompt to send.

    Returns:
        str: The model's text response from the ``gpt-4o-mini`` model.

    Raises:
        Exception: If the cloud circuit is currently open (cooldown active).
        requests.exceptions.HTTPError: If the API returns a non-2xx status.
    """
    if not cloud_available():
        raise Exception("Cloud disabled")

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}]
    }

    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=CLOUD_TIMEOUT
    )

    r.raise_for_status()
    register_success()
    return r.json()["choices"][0]["message"]["content"]

# =========================
# LOCAL
# =========================
def ask_local(prompt):
    """Send *prompt* to the locally-running Ollama instance and return the response.

    Used as the fallback (offline) tier when the cloud tier is unavailable or
    its circuit breaker is open.

    Args:
        prompt (str): The user prompt to send.

    Returns:
        str: The model's text response from the local ``LOCAL_MODEL``.

    Raises:
        requests.exceptions.ConnectionError: If Ollama is not running on
            ``http://localhost:11434``.
    """
    r = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": LOCAL_MODEL,
            "prompt": prompt,
            "stream": False
        }
    )
    return r.json()["response"]

# =========================
# ROUTER
# =========================
def ask_ai(prompt):
    """Route *prompt* through the cache → cloud → local fallback chain.

    Processing steps:

    1. **Cache lookup** — return immediately if an identical prompt was
       answered previously (keyed by SHA-256 hash).
    2. **RAG context injection** — if any documents are loaded, prepend the
       most relevant one to the prompt before querying the AI.
    3. **Cloud tier (primary)** — attempt :func:`ask_cloud`; on any
       exception, call :func:`register_failure` and fall through.
    4. **Local tier (fallback)** — call :func:`ask_local` when the cloud
       tier fails or its circuit is open.
    5. **Cache write** — persist the response so future identical prompts
       are served instantly.

    Args:
        prompt (str): The user's raw question or instruction.

    Returns:
        dict: A dictionary with two keys:

            ``"source"`` (str)
                Which tier answered: ``"cache"``, ``"cloud"``, or ``"local"``.

            ``"response"`` (str)
                The AI model's text response.
    """

    key = hash_prompt(prompt)
    cached = get_cache(key)
    if cached:
        return {"source": "cache", "response": cached}

    context = search_docs(prompt)
    if context:
        prompt = f"Context:\n{context}\n\nQuestion:\n{prompt}"

    try:
        response = ask_cloud(prompt)
        source = "cloud"
    except:
        register_failure()
        response = ask_local(prompt)
        source = "local"

    set_cache(key, response)
    return {"source": source, "response": response}

# =========================
# HTTP SERVER
# =========================
class Handler(BaseHTTPRequestHandler):
    """Minimal HTTP request handler for the AI Edge server.

    Accepts ``POST`` requests with a JSON body containing a ``"prompt"`` key
    and returns a JSON response produced by :func:`ask_ai`.

    Example request::

        curl -X POST http://localhost:8080 \\
             -H "Content-Type: application/json" \\
             -d '{"prompt": "What is the capital of France?"}'

    Example response::

        {"source": "cloud", "response": "The capital of France is Paris."}
    """

    def do_POST(self):
        """Handle an incoming POST request.

        Reads the full request body, parses it as JSON, passes the
        ``"prompt"`` field to :func:`ask_ai`, and writes the JSON-encoded
        result back to the client with a 200 status code.
        """
        length = int(self.headers["Content-Length"])
        body = self.rfile.read(length)
        data = json.loads(body)

        result = ask_ai(data.get("prompt", ""))

        output = json.dumps(result).encode()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(output)))
        self.end_headers()
        self.wfile.write(output)

# =========================
# CLI MODE
# =========================
def cli():
    """Run the AI Edge server in interactive CLI mode.

    Presents a read-eval-print loop that reads prompts from stdin, passes
    them to :func:`ask_ai`, and prints the source tier and response.

    Type ``exit`` (case-insensitive) to quit.

    Example session::

        AI EDGE CLI (type exit)

        You: What is 2 + 2?

        [cloud]
        2 + 2 equals 4.

        You: exit
    """
    print("AI EDGE CLI (type exit)")
    while True:
        prompt = input("\nYou: ")
        if prompt.lower() == "exit":
            break
        result = ask_ai(prompt)
        print(f"\n[{result['source']}]\n{result['response']}")

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        cli()
    else:
        print(f"AI Edge running on http://localhost:{PORT}")
        HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
