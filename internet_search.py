import scholarly
from googlesearch import search
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import os
import requests
import llm

subscription_key = os.environ['BING_SEARCH_V7_SUBSCRIPTION_KEY']
endpoint = os.environ['BING_SEARCH_V7_ENDPOINT'] + "/v7.0/search"
# export BING_SEARCH_V7_SUBSCRIPTION_KEY="30019514e5c24d9db274a13d925077ed"
# export BING_SEARCH_V7_ENDPOINT="https://api.bing.microsoft.com"


def search_google(question, num_results):
    links = []
    for result in search(question, num=5):
        links.append(result)
    return links


def search_google_new(query, num_results):
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
    # print(response.json()['items'])


def search_duckduckgo(question, num_results):
    results = DDGS().text(question, max_results=num_results)
    links = [result['href'] for result in results]
    return links


def search_scholar_links(question, num_results):
    search_query = scholarly.search_pubs_query(question)
    links = []
    for i, result in enumerate(search_query):
        if i >= num_results:
            break
        # Extract the publication URL if available
        pub_url = result.get('pub_url', None)
        if pub_url:
            links.append(pub_url)
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

        # Parse the JSON response
        results = response.json()

        print(results)

    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as e:
        print(f"An error occurred: {e}")


def parsing_web_page(url, accumulated_text):
    """Fetch and parse content from a web page"""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            elements = soup.find_all(['p', 'div', 'span', 'h1', 'h2', 'h3', 'li'])
            for element in elements:
                text = element.get_text(strip=True)
                if len(text) > 30:
                    accumulated_text += text
            summarization = llm.gemini_summ(accumulated_text)
            accumulated_text += f"Content from {url}:\n{summarization}\n\n"
        else:
            print(f"Failed to retrieve {url}")
    except Exception as e:
        print(f"Error parsing {url}: {e}")
    return accumulated_text

