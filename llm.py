import time

import google.generativeai as genai
import os
from loguru import logger
from google.api_core.exceptions import ResourceExhausted
import time


def gemini(question, context):
    try:
        genai.configure(api_key=os.environ["API_KEY"])
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        responses = model.generate_content("Answer this question: " + question + " Use only this information: " +
                                           context +
                                           "when you use information create cite where you take it "
                                           " AND WRITE TAKEN URL IN THIS FORMAT: "
                                           "text_from_source  [ <a href='url_from_source' target='_blank'>1</a> ]."
                                           "text_from_source_second "
                                           "[ <a href='url_from_second_source' target='_blank'>2</a> ]."
                                           "text_from_second_and_one_source "
                                           "[ <a href='url_from_source' target='_blank'>1</a> ], "
                                           "[ <a href='url_from_second_source' target='_blank'>2</a> ].")
    except ResourceExhausted as e:
        print(f"Encountered ResourceExhausted: {e}")
        time.sleep(60)
        return gemini(question, context)
    except Exception as e:
        logger.info(f"Error size context ai:  {len(context)}")
        return ''
    return responses.text


def gemini_config():
    genai.configure(api_key=os.environ["API_KEY"])
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    return model


def gemini_clean(model, context):
    try:
        logger.info("GEMINI CLEAN")
        response = model.generate_content("Clean the text and remove any irrelevant or distracting information." + context)

        logger.info("GEMINI CLEAN STOP")
        return response.text
    except ResourceExhausted as e:
        print(f"Encountered ResourceExhausted: {e}")
        return "ResourceExhausted " + context
    except Exception as e:
        logger.error(f"ERROR Gemini clean {e}")
        return ""


def gemini_summ(model, context):
    try:
        response = model.generate_content("Summorize this text " + context)
        return response.text
    except ResourceExhausted as e:
        print(f"Encountered ResourceExhausted: {e}")
        return "ResourceExhausted " + context


def gemini_relative(model, context, question):
    try:
        response = model.generate_content("Check if this text " + context + " is relative to this question " + question +
                                          "RETURN ONLY NO or YES")
        logger.warning("RELATIVITY " + response.text)
        return response.text
    except ResourceExhausted as e:
        print(f"Encountered ResourceExhausted: {e}")
        return "ResourceExhausted " + question


def gemini_find_keywords(model, keywords, question):
    try:
        response = model.generate_content("delete not target keywords from this list  " + keywords +
                                          " of this query " + question +
                                          "RETURN ONLY KEYWORDS")
        logger.warning("KEYWORDS " + response.text)
        return response.text
    except ResourceExhausted as e:
        print(f"Encountered ResourceExhausted: {e}")
        return "ResourceExhausted " + keywords


def gemini_answer(question):
    try:
        genai.configure(api_key=os.environ["API_KEY"])
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        response = model.generate_content(question)
        return response.text
    except ResourceExhausted as e:
        print(f"Encountered ResourceExhausted: {e}")
        time.sleep(60)
        return gemini_answer(question)
