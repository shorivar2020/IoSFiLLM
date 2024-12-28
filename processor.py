"""
This module processes and handles text queries, document uploads.
"""
from loguru import logger
import llm
import preprocess_text
import internet_search
from config import config


def write_context_to_file(context):
    """
    Writes the provided context information to a specified file.

    Args:
        context (str): The context content to be saved to a file.
    """
    with open(config['files_information']['name'],
              "w", encoding="utf-8") as file:
        file.write(context)


def file_content_process(file_content, articles, context):
    """
    Processes the content of an uploaded file, appending it to the list of articles if it meets a minimum length.

    Args:
        file_content (tuple): A tuple where the first element is the content of the file.
        articles (list): List of existing articles to append the new content to.
        context (str): Accumulated text from previous documents and articles.

    Returns:
        tuple: Updated list of articles and the accumulated text.
    """
    if len(file_content) > config['files_information']['min_length']:
        logger.info("Add file content")
        file = (f"Content from uploaded file: \n{file_content}\n"
                f"--------------------------------------\n")
        articles.append({
            "title": "Uploaded content",
            "link": '',
            "abstract": file,
            "year": '',
            "author": ''
        })
        context += file
    return articles, context


def process_query(query, search_engine, num_results, file_content):
    """
    Processes a query, searches for relevant information, and combines it with uploaded file content.

    Args:
        query (str): The user's query to be processed.
        search_engine (str): The search engine to use for gathering information.
        num_results (int): The number of search results to retrieve.
        file_content (tuple): The content of an uploaded file to be appended (if present).

    Returns:
        tuple: The response generated by the LLM, a list of links, the articles, and the generated answer.
    """
    question_keywords = query  # Use short query as keywords
    if len(query.split()) > config['query_information']['max_length']:
        logger.info("Question too long, start preprocessing query")
        question, question_keywords = preprocess_text.prepare_query(query)
    logger.info("Start searching " + query)
    context, articles, links = internet_search.search_information(search_engine, query, question_keywords, int(num_results))
    logger.info("Create context")
    if file_content:
        articles, context = file_content_process(file_content[0], articles, context)
    write_context_to_file(context)  # Save context to file for debugging
    logger.info("Get responses")
    return llm.gemini(query, context), links, articles, llm.gemini_answer(query)


if __name__ == "__main__":
    r, urls, a, ai = process_query('Can you find similar articles to Happy ending programme?', "1", 10, "")
    for i in range(len(urls)):
        logger.info("Link " + urls[i])
        logger.info("Article " + str(a[i]))
    logger.info("Response " + r)
    logger.info("AI Answer " + ai)
