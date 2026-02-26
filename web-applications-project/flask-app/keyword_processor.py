from flask import Flask, request, jsonify

# Initial Setup - load keywords from the file and provide an in-memory storage
def load_keywords(filename='keywords.txt'):
    try:
        with open(filename, 'r') as file:
            return {line.strip().lower() for line in file}
    except FileNotFoundError:
        return set()

def save_keyword(keyword, filename='keywords.txt'):
    with open(filename, 'a') as file:
        file.write(f'{keyword.lower()}\n')

app = Flask(__name__)
keywords = load_keywords()

@app.route('/process', methods=['POST'])
def process_text():
    content = request.json.get('text', '')
    if not content:
        return jsonify({"error": "No text provided"}), 400
    processed_content = process_and_add_hashtags(content)
    return jsonify({"original": content, "processed": processed_content})

@app.route('/keyword', methods=['POST'])
def add_new_keyword():
    new_keyword = request.json.get('keyword', '')
    if not new_keyword:
        return jsonify({"error": "No keyword provided"}), 400
    if new_keyword.lower() not in keywords:
        keywords.add(new_keyword.lower())
        save_keyword(new_keyword)
        return jsonify({"message": f"Keyword '{new_keyword}' added successfully."})
    else:
        return jsonify({"message": f"Keyword '{new_keyword}' is already in the list."})

def process_and_add_hashtags(content):
    words = content.split()
    processed_words = []
    for word in words:
        clean_word = word.lower().strip(".,!?:;")
        if clean_word.startswith('#') and clean_word[1:] not in keywords:
            add_keyword(clean_word[1:])  # Add without the hash
            processed_words.append(word)
        elif clean_word in keywords:
            processed_words.append(f'#{word}')
        else:
            processed_words.append(word)
    return ' '.join(processed_words)

def add_keyword(new_keyword):
    new_keyword = new_keyword.lower().strip(".,!?:;")
    if new_keyword not in keywords:
        keywords.add(new_keyword)
        save_keyword(new_keyword)

if __name__ == '__main__':
    app.run(debug=True)
