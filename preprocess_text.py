"""
This module provides functions to clean user input text, correct spelling and grammar,
extract keywords, and prepare queries for further processing.
"""
import re
from loguru import logger
from textblob import TextBlob
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk
import llm


def clean_text(text):
    """
    Remove special characters, normalize whitespace, and convert to lowercase.

    Args:
        text (str): The input text to be cleaned.

    Returns:
        str: The cleaned text with special characters removed, normalized whitespace,
             and converted to lowercase.
    """
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)  # Remove special characters
    text = re.sub(r"\s+", " ", text)  # Normalize whitespace
    return text.lower()


def correct_spelling(text):
    """
    Use TextBlob to correct spelling and basic grammar.

    Args:
        text (str): The input text to be corrected.

    Returns:
        str: The text after spelling and grammar correction.
    """
    blob = TextBlob(text)
    corrected_text = str(blob.correct())
    return corrected_text


def prepare_query(text):
    """
    Takes user input, cleans it, corrects it, and prepares a query.

    This function processes the user input by:
    - Cleaning the text to remove unwanted characters and normalize format.
    - Correcting spelling and grammar errors.
    - Tokenizing the text to extract meaningful keywords.
    - Lemmatizing the tokens and removing stop words.
    - Leveraging an external LLM to further process keywords.

    Args:
        text (str): The raw input text from the user.

    Returns:
        tuple: A tuple containing the corrected text and keywords processed by the LLM.
    """
    # Ensure required NLTK resources are downloaded
    nltk.download('wordnet')  # WordNet lemmatizer resources
    nltk.download('omw-1.4')  # Additional WordNet resources
    nltk.download('stopwords')  # Stopwords for filtering out common words
    nltk.download('punkt_tab')  # Tokenizer resources
    stop_words = set(stopwords.words("english"))
    lemmatizer = WordNetLemmatizer()

    logger.info(f"User input: {text}")
    # Clean the input text
    cleaned_text = clean_text(text)
    logger.info(f"Cleaned text: {cleaned_text}")
    # Correct spelling and grammar
    corrected_text = correct_spelling(cleaned_text)
    logger.info(f"Corrected text: {corrected_text}")
    tokens = word_tokenize(text)
    logger.info(f"Tokens: {tokens}")
    # Extract keywords by filtering stopwords and lemmatizing tokens
    keywords = [lemmatizer.lemmatize(token.lower()) for token in tokens if
                token.isalpha() and token.lower() not in stop_words]
    logger.info(f"Keywords: {keywords}")
    # Use LLM to find keywords
    keywords = llm.gemini_find_keywords(llm.gemini_config(),
                                        ' '.join(keywords), text)
    logger.info(f"Keywords from LLM: {str(keywords)}")
    return corrected_text, correct_spelling(keywords)
