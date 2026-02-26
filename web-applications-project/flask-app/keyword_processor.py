from flask import Flask, request, jsonify

# Initial Setup - load keywords from the file and provide an in-memory storage
def load_keywords(filename='keywords.txt'):
    """Load keywords from a plain-text file into a set.

    Reads each line of *filename*, strips whitespace, and lowercases the
    value before adding it to the set.  If the file does not exist an empty
    set is returned so the application can start without pre-existing data.

    Args:
        filename (str): Path to the keywords file. Defaults to
            ``'keywords.txt'``.

    Returns:
        set[str]: Set of lowercase keyword strings loaded from the file.
    """
    try:
        with open(filename, 'r') as file:
            return {line.strip().lower() for line in file}
    except FileNotFoundError:
        return set()

def save_keyword(keyword, filename='keywords.txt'):
    """Append a single keyword to the persistent keywords file.

    The keyword is lowercased before being written so the file stays
    consistently cased.

    Args:
        keyword (str): The keyword to persist.
        filename (str): Path to the keywords file. Defaults to
            ``'keywords.txt'``.
    """
    with open(filename, 'a') as file:
        file.write(f'{keyword.lower()}\n')

app = Flask(__name__)
keywords = load_keywords()

@app.route('/process', methods=['POST'])
def process_text():
    """Process submitted text and prepend ``#`` to recognised keywords.

    Expects a JSON body with a ``"text"`` field.  Each word in the text is
    checked against the in-memory keyword set; matching words are prefixed
    with a hash symbol to turn them into hashtags.

    Returns:
        JSON response with keys ``"original"`` (the input text) and
        ``"processed"`` (the hashtag-enhanced text), or a 400 error if no
        text was provided.
    """
    content = request.json.get('text', '')
    if not content:
        return jsonify({"error": "No text provided"}), 400
    processed_content = process_and_add_hashtags(content)
    return jsonify({"original": content, "processed": processed_content})

@app.route('/keyword', methods=['POST'])
def add_new_keyword():
    """Add a new keyword to the in-memory set and persist it to disk.

    Expects a JSON body with a ``"keyword"`` field.  The keyword is
    lowercased and deduplicated before being stored.

    Returns:
        JSON response confirming addition or indicating the keyword already
        exists.  Returns a 400 error if no keyword was provided.
    """
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
    """Scan *content* and prefix known keywords with ``#``.

    For each word in the content:
    - If the word already starts with ``#`` and the bare word is not yet a
      keyword, it is added to the keyword set automatically.
    - If the bare word (lowercased, punctuation stripped) is a known keyword,
      it is prefixed with ``#``.
    - Otherwise the word is left unchanged.

    Args:
        content (str): The input text to process.

    Returns:
        str: The processed text with hashtags applied to keyword matches.
    """
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
    """Add *new_keyword* to the in-memory set and persist it if not already present.

    Strips common punctuation and lowercases the value before storage to
    ensure consistent matching.

    Args:
        new_keyword (str): The keyword to add.
    """
    new_keyword = new_keyword.lower().strip(".,!?:;")
    if new_keyword not in keywords:
        keywords.add(new_keyword)
        save_keyword(new_keyword)

if __name__ == '__main__':
    app.run(debug=True)
