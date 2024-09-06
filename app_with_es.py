from flask import Flask, request, jsonify
from elasticsearch import Elasticsearch
from nltk.tokenize import word_tokenize
import nltk
nltk.download('punkt')

# Connect to local Elasticsearch server
es = Elasticsearch()

app = Flask(__name__)

# Create the index in Elasticsearch if it doesn't exist
def create_index(index_name='hashtags'):
    if not es.indices.exists(index_name):
        es.indices.create(index=index_name, ignore=400)  # 400 caused by IndexAlreadyExistsException, means index is already there

def add_keyword(keyword):
    es.index(index="hashtags", body={"keyword": keyword.lower()})

def get_keywords():
    result = es.search(index="hashtags", body={"query": {"match_all": {}}})
    return {hit['_source']['keyword'] for hit in result['hits']['hits']}

@app.route('/process', methods=['POST'])
def process_text():
    content = request.json.get('text', '')
    keywords = get_keywords()
    tokens = word_tokenize(content)
    processed_tokens = ['#' + token if token.lower() in keywords else token for token in tokens]
    processed_text = ' '.join(processed_tokens)
    return jsonify({"original": content, "processed": processed_text})

@app.route('/keyword', methods=['POST'])
def add_new_keyword():
    new_keyword = request.json.get('keyword', '').lower()
    if not new_keyword:
        return jsonify({"error": "No keyword provided"}), 400
    add_keyword(new_keyword)
    return jsonify({"message": f"Keyword '{new_keyword}' added successfully."})

if __name__ == '__main__':
    create_index()
    app.run(debug=True)
