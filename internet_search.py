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


def search_google(query, num_results):
    params = {
        'q': query,
        'key': 'AIzaSyBQPjmZ7_93LnCwF0z9JSjiQF16Lrj9vPo',
        'cx': '466d5706bf5384c11',
        'num': num_results
    }
    response = requests.get('https://www.googleapis.com/customsearch/v1', params=params)
    if response.status_code != 200:
        logger.warning(f"API request failed with status {response.status_code}: {response.text}")
    items = response.json()['items']
    links = [item['link'] for item in items]
    return parsing.links_parsing(links, query)


def search_duckduckgo(query, num):
    items = DDGS().text(query, max_results=int(num))
    links = [item['href'] for item in items]
    return parsing.links_parsing(links, query)


def search_bing(query, num):
    subscription_key = os.environ['BING_SEARCH_V7_SUBSCRIPTION_KEY']
    endpoint = os.environ['BING_SEARCH_V7_ENDPOINT'] + "/v7.0/search"
    mkt = 'en-US'
    params = {'q': query, 'mkt': mkt, 'count': num}
    headers = {'Ocp-Apim-Subscription-Key': subscription_key}

    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
        items = response.json().get('webPages', {}).get('value', [])
        links = [item['url'] for item in items]
        return parsing.links_parsing(links, query)
    except Exception as ex:
        raise ex


def search_brave(query, num):
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": os.environ['BRAVE_TOKEN']
    }
    params = {"q": query}
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        items = response.json()['web']['results'][:num]
        links = [item['url'] for item in items]
        return parsing.links_parsing(links, query)
    except requests.exceptions.HTTPError as err:
        logger.error(f"HTTP error occurred: {err}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")


def search_scholar_links(query, num_results):
    search_query = scholarly.search_pubs(query)  # Search for publications on Google Scholar
    articles = []
    links = []
    count = 0
    all_text = ""
    for result in search_query:
        count += 1
        if count > num_results:
            break
        title = result['bib'].get('title', 'No title available')
        abstract = result['bib'].get('abstract', 'No abstract available')
        if 'pub_year' in result:
            year = result.get('pub_year', 'No year available')
        elif 'date' in result:
            year = result.get('date', 'No year available')
        else:
            possible_year = re.search(r'\b(19|20)\d{2}\b', title + " " + abstract)
            year = possible_year.group(0) if possible_year else ''
        author = result['bib'].get('author', '')
        link = result.get('pub_url', None)
        all_text, articles, links = process_database_data(articles, links, all_text, abstract, query, title, link, year, author)
    return all_text, articles, links


def search_pub_med(query, num):
    fetch = PubMedFetcher()
    pmids = fetch.pmids_for_query(query, retmax=num)
    articles = []
    links = []
    all_text = ""
    for pmid in pmids:
        title = fetch.article_by_pmid(pmid).title
        abstract = fetch.article_by_pmid(pmid).abstract
        author = fetch.article_by_pmid(pmid).authors
        year = fetch.article_by_pmid(pmid).year
        link = "https://pubmed.ncbi.nlm.nih.gov/" + pmid + "/"
        logger.info("Pmid" + link)

        all_text, articles, links = process_database_data(articles, links, all_text, abstract, query, title, link, year, author)
    return all_text, articles, links


def process_database_data(articles, links, all_text, abstract, query, title, link, year, author):
    if "YES" in llm.gemini_relative(llm.gemini_config(), abstract, query):
        articles.append({
            "title": title,
            "link": link,
            "abstract": abstract,
            "year": year,
            "author": author
        })
        accumulated_text = (f"Content from [{link}]: \n{abstract}\n"
                            f"----------------------------------------------------------\n")
        links.append(link)
        all_text += accumulated_text
    return all_text, articles, links

