from flask import Flask, request, jsonify
from flask_cors import CORS
import controller
from controller import *
from werkzeug.utils import secure_filename
import os
import PyPDF2

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config['UPLOAD_FOLDER'] = 'uploads/'
ALLOWED_EXTENSIONS = {'txt', 'pdf'}


def allowed_file(filename):
    """Check if the uploaded file is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/download', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        file_extension = filename.rsplit('.', 1)[1].lower()
        file_content = ""

        # Read and return the content of the text file
        try:
            if file_extension == 'txt':
                # Read text file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()

            elif file_extension == 'pdf':
                # Read PDF file content
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        file_content += page.extract_text()
            summ = process_download_document(file_content)
            return jsonify({"file_content": summ}), 200
        except Exception as e:
            return jsonify({"error": f"Failed to process file: {str(e)}"}), 500

    return jsonify({"error": "File type not allowed"}), 400


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
    file_content = data.get('fileContent', '')
    print("Received question:", question)
    print("Search engine selected:", search_engine)
    print("File content:", file_content)
    num_results = 10
    answer, source, articles, ai_answer = controller(question, search_engine, num_results, file_content)
    return jsonify({"answer": answer, "source": source, "ai_answer": ai_answer, "articles": articles})


if __name__ == '__main__':
    print("Start app")
    app.run(host='0.0.0.0', port=8080, debug=False)
