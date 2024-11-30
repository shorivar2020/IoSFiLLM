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

    for result in search_query:
        # Extract details from the result
        title = result['bib'].get('title', 'No title available')
        abstract = result['bib'].get('abstract', 'No abstract available')
        keywords = result['bib'].get('keywords', 'No keywords available')
        pub_url = result.get('pub_url', None)
        links.append(pub_url)
        # Prepare the data to append
        article = {
            'title': title,
            'abstract': abstract,
            'keywords': keywords,
            'link': pub_url if pub_url else 'No link available'
        }
        articles.append(article)

        # Stop after the desired number of results
        count += 1
        if count >= num_results:
            break

    return articles, links


def search_pub_med(query, num):
    Entrez.email = "shorivar@fel.cvut.cz"  # Set the email parameter
    # Search PubMed
    handle = Entrez.esearch(db="pubmed", term=query, retmax=num)
    record = Entrez.read(handle)
    handle.close()

    # Get PubMed IDs (PMIDs)
    id_list = record["IdList"]
    # Fetch links
    links = []
    articles = []
    for pubmed_id in id_list:
        handle = Entrez.esummary(db="pubmed", id=pubmed_id)
        summary = Entrez.read(handle)
        handle.close()
        links.append(f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/")
        title = summary[0].get("Title", "No title available")
        link = f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/"
        abstract = summary[0].get("Source", "No abstract available")
        keywords = summary[0].get("Keywords", "No keywords available")
        print(title)
        print(abstract)
        links.append(link)
        articles.append({
            "title": title,
            "link": link,
            "abstract": abstract,
            "keywords": keywords
        })
    return articles, links


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
    for link in links:
        new_text = parsing_web_page(link, all_text, ai_engine)
        all_text += new_text
    return all_text


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
    for res in search_pub_med("What is negative emotions?", 5):
        print(res)
