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
def upload_files():
    if 'file_0' not in request.files:
        return jsonify({"error": "No files provided"}), 400

    files = request.files  # Получить все файлы из запроса
    processed_files = []  # Для хранения информации о каждом обработанном файле
    logger.info("files")
    for key in files:
        file = files[key]
        file_name = file.filename
        logger.info("file with name " + file_name)
        if file_name == '':
            return jsonify({"error": f"File {key} has no name"}), 400

        if file and allowed_file(file_name):
            try:
                filename = secure_filename(file_name)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                file_extension = filename.rsplit('.', 1)[1].lower()
                file_content = ""

                if file_extension == 'txt':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()

                elif file_extension == 'pdf':
                    with open(file_path, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        for page in pdf_reader.pages:
                            file_content += page.extract_text()

                summary = process_download_document(file_content)

                processed_files.append({
                    "file_name": file_name,
                    "file_content": summary
                })
                logger.info(f"Processed {file_name}")

            except Exception as e:
                return jsonify({"error": f"Failed to process file {file_name}: {str(e)}"}), 500
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)
        else:
            return jsonify({"error": f"File type not allowed for {file_name}"}), 400
    logger.info(f"Processed {len(processed_files)} files")
    return jsonify({
        "files_name": [file["file_name"] for file in processed_files],
        "files_content": [file["file_content"] for file in processed_files]
    }), 200


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
    num_results = int(data.get('resultNumber', 1))
    logger.info("Received question: ", question)
    logger.info("Search engine selected: ", search_engine)
    logger.info("File content: ", file_content)
    logger.info("Num results: ", num_results)
    answer, source, articles, ai_answer = controller(question, search_engine, num_results, file_content)
    return jsonify({"answer": answer, "source": source, "ai_answer": ai_answer, "articles": articles})


if __name__ == '__main__':
    print("Start app")
    app.run(host='0.0.0.0', port=8080, debug=False)
