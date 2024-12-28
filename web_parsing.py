#
# """
# This module provides search functionality across various search engines and databases.
# """
# import re
# import os
# from loguru import logger
# from scholarly import scholarly
# from duckduckgo_search import DDGS
# from metapub import PubMedFetcher
# from duckduckgo_search.exceptions import RatelimitException
# import time
# import llm
# import web_parsing
# from config import GOOGLE_API_URL, TIME_SLEEPING, BING_API_LINK, PUBMED_LINK_API
#
#
# def search_information(search_engine, question, question_keywords, num_results):
#     """Handle search across multiple search engines and databases.
#
#     Args:
#         search_engine (str): The identifier for the search engine (e.g., "1" for Google).
#         question (str): The full query for general-purpose search engines.
#         question_keywords (str): Keywords for specific databases like PubMed or Google Scholar.
#         num_results (int): Number of results to retrieve.
#
#     Returns:
#         tuple: A tuple containing aggregated text, articles (dict), and parsed links.
#     """
#     search_functions = {
#         "1": search_google,
#         "2": search_duckduckgo,
#         "3": search_bing,
#         "4": search_brave,
#         "5": search_scholar_links,
#         "6": search_pub_med,
#     }
#
#     search_func = search_functions.get(search_engine)
#     if not search_func:
#         logger.error("Not available search engine")
#         return "", [], []
#
#     if search_engine in ["1", "2", "3", "4"]:
#         return search_func(question, num_results)
#     return search_func(question_keywords, num_results)
#
#
# def extract_links(response, items, query):
#     """
#     Extract links from search engine responses.
#
#     Args:
#         response (Response): The response object from the search engine.
#         items (list): List of search result items.
#         query (str): The original search query.
#
#     Returns:
#         tuple: A tuple containing parsed links and corresponding metadata.
#     """
#     if not response:
#         logger.warning(f"No response from Google for query: {query}")
#         return "", [], []
#
#     if not items:
#         logger.warning(f"No search results returned for query: {query}")
#         return "", [], []
#
#     links = [item['link'] for item in items]
#     return web_parsing.links_parsing(links, query)
#
#
# def search_google(query, num_results):
#     """
#     Perform a search using the Google Custom Search API.
#
#     Args:
#         query (str): The search query.
#         num_results (int): The number of results to retrieve.
#
#     Returns:
#         tuple: A tuple containing parsed links and corresponding metadata.
#     """
#     params = {
#         'q': query,
#         'key': os.environ['GOOGLE_KEY'],
#         'cx': os.environ['GOOGLE_TOKEN'],
#         'num': num_results
#     }
#     response = web_parsing.get_request(GOOGLE_API_URL, params=params)
#     items = response.json().get('items', [])
#     return extract_links(response, items, query)
#
#
# def search_duckduckgo(query, num_results):
#     """
#     Perform a search using DuckDuckGo.
#
#     Args:
#         query (str): The search query.
#         num_results (int): The number of results to retrieve.
#
#     Returns:
#         tuple: A tuple containing parsed links and corresponding metadata.
#     """
#     try:
#         results = DDGS().text(query, max_results=int(num_results))
#     except RatelimitException as e:
#         logger.warning(f"Ratelimit hit: {e}. Retrying ...")
#         time.sleep(TIME_SLEEPING)
#         results = DDGS().text("your search query", max_results=int(num_results))
#
#     links = [result['href'] for result in results]
#     return web_parsing.links_parsing(links, query)
#
#
# def search_bing(query, num_results):
#     """
#     Perform a search using the Bing Search API.
#
#     Args:
#         query (str): The search query.
#         num_results (int): The number of results to retrieve.
#
#     Returns:
#         tuple: A tuple containing parsed links and corresponding metadata.
#     """
#     params = {'q': query, 'mkt': 'en-US', 'count': num_results}
#     subscription_key = os.getenv('BING_SEARCH_V7_SUBSCRIPTION_KEY')
#     headers = {'Ocp-Apim-Subscription-Key': subscription_key}
#     endpoint = os.getenv('BING_SEARCH_V7_ENDPOINT') + "/v7.0/search"
#     response = web_parsing.get_request(endpoint, params=params, headers=headers)
#     items = response.json().get('webPages', {}).get('value', [])
#     return extract_links(response, items, query)
#
#
# def search_brave(query, num):
#     """
#     Perform a search using the Brave Search API.
#
#     Args:
#         query (str): The search query.
#         num (int): The number of results to retrieve.
#
#     Returns:
#         tuple: A tuple containing parsed links and corresponding metadata.
#     """
#     headers = {
#         "Accept": "application/json",
#         "Accept-Encoding": "gzip",
#         "X-Subscription-Token": os.environ['BING_TOKEN']
#     }
#     response = web_parsing.get_request(BING_API_LINK, headers=headers, params={"q": query})
#     items = response.json()['web']['results'][:num]
#     return extract_links(response, items, query)
#
#
# def get_data_from_scholar(result):
#     """
#     Extract data from a Google Scholar result.
#
#     Args:
#         result (dict): The result item from Google Scholar.
#
#     Returns:
#         tuple: A tuple containing the abstract, title, year, link, and author information.
#     """
#     abstract = result['bib'].get('abstract', 'No abstract available')
#     title = result['bib'].get('title', 'No title available')
#     year = find_year_of_publication(result, title, abstract)
#     link = result.get('pub_url', None)
#     author = result['bib'].get('author', '')
#     return abstract, title, year, link, author
#
#
# def process_doc(query, links, articles, all_text, abstract, title, year, link, author):
#     """
#     Process and filter document content based on relevance.
#
#     Args:
#         query (str): The search query.
#         links (list): A list of parsed links.
#         articles (dict): Articles metadata.
#         all_text (str): Aggregated text from the documents.
#         abstract (str): Abstract of the document.
#         title (str): Title of the document.
#         year (str): Year of publication.
#         link (str): URL of the document.
#         author (str): Author information.
#
#     Returns:
#         tuple: Updated links, articles, and all_text.
#     """
#     relativity = llm.gemini_relative(llm.gemini_config(), abstract, query)
#     if "YES" in relativity:
#         links.append(link)
#         articles = web_parsing.create_articles(articles, title, link,
#                                                abstract, year,
#                                                author)
#         all_text += f"Content from [{link}]:\n{abstract}\n{'-' * 34}\n"
#     return links, articles, all_text
#
#
# def search_scholar_links(query, num_results):
#     """
#     Perform a search using Google Scholar.
#
#     Args:
#         query (str): The search query.
#         num_results (int): The number of results to retrieve.
#
#     Returns:
#         tuple: A tuple containing aggregated text, articles (dict), and parsed links.
#     """
#     articles, links, all_text = [], [], ""
#     count = 0
#     for result in scholarly.search_pubs(query):
#         count += 1
#         if count > num_results:
#             break
#         abstract, title, year, link, author = get_data_from_scholar(result)
#         links, articles, all_text = process_doc(query, links, articles, all_text,
#                                                 abstract, title, year, link, author)
#     links = web_parsing.parsing_doc_db(articles)
#     return all_text, articles, links
#
#
# def find_year_of_publication(result, title, abstract):
#     """
#     Find the year of publication from the document metadata.
#
#     Args:
#         result (dict): The result item from the search.
#         title (str): The title of the document.
#         abstract (str): The abstract of the document.
#
#     Returns:
#         str: The year of publication, if found; otherwise an empty string.
#     """
#     if 'pub_year' in result:
#         return result.get('pub_year', 'No year available')
#     elif 'date' in result:
#         return result.get('date', 'No year available')
#     possible_year = re.search(r'\b(19|20)\d{2}\b', title + " " + abstract)
#     return possible_year.group(0) if possible_year else 'No year available'
#
#
# def search_pub_med(query, num_results):
#     """
#     Perform a search using PubMed.
#
#     Args:
#         query (str): The search query.
#         num_results (int): The number of results to retrieve.
#
#     Returns:
#         tuple: A tuple containing aggregated text, articles (dict), and parsed links.
#     """
#     articles, links, all_text = [], [], ""
#     fetch = PubMedFetcher()
#     for doc in fetch.pmids_for_query(query, retmax=num_results):
#         article = fetch.article_by_pmid(doc)
#         link = f"{PUBMED_LINK_API}{doc}/"
#         links, articles, all_text = process_doc(query, links, articles, all_text,
#                                                 article.abstract, article.title,
#                                                 article.year, link, article.author)
#     links = web_parsing.parsing_doc_db(articles)
#     return all_text, articles, links
#
#
"""
This module provides functions for scraping web content, parsing data, and creating article summaries.
"""
from loguru import logger
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import llm
import requests
import time
from config import config, USER_AGENT, MIN_TEXT_LENGTH, HTML_TAGS, TIMEOUT, TIME_SLEEPING


def scrape_with_playwright(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=USER_AGENT)
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(TIMEOUT * 100)  # Wait 3 seconds to mimic human actions
            content = page.content()
            browser.close()
            return content
    except Exception as e:
        logger.error(f"Error during Playwright scraping: {e}")
        return ""


def parsing_doc_db(results):
    return [r['link'] for r in results]


def create_articles(articles, title, link, abstract, year, author):
    """
    Append article information to the list of articles.

    Args:
        articles (List[Dict]): Existing list of articles.
        title (str): Title of the article.
        link (str): URL of the article.
        abstract (str): Abstract or summary of the article.
        year (str): Publication year.
        author (str): Author of the article.

    Returns:
        List[Dict]: Updated list of articles.
    """
    articles.append({
        "title": title,
        "link": link,
        "abstract": abstract,
        "year": year,
        "author": author
    })
    return articles


def links_parsing(links, question):
    all_text, articles, relative_links = "", [], []
    model = llm.gemini_config()
    for link in links:
        logger.info("Process " + link)
        new_text = parsing_web_page(model, link)
        if not new_text:
            continue

        if "YES" in llm.gemini_relative(model, new_text, question):
            logger.info(f"Relevant content found for link: {link}")
            relative_links.append(link)
            summ = llm.gemini_summ(model, new_text)
            articles = create_articles(articles, link, link, summ, '', '')
            all_text += new_text
    return all_text, articles, relative_links


def parsing_web_page(model, url):
    response = get_request(url, headers={"User-Agent": USER_AGENT})
    if response.status_code == config['http_status_codes']['success_request_ok']:
        html = response.text
    else:
        logger.warning(f"Failed to retrieve {url} try playwright")
        html = scrape_with_playwright(url)

    if not html:
        logger.error(f"Failed to retrieve content for {url}")
        return f"Error: Unable to fetch content from {url}\n"

    elements = BeautifulSoup(html, 'html.parser').find_all(HTML_TAGS)
    accumulated_text = ""

    for element in elements:
        text = element.get_text(strip=True)
        if len(text) > MIN_TEXT_LENGTH:
            accumulated_text += text

    if accumulated_text:
        summarization = llm.gemini_clean(llm.gemini_config(), accumulated_text)
        if summarization:
            return (f"Content from [{url}]: \n{summarization}\n"
                    f"------------------------------\n")
    return f"No sufficient content found on {url}\n"


def get_request(url, params=None, headers=None, retries=3):
    """Helper function to handle HTTP requests with retry logic."""
    logger.info("Get request")
    try:
        response = requests.get(url, params=params, headers=headers, timeout=config['timeout_time'])
        response.raise_for_status()  # Raises an HTTPError for bad responses
        logger.info("Get response")
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for {url} with error: {e}")
        if retries > 0:
            time.sleep(TIME_SLEEPING)
            return get_request(url, params, headers, retries - 1)
        logger.error(f"Max retries reached for {url}")
        return None
