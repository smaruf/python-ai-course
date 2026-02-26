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
    return hashlib.sha256(prompt.encode()).hexdigest()

def get_cache(key):
    cursor.execute("SELECT response FROM cache WHERE prompt_hash=?", (key,))
    row = cursor.fetchone()
    return row[0] if row else None

def set_cache(key, value):
    cursor.execute("INSERT OR REPLACE INTO cache VALUES (?,?)", (key, value))
    conn.commit()

def cloud_available():
    return time.time() > cloud_disabled_until

def register_failure():
    global cloud_failures, cloud_disabled_until
    cloud_failures += 1
    if cloud_failures >= FAIL_THRESHOLD:
        cloud_disabled_until = time.time() + COOLDOWN_SECONDS
        cloud_failures = 0

def register_success():
    global cloud_failures
    cloud_failures = 0

# =========================
# EMBEDDING RAG
# =========================
doc_embeddings = []
doc_texts = []

def load_docs():
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
    def do_POST(self):
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
