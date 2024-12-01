import re

from scholarly import scholarly
from googlesearch import search
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import os
import requests
import llm
from Bio import Entrez
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from metapub import PubMedFetcher
import pandas as pd


subscription_key = os.environ['BING_SEARCH_V7_SUBSCRIPTION_KEY']
endpoint = os.environ['BING_SEARCH_V7_ENDPOINT'] + "/v7.0/search"
# export BING_SEARCH_V7_SUBSCRIPTION_KEY="30019514e5c24d9db274a13d925077ed"
# export BING_SEARCH_V7_ENDPOINT="https://api.bing.microsoft.com"


def search_google_pirate(question, num_results):
    links = []
    for result in search(question, num=5):
        links.append(result)
    return links


def search_google(query, num_results):

    params = {
        'q': query,
        'key': 'AIzaSyBQPjmZ7_93LnCwF0z9JSjiQF16Lrj9vPo',
        'cx': '466d5706bf5384c11',
        'num': num_results
    }
    response = requests.get('https://www.googleapis.com/customsearch/v1', params=params)
    links = []
    for item in response.json()['items']:
        links.append(item['link'])
    return links


def search_duckduckgo(question, num_results):
    results = DDGS().text(question, max_results=num_results)
    links = [result['href'] for result in results]
    return links


def search_bing(query, num):
    mkt = 'en-US'
    params = {'q': query, 'mkt': mkt, 'count': num}
    headers = {'Ocp-Apim-Subscription-Key': subscription_key}

    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
        urls = [item['url'] for item in response.json().get('webPages', {}).get('value', [])]
        return urls
    except Exception as ex:
        raise ex


def search_brave(query, num):
    # Define the Brave Search API URL
    url = "https://api.search.brave.com/res/v1/web/search"

    # Set the headers with your Brave API key (replace 'YOUR_API_KEY' with your actual API key)
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": "BSAfdTtBkmxIVHJlkS1tSJG22KJcr6u"
    }

    # Set the search parameters
    params = {
        "q": query
    }

    try:
        # Send a GET request to the Brave Search API
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an error for bad responses
        results = response.json()
        urls = [result['url'] for result in results['web']['results'][:num]]
        return urls
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as e:
        print(f"An error occurred: {e}")


def search_scholar_links(question, num_results):
    search_query = scholarly.search_pubs(question)  # Search for publications on Google Scholar
    articles = []
    links = []
    count = 0
    all_text = ""
    for result in search_query:
        # Extract details from the result
        title = result['bib'].get('title', 'No title available')
        abstract = result['bib'].get('abstract', 'No abstract available')
        keywords = result['bib'].get('keywords', 'No keywords available')
        if 'pub_year' in result:
            year = result.get('pub_year', 'No year available')
        elif 'date' in result:
            year = result.get('date', 'No year available')
        else:
            possible_year = re.search(r'\b(19|20)\d{2}\b', title + " " + abstract)
            year = possible_year.group(0) if possible_year else ''
        author = result['bib'].get('author', '')
        pub_url = result.get('pub_url', None)
        links.append(pub_url)
        # Prepare the data to append
        article = {
            'title': title,
            'abstract': abstract,
            "year": year,
            "author": author,
            'keywords': keywords,
            'link': pub_url if pub_url else 'No link available'
        }
        articles.append(article)
        all_text += abstract
        # Stop after the desired number of results
        count += 1
        if count >= num_results:
            break

    return articles, links, all_text


def search_pub_med(query, num):
    fetch = PubMedFetcher()
    pmids = fetch.pmids_for_query(query, retmax=num)
    articles = []
    links = []
    all_text = ""
    for pmid in pmids:
        article = fetch.article_by_pmid(pmid)
        title = fetch.article_by_pmid(pmid).title
        abstract = fetch.article_by_pmid(pmid).abstract
        author = fetch.article_by_pmid(pmid).authors
        year = fetch.article_by_pmid(pmid).year
        volume = fetch.article_by_pmid(pmid).volume
        issue = fetch.article_by_pmid(pmid).issue
        journal = fetch.article_by_pmid(pmid).journal
        citation = fetch.article_by_pmid(pmid).citation
        link = "https://pubmed.ncbi.nlm.nih.gov/" + pmid + "/"
        articles.append({
            "title": title,
            "link": link,
            "abstract": abstract,
            "year": year,
            "author": author
        })
        links.append(link)
        all_text += abstract
    return articles, links, all_text


def scrape_with_headers(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"
        )
        page = context.new_page()
        page.goto(url)

        # Wait and mimic human actions
        page.wait_for_timeout(3000)  # Wait 3 seconds
        content = page.content()
        browser.close()

        return content


def parsing_web_page(url, accumulated_text, ai_engine):
    """Fetch and parse content from a web page"""
    try:
        response = requests.get(url)
        if response.status_code != 200:
            html = scrape_with_headers(url)
            print(f"Failed to retrieve {url}")
        else:
            html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        elements = soup.find_all(['p', 'div', 'span', 'h1', 'h2', 'h3', 'li'])
        for element in elements:
            text = element.get_text(strip=True)
            if len(text) > 30:
                accumulated_text += text
        match ai_engine:
            case "2":
                summarization = llm.pegasus_summ(accumulated_text)
            case "3":
                summarization = llm.t5_summ(accumulated_text)
            case "4":
                summarization = llm.bart_summ(accumulated_text)
            case _:
                summarization = llm.gemini_summ(accumulated_text)
        accumulated_text = f"Content from {url} amd ai_engine {ai_engine}:\n{summarization}\n\n"
    except Exception as e:
        print(f"Error parsing {url}: {e}")
    return accumulated_text


def parsing_doc_db(results, ai_engine):
    links = []
    for r in results:
        # TODO implement ai_engine that check if it is relative doc
        links.append(r['link'])
        # print(r['link'])
        # print(r['abstract'])
        # print(r['title'])
        # print(r['keywords'])
        # print("-------------------")
    return links


def fetch_html_data(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title').text
        paragraphs = [p.text for p in soup.find_all('p')]
        return " ".join(paragraphs)
    else:
        return {"error": f"Unable to fetch the page, status code: {response.status_code}"}


def links_parsing(links, ai_engine):
    all_text = ''
    articles = []
    for link in links:
        new_text = parsing_web_page(link, all_text, ai_engine)
        articles.append({
            "title": link,
            "link": link,
            "abstract": new_text,
            "year": '',
            "author": ''
        })
        all_text += new_text
    return all_text, articles


if __name__ == '__main__':
    print("Start app")
    # print(search_google("What is negative emotions?", 5))
# print(search_scholar_links("What is negative emotions?", 5))
#     print("Duck duck go")
#     print(search_duckduckgo("What is negative emotions?", 5))
#     print("Bing")
#     print(search_bing("What is negative emotions?", 5))
#     print("Brave")
    # print(search_brave("What is negative emotions?", 5))
    # print("Google Scholar")
    # for res in search_scholar_links("What is negative emotions?", 5):
    #     print(res['link'])
    # print("Pub med")
    # for res in search_pub_med("What is negative emotions?", 5):
    #     print(res)
    # print(search_pub_med("Indicate ibuprofen", 5))
    # print(search_scholar_links("Indicate ibuprofen", 5))
