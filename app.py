"""
This module start prototype of integration of search functionality into LLM.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from loguru import logger
import processor
import upload_file
from config import config, file_dir

# Initialize Flask application
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": config['cors']['origins']}})


@app.route('/api/download', methods=['POST'])
def upload_files():
    """
    Handle file uploads, validate, and process them.

    Returns:
        JSON: Response with file names and contents or error message.
    """
    files = request.files
    if 'file_0' not in files:
        logger.warning("No files provided in the request.")
        return (jsonify({"error": "No files provided"}),
                config['http_status_codes']['bad_request'])
    key, code = upload_file.get_file(files, file_dir)

    if code == config['http_status_codes']['success_request_ok']:
        return jsonify({
            "files_name": [file["file_name"] for file in key],
            "files_content": [file["file_content"] for file in key]
        }), config['http_status_codes']['success_request_ok']
    if code == config['http_status_codes']['bad_request']:
        logger.warning(f"File type not allowed for {key} or has no name.")
        return (jsonify({"error": f"File type not allowed for {key}"
                                  f" or has no name."}),
                config['http_status_codes']['bad_request'])
    logger.error(f"Failed to process file {key}.")
    return (jsonify({"error": f"Failed to process file {key}."}),
            config['http_status_codes']['internal_server_error'])


@app.after_request
def add_cors_headers(response):
    """
    Add CORS headers to the response.

    Args:
        response (Response): The HTTP response object.

    Returns:
        Response: The modified response object.
    """
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/api/check', methods=['POST'])
def check_question():
    """
    Handle incoming question requests, process them, and return an answer.

    Returns:
        JSON: The answer and related information, or error message.
    """
    data = request.json
    query = data.get('question', '').lower()
    search_engine = data.get('searchEngine', 1)
    file_content = data.get('fileContent', '')
    num_results = int(data.get('resultNumber', 1))

    if not query:
        logger.error("Question is required but missing.")
        return (jsonify({"error": "Question is required"}),
                config['http_status_codes']['bad_request'])
    if not search_engine:
        logger.error("Search engine is required but missing.")
        return (jsonify({"error": "Search engine must be an integer"}),
                config['http_status_codes']['bad_request'])
    if not isinstance(num_results, int) or num_results < 1:
        logger.error("Invalid number of results specified.")
        return (jsonify({"error": "Invalid number"}),
                config['http_status_codes']['bad_request'])

    logger.info("Received question: " + query)
    logger.info("Search engine selected: " + search_engine)
    logger.info(f"File content: {file_content}")
    logger.info(f"Num results: {num_results}")
    try:
        response, source, articles, ai_answer = (
            processor.process_query(query,
                                    search_engine,
                                    int(num_results),
                                    file_content))
        return jsonify({"answer": response,
                        "source": source,
                        "ai_answer": ai_answer,
                        "articles": articles})
    except Exception as e:
        logger.error(f"Error in processing question: {e}")
        return (jsonify({"error": "An error occurred"}),
                config['http_status_codes']['internal_server_error'])


if __name__ == '__main__':
    logger.info(f"Starting Flask application on {config['flask']['host']}:{config['flask']['port']}")
    app.run(
        host=config['flask']['host'],
        port=config['flask']['port'],
        debug=config['flask']['debug']
    )
