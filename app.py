from flask import Flask, request, jsonify
from flask_cors import CORS
from controller import *

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "https://localhost:8080"}})


@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/api/check', methods=['POST'])
def check_question():
    data = request.json
    question = data.get('question', '').lower()
    search_engine = data.get('searchEngine', 1)
    ai_engine = data.get('aiEngine', 1)
    db = data.get('db', 1)
    print("Received question:", question)
    print("Search engine selected:", search_engine)
    print("AI engine selected:", ai_engine)
    answer, source, ai_answer, doc_links = controller(question, search_engine, db, ai_engine)
    return jsonify({"answer": answer, "source": source, "ai_answer": ai_answer, "doc_links": doc_links})


if __name__ == '__main__':
    print("Start app")
    app.run(host='0.0.0.0', port=8080, debug=False)
