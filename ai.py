from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup
import re
from transformers import pipeline
from transformers import BartForConditionalGeneration, BartTokenizer
from scholarly import scholarly
from googlesearch import search


MODEL_NAME = 'facebook/bart-large'
NUMBER_OF_INTERNET_RESULT = 15
MAX_INPUT_LENGTH = 1024
SUMMARY_MAX_LENGTH = 512
SUMMARY_MIN_LENGTH = 100
ANSWER_MAX_LENGTH = 500
ANSWER_MIN_LENGTH = 100
ANSWER_LENGTH_PENALTY = 2.0
NUM_BEAMS = 4
# Initialize BART model and tokenizer
tokenizer = BartTokenizer.from_pretrained(MODEL_NAME)
model = BartForConditionalGeneration.from_pretrained(MODEL_NAME)


def get_summary(context):
    """Generate a summary of the provided text"""
    summarizer = pipeline("summarization")
    tokens = summarizer.tokenizer.encode(context, truncation=True, max_length=MAX_INPUT_LENGTH)
    truncated_text = summarizer.tokenizer.decode(tokens, skip_special_tokens=True)
    summary = summarizer(truncated_text, max_length=SUMMARY_MAX_LENGTH, min_length=SUMMARY_MIN_LENGTH, do_sample=False)
    print(summary[0]['summary_text'])


def get_long_answer(context, question):
    """Generate a long answer using BART model"""
    # Construct the input for the model
    input_text = f"{context}\n\nQuestion: {question}"
    inputs = tokenizer.encode(input_text, return_tensors='pt', max_length=MAX_INPUT_LENGTH, truncation=True)

    # Generate the response
    summary_ids = model.generate(inputs, max_length=ANSWER_MAX_LENGTH, min_length=ANSWER_MIN_LENGTH,
                                 length_penalty=ANSWER_LENGTH_PENALTY, num_beams=NUM_BEAMS, early_stopping=True)
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)


def get_answer(context, question):
    """Generate a short answer using question-answering pipeline"""
    qa_pipeline = pipeline("question-answering")
    result = qa_pipeline(question=question, context=context)
    return result['answer']


def clean_text(text):
    """Clean and preprocess text by removing unwanted characters and phrases"""
    text = re.sub(r'\s*Free eBooks at Planet eBook\.com\s*', '', text, flags=re.DOTALL)
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'(David Copperfield )?[\x00-\x1F]', '', text)
    text = text.replace('\n', ' ')
    text = re.sub(r'\s*-\s*', '', text)
    return text


def parsing_web_page(url, accumulated_text):
    """Fetch and parse content from a web page"""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = soup.find_all('p')
            page_text = ""
            for paragraph in paragraphs:
                page_text += paragraph.get_text() + " "
            accumulated_text += f"Content from {url}:\n{page_text}\n\n"
        else:
            print(f"Failed to retrieve {url}")
    except Exception as e:
        print(f"Error parsing {url}: {e}")
    return accumulated_text


def search_duckduckgo(query):
    """Search DuckDuckGo for the provided query and return the links"""
    results = DDGS().text(query, max_results=NUMBER_OF_INTERNET_RESULT)
    links = [result['href'] for result in results]
    return links


def search_scholar_links(query, num_results):
    """Search Google Scholar for the provided query and return only the links."""
    search_query = scholarly.search_pubs(query)

    links = []
    for i, result in enumerate(search_query):
        if i >= num_results:
            break
        # Extract the publication URL if available
        pub_url = result.get('pub_url', None)
        if pub_url:
            links.append(pub_url)
    return links


def text_to_file(file_name, text):
    with open(file_name, 'w') as file:
        # Write the text to the file
        file.write(text)
        file.close()


def ai(question):
    # What emotions are negative?
    # question = input("Input you question: ")
    # question = 'What emotions are negative?'
    # Search for relevant web pages
    links = []
    # Google Scholar
    # links = search_scholar_links(question, num_results=NUMBER_OF_INTERNET_RESULT)
    # Duck Duck Go
    # links = search_duckduckgo(question)
    # Google
    for result in search(question, num_results=NUMBER_OF_INTERNET_RESULT):
        links.append(result)
    print(links)
    all_text = ""
    # Parsing web pages
    for link in links:
        all_text = parsing_web_page(link, all_text)
    context = clean_text(all_text)
    # Get summary
    # print(get_summary(context))
    # Get short answer
    short_answer = get_answer(context, question)
    # Get long answer
    long_answer = get_long_answer(context, question)
    # Save text to file
    text_to_file('Google - Bart', short_answer + long_answer)
    return long_answer

if __name__ == "__main__":
    ai('What emotions are negative?')
