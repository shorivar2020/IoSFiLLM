import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


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


def main(url):
    html = scrape_with_headers(url)
    # print(html)
    accumulated_text = ""
    # response = requests.get("https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1467-6494.2008.00496.x")
    soup = BeautifulSoup(html, 'html.parser')
    elements = soup.find_all(['p', 'div', 'span', 'h1', 'h2', 'h3', 'li'])
    for element in elements:
        text = element.get_text(strip=True)
        if len(text) > 30:
            accumulated_text += text
            print(text)


url = "https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1467-6494.2008.00496.x"
main(url)
#https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1467-6494.2008.00496.x
#https://psycnet.apa.org/fulltext/2011-28769-001.html
#https://onlinelibrary.wiley.com/doi/abs/10.1002/acp.1064
#https://psycnet.apa.org/journals/psp/95/1/66/
