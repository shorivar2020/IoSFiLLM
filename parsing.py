import llm
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from loguru import logger


def scrape_with_playwright(url):
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


def parsing_web_page(model, url):
    """Fetch and parse content from a web page"""
    try:
        response = requests.get(url)
        if response.status_code != 200:
            logger.error(f"Failed to retrieve {url} try playwright")
            html = scrape_with_playwright(url)
        else:
            html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        elements = soup.find_all(['p', 'div', 'span', 'h1', 'h2', 'h3', 'li'])
        accumulated_text = ""
        for element in elements:
            text = element.get_text(strip=True)
            if len(text) > 30:
                accumulated_text += text
        if accumulated_text:
            summarization = llm.gemini_clean(model, accumulated_text)
            accumulated_text = (f"Content from [{url}]: \n{summarization}\n"
                                f"----------------------------------------------------------\n")
    except Exception as e:
        logger.error(f"Error parsing {url}: {e}")
        accumulated_text = (f"Error parsing {url}: {e}"
                            f"----------------------------------------------------------\n")
        return accumulated_text
    return accumulated_text


def parsing_doc_db(results):
    links = []
    for r in results:
        # TODO implement ai_engine that check if it is relative doc
        links.append(r['link'])
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


def links_parsing(links, question):
    all_text = ''
    articles = []
    relative_links = []
    for link in links:
        model = llm.gemini_config()
        new_text = parsing_web_page(model, link)
        if new_text != "":
            if "YES" in llm.gemini_relative(model, new_text, question):
                logger.info("Append source")
                relative_links.append(link)
                summ = llm.gemini_summ(model, new_text)
                articles.append({
                    "title": link,
                    "link": link,
                    "abstract": summ,
                    "year": '',
                    "author": ''
                })
                all_text += new_text
    return all_text, articles, relative_links
