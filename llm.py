import logging

import google.generativeai as genai
import os


def gemini(question, context):
    try:
        genai.configure(api_key=os.environ["API_KEY"])
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        responses = model.generate_content("Answer this question: " + question + " Use only this information: " + context)
    except Exception as e:
        logging.info(f"Error size context ai:  {len(context)}")
        responses = ''
    return responses


def gemini_summ(context):
    genai.configure(api_key=os.environ["API_KEY"])
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content("Summorize this text " + context )
    return response


def gemini_answer(question):
    genai.configure(api_key=os.environ["API_KEY"])
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content(question)
    return response

