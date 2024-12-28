"""
This module processes uploaded files.
"""
import os
from loguru import logger
from werkzeug.utils import secure_filename
import PyPDF2
import llm
from config import config, ALLOWED_EXTENSIONS


def allowed_file(filename):
    """
    Check if a given file has an allowed extension.

    Args:
        filename (str): The name of the file to check.

    Returns:
        bool: True if the file extension is allowed, False otherwise.
    """
    return ('.' in filename and
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS)


def process_txt(file_path):
    """
    Read and process the content of a text file.

    Args:
        file_path (str): The path to the text file.

    Returns:
        str: The content of the text file as a string.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        file_content = f.read()
    return file_content


def process_pdf(file_path):
    """
    Extract and process the content of a PDF file.

    Args:
        file_path (str): The path to the PDF file.

    Returns:
        str: The extracted text from the PDF as a string.
    """
    file_content = ""
    with open(file_path, 'rb') as f:
        pdf_reader = PyPDF2.PdfReader(f)
        for page in pdf_reader.pages:
            file_content += page.extract_text()
    return file_content


def process_file(file, file_name, file_path):
    """
    Process an uploaded file by reading its content and generating a summary.

    Args:
        file (werkzeug.datastructures.FileStorage): The uploaded file object.
        file_name (str): The name of the file.
        file_path (str): The path where the file will be saved temporarily.

    Returns:
        dict: A dictionary containing the file name and its summarized content.
    """
    filename = secure_filename(file_name)
    file.save(file_path)
    file_extension = filename.rsplit('.', 1)[1].lower()
    file_content = ""
    if file_extension == 'txt':
        file_content = process_txt(file_path)
    elif file_extension == 'pdf':
        file_content = process_pdf(file_path)

    summary = llm.gemini_summ(llm.gemini_config(), file_content)
    return {"file_name": file_name, "file_content": summary}


def remove_file_from_system(file_path):
    """
    Remove a file from the filesystem if it exists.

    Args:
        file_path (str): The path to the file to be removed.
    """
    if os.path.exists(file_path):
        os.remove(file_path)


def get_file(files, file_dir):
    """
    Process multiple uploaded files, generate summaries, and remove temporary files.

    Args:
        files (tuples): A list of key-value pairs where the key is a string and
                                the value is a `FileStorage` object representing an uploaded file.
        file_dir (str): The directory path where files will be temporarily saved.

    Returns:
        tuple: A list of dictionaries with file names and summaries, and an HTTP status code.
    """
    processed_files = []
    for key in files:
        file = files[key]
        file_name = file.filename
        logger.info(f"Processing file: {file_name}")
        file_path = ""

        if not file_name:
            logger.warning(f"No file provided for key: {key}")
            return key, config['http_status_codes']['bad_request']

        if not allowed_file(file_name):
            logger.warning(f"File {file_name} has an unsupported extension.")
            return file_name, config['http_status_codes']['bad_request']

        try:
            file_path = os.path.join(file_dir, file_name)
            logger.info(f"Processed {file_name}")
            processed_files.append(process_file(file, file_name, file_path))
        except Exception as e:
            logger.warning(f"Failed to process file {file_name}: {e}")
            return file_name, config['http_status_codes']['internal_server_error']
        finally:
            remove_file_from_system(file_path)

    logger.info(f"Successfully processed {len(processed_files)} files.")
    return processed_files, config['http_status_codes']['success_request_ok']
