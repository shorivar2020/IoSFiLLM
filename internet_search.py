import re
import os
import requests
from loguru import logger
from scholarly import scholarly
from duckduckgo_search import DDGS
from metapub import PubMedFetcher
import llm
import parsing


def search_information(search_engine, question, question_keywords, num_results):
    """Handle search across multiple search engines and databases.

    Args:
        search_engine (str): The identifier for the search engine (e.g., "1" for Google).
        question (str): The full query for general-purpose search engines.
        question_keywords (str): Keywords for specific databases like PubMed or Google Scholar.
        num_results (int): Number of results to retrieve.

    Returns:
        tuple: A tuple containing aggregated text, articles (dict), and parsed links.
    """
    search_functions = {
        "1": search_google,
        "2": search_duckduckgo,
        "3": search_bing,
        "4": search_brave,
        "5": search_scholar_links,
        "6": search_pub_med,
    }

    search_func = search_functions.get(search_engine)
    if not search_func:
        logger.error("Not available search engine")
        return "", [], []

    if search_engine in ["1", "2", "3", "4"]:
        return search_func(question, num_results)
    return search_func(question_keywords, num_results)


def get_request(api_link, params, headers):
    """
    Perform an HTTP GET request to the specified API endpoint.

    Args:
        api_link (str): The API endpoint URL to send the request to.
        params (dict): Query parameters to include in the GET request.
        headers (dict): Headers to include in the GET request.

    Returns:
        dict or str: The JSON response from the API as a dictionary if the request is successful.
                     Returns an empty string if the request fails.
    """
    try:
        response = requests.get(api_link, params=params, headers=headers)
        logger.info(f"Response status: {response.status_code}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        return ""


def search_google(query, num_results):
    """
    Perform a search using the Google Custom Search API.

    Args:
        query (str): The search query.
        num_results (int): The number of results to retrieve.

    Returns:
        tuple: A tuple containing parsed links and corresponding metadata.
    """
    google_api_link = 'https://www.googleapis.com/customsearch/v1'

    params = {
        'q': query,
        'key': os.environ['GOOGLE_KEY'],
        'cx': os.environ['GOOGLE_TOKEN'],
        'num': num_results
    }
    response = get_request(google_api_link, params, {})
    if response:
        items = response['items']
        links = [item['link'] for item in items]
        return parsing.links_parsing(links, query)
    return ""


def search_duckduckgo(query, num_results):
    """
    Perform a search using DuckDuckGo.

    Args:
        query (str): The search query.
        num_results (int): The number of results to retrieve.

    Returns:
        tuple: A tuple containing parsed links and corresponding metadata.
    """
    items = DDGS().text(query, max_results=num_results)
    links = [item['href'] for item in items]
    return parsing.links_parsing(links, query)


def search_bing(query, num_results):
    """
    Perform a search using the Bing Search API.

    Args:
        query (str): The search query.
        num_results (int): The number of results to retrieve.

    Returns:
        tuple: A tuple containing parsed links and corresponding metadata.
    """
    subscription_key = os.environ['BING_SEARCH_V7_SUBSCRIPTION_KEY']
    endpoint = os.environ['BING_SEARCH_V7_ENDPOINT'] + "/v7.0/search"
    mkt = 'en-US'
    params = {'q': query, 'mkt': mkt, 'count': num_results}
    headers = {'Ocp-Apim-Subscription-Key': subscription_key}
    response = get_request(endpoint, params, headers)
    if response:
        items = response.get('webPages', {}).get('value', [])
        links = [item['url'] for item in items]
        return parsing.links_parsing(links, query)
    return ""


def search_brave(query, num_results):
    """
    Perform a search using the Brave Search API.

    Args:
        query (str): The search query.
        num_results (int): The number of results to retrieve.

    Returns:
        tuple: A tuple containing parsed links and corresponding metadata.
    """
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": os.environ['BRAVE_TOKEN']
    }
    params = {"q": query}
    response = get_request(url, params, headers)
    if response:
        items = response['web']['results'][:num_results]
        links = [item['url'] for item in items]
        return parsing.links_parsing(links, query)
    return ""


def search_scholar_links(query, num_results):
    """
    Perform a search using Google Scholar.

    Args:
        query (str): The search query.
        num_results (int): The number of results to retrieve.

    Returns:
        tuple: A tuple containing aggregated text, articles (dict), and parsed links.
    """
    results = scholarly.search_pubs(query)
    articles = []
    links = []
    count = 0
    all_text = ""

    for result in results:
        count += 1
        if count > num_results:
            break

        # Extract article details
        title = result['bib'].get('title', 'No title available')
        abstract = result['bib'].get('abstract', 'No abstract available')
        # Extract year
        year = (
            result.get('pub_year') or
            result.get('date') or
            re.search(r'\b(19|20)\d{2}\b', title + " " + abstract).group(0) if re.search(r'\b(19|20)\d{2}\b',                                                                                     title + " " + abstract) else 'No year available'
        )
        author = result['bib'].get('author', '')
        link = result.get('pub_url', None)
        # Process the data
        all_text, articles, links = process_database_data(articles, links, all_text, abstract, query, title, link, year, author)

    return all_text, articles, links


def search_pub_med(query, num_results):
    """
    Perform a search using PubMed.

    Args:
        query (str): The search query.
        num_results (int): The number of results to retrieve.

    Returns:
        tuple: A tuple containing aggregated text, articles (dict), and parsed links.
    """
    fetch = PubMedFetcher()
    pmids = fetch.pmids_for_query(query, retmax=num_results)
    articles = []
    links = []
    all_text = ""

    for pmid in pmids:
        # Fetch article details
        title = fetch.article_by_pmid(pmid).title
        abstract = fetch.article_by_pmid(pmid).abstract
        author = fetch.article_by_pmid(pmid).authors
        year = fetch.article_by_pmid(pmid).year
        link = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

        # Process the data
        all_text, articles, links = process_database_data(articles, links, all_text, abstract, query, title, link, year, author)

    return all_text, articles, links


def process_database_data(articles, links, all_text, abstract, query, title, link, year, author):
    """
    Processes database data and appends relevant information to articles, links, and all_text.

    This function evaluates the relevance of a given abstract using the LLM Gemini's relative matching mechanism.
    If the abstract is relevant, it appends the title, link, abstract, year, and author to the `articles` list,
    the link to the `links` list, and the abstract content to the `all_text` string.

    Parameters:
        articles (list): A list to store dictionaries with article metadata.
        links (list): A list to store URLs of relevant articles.
        all_text (str): A string to accumulate the content of all relevant abstracts.
        abstract (str): The abstract of the article to be evaluated.
        query (str): The query string to evaluate the relevance of the abstract.
        title (str): The title of the article.
        link (str): The URL of the article.
        year (int): The publication year of the article.
        author (str): The author of the article.

    Returns:
        tuple: A tuple containing:
            - all_text (str): The updated content of all relevant abstracts.
            - articles (list): The updated list of dictionaries with article metadata.
            - links (list): The updated list of URLs of relevant articles.
    """
    if "YES" in llm.gemini_relative(llm.gemini_config(), abstract, query):
        articles.append({
            "title": title,
            "link": link,
            "abstract": abstract,
            "year": year,
            "author": author
        })
        accumulated_text = (
            f"Content from [{link}]: \n{abstract}\n"
            "----------------------------------------------------------\n"
        )
        links.append(link)
        all_text += accumulated_text
    return all_text, articles, links

