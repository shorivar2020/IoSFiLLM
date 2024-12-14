import google.generativeai as genai
import os
from loguru import logger


def gemini(question, context):
    try:
        genai.configure(api_key=os.environ["API_KEY"])
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        responses = model.generate_content("Answer this question: " + question + " Use only this information: " +
                                           context +
                                           "when you use information create cite where you take it  AND WRITE TAKEN URL IN THIS FORMAT: "
                                           "text_from_source  <a href='url_from_source'>1</a>"
                                           "text_from_source_second <a href='url_from_second_source'>2</a> ")
    except Exception as e:
        logger.info(f"Error size context ai:  {len(context)}")
        responses = ''
    return responses.text


def gemini_config():
    genai.configure(api_key=os.environ["API_KEY"])
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    return model


def gemini_clean(model, context):
    response = model.generate_content("Clean text from access information, CAPTCHAs, JavaScript and cookie requirements, slow response times and another not useful information" + context)
    return response.text


def gemini_summ(model, context):
    response = model.generate_content("Summorize this text " + context)
    return response.text


def gemini_relative(model, context, question):
    response = model.generate_content("Check if this text " + context + " is relative to this question " + question +
                                      "RETURN ONLY NO or YES")
    logger.warning("RELATIVITY " + response.text)
    return response.text


def gemini_answer(question):
    genai.configure(api_key=os.environ["API_KEY"])
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content(question)
    return response.text
