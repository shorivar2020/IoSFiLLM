import re

from textblob import TextBlob
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk
import logging


nltk.download('stopwords')
stop_words = set(stopwords.words("english"))
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
lemmatizer = WordNetLemmatizer()


def clean_text(text):
    """
    Remove special characters, normalize whitespace, and convert to lowercase.
    """
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)  # Remove special characters
    text = re.sub(r"\s+", " ", text)  # Normalize whitespace
    return text.lower()


def correct_spelling(text):
    """
    Use TextBlob to correct spelling and basic grammar.
    """
    blob = TextBlob(text)
    corrected_text = str(blob.correct())
    return corrected_text


def extract_keywords(text):
    tokens = word_tokenize(text)
    lemmatized_tokens = [lemmatizer.lemmatize(token.lower()) for token in tokens if token.isalpha() and token.lower() not in stop_words]
    return lemmatized_tokens


def prepare_query(text):
    """
    Takes user input, cleans it, corrects it, and prepares a query.
    """
    logging.info("User input: " + text)
    # Step 1: Clean the text
    cleaned_text = clean_text(text)
    logging.info(cleaned_text)

    # Step 2: Correct spelling and grammar
    corrected_text = correct_spelling(cleaned_text)
    logging.info(corrected_text)
    # Step 3: Extract keywords
    keywords = extract_keywords(corrected_text)
    logging.info(keywords)
    keywords.append(corrected_text)
    return ' '.join(keywords)


user_input = "What is negative emotions?"
final_query = prepare_query(user_input)
print("Final Search Query:", final_query)
