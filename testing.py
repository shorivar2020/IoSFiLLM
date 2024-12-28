import pytest
from loguru import logger
from processor import process_query


def log_results(query, search_engine, num_results, file_content):
    """Helper function to log results for debugging."""
    r, urls, a, ai = process_query(query, search_engine, num_results, file_content)
    print("Query: " + query)
    for i, url in enumerate(urls):
        print("Link " + url)
        print("Article " + str(a[i]))
    print("Response " + r)
    print("AI Answer " + ai)
    return r, urls, a, ai


@pytest.mark.parametrize("query, search_engine, num_results, file_content", [
    ("Can you find similar articles to Happy ending programme?", "1", 10, ""),
    ("Can you find similar articles to Happy ending programme?", "2", 10, ""),
    ("Can you find similar articles to Happy ending programme?", "3", 10, ""),
])
def test_process_query(query, search_engine, num_results, file_content):
    try:
        r, urls, a, ai = process_query(query, search_engine, num_results, file_content)
        assert isinstance(r, str), "Response should be a string."
        assert isinstance(urls, list), "URLs should be a list."
        assert isinstance(a, list), "Articles should be a list."
        assert isinstance(ai, str), "AI Answer should be a string."
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        raise

