import scoring
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def hello_world():
    return jsonify(message="Hello, World!")


# Score text using FinBERT model
@app.route('/score_text', methods=['POST'])
def score_text():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'must provide text_content'}), 400
    
    text_content = data.get('text_content')

    if not text_content:
         return jsonify({'error': 'must provide text_content'}), 400
    
    score_tensor, magnitude = scoring.process_chunk(text_content)
    return jsonify({"score": score_tensor.item(), "magnitude": magnitude})


if __name__ == "__main__":
    app.run(debug=True)