import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# -------------------- Flight Data Fetching --------------------
def fetch_flights(bbox=None):
    url = "https://opensky-network.org/api/states/all"
    params = {}
    if bbox:
        params["lamin"], params["lamax"], params["lomin"], params["lomax"] = bbox
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


# -------------------- AI Assistant via Ollama --------------------
def ask_ollama(question, context):
    prompt = f"Flight data:\n{context}\n\nQuestion: {question}\nAnswer:"
    resp = requests.post("http://localhost:11434/api/generate", json={
        "model": "llama2",
        "prompt": prompt,
        "stream": False
    })
    return resp.json().get("response", "No answer.")


# -------------------- REST API Endpoint --------------------
@app.route("/api/aviation/ask", methods=["POST"])
def aviation_ask():
    if request.is_json:
        data = request.get_json()
        question = data.get("question", "")
    else:
        question = request.data.decode() or ""
    flights = fetch_flights()
    # You can format/truncate context as needed; here we use all
    context = str(flights)[:2500]
    answer = ask_ollama(question, context)
    return jsonify({"answer": answer})


# -------------------- Web UI --------------------
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>Flight Tracker AI</title>
<style>
body { font-family: Arial, sans-serif; margin: 2em; }
input, button { font-size: 1.2em; }
pre { background: #f4f4f4; padding: 1em; }
</style>
</head>
<body>
<h1>Flight Tracker AI Assistant</h1>
<input id="question" type="text" placeholder="Ask about flights..." size="50"/>
<button onclick="ask()">Ask</button>
<pre id="answer"></pre>
<script>
function ask() {
    fetch("/api/aviation/ask", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({question: document.getElementById('question').value})
    })
    .then(r => r.json()).then(data => {
        document.getElementById('answer').innerText = data.answer
    });
}
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

# -------------------- (Optional) Rate Limiting --------------------
# from flask_limiter import Limiter
# limiter = Limiter(app, key_func=lambda: request.remote_addr)
# @app.route("/api/aviation/ask", methods=["POST"])
# @limiter.limit("5 per minute")
# def aviation_ask():
#     ...

# -------------------- Main Entry --------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
