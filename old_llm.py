import logging
import torch
import google.generativeai as genai
import os
from transformers import (
    PegasusForConditionalGeneration, PegasusTokenizer,
    BartForConditionalGeneration, BartTokenizer,
    T5ForConditionalGeneration, T5Tokenizer,
    pipeline
)


def gemini(question, context):
    try:
        genai.configure(api_key=os.environ["API_KEY"])
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        responses = model.generate_content("Answer this question: " + question + " Use only this information: " + context)
    except Exception as e:
        logging.info(f"Error size context ai:  {len(context)}")
        responses = ''
    return responses.text


def gemini_summ(context):
    genai.configure(api_key=os.environ["API_KEY"])
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content("Clean text from access information, CAPTCHAs, JavaScript and cookie requirements, slow response times and another not useful information" + context)
    response = model.generate_content("Summorize this text " + response.text)
    return response.text


def gemini_answer(question):
    genai.configure(api_key=os.environ["API_KEY"])
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content(question)
    return response.text


def pegasus_summ(text):
    model_name = "google/pegasus-xsum"
    tokenizer = PegasusTokenizer.from_pretrained(model_name)
    model = PegasusForConditionalGeneration.from_pretrained(model_name)
    inputs = tokenizer(text, truncation=True, padding="longest", return_tensors="pt")
    summary_ids = model.generate(inputs.input_ids, max_length=60, num_beams=5, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary


def t5(question, context):
    model_name = "t5-base"  # "t5-small", "t5-large" "t5-3b"
    model = T5ForConditionalGeneration.from_pretrained(model_name)
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    input_text = f"question: {question}  context: {context}"
    input_ids = tokenizer.encode(input_text, return_tensors="pt")
    output_ids = model.generate(input_ids)
    answer = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    return answer


def t5_summ(text):
    model_name = "t5-base"  # t5-base, t5-large
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)
    input_text = "summarize: " + text
    inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
    summary_ids = model.generate(inputs.input_ids, max_length=60, num_beams=4, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary


def t5_answer(question):
    model_name = "t5-small"  # "t5-small", "t5-large" или "t5-3b"
    model = T5ForConditionalGeneration.from_pretrained(model_name)
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    input_text = f"question: {question}"
    input_ids = tokenizer.encode(input_text, return_tensors="pt")
    output_ids = model.generate(input_ids)
    answer = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    return answer


def bart(question, context):
    model_name = "facebook/bart-base"  # "facebook/bart-large-cnn"
    model = BartForConditionalGeneration.from_pretrained(model_name)
    tokenizer = BartTokenizer.from_pretrained(model_name)
    input_text = f"question: {question} context: {context}"
    input_ids = tokenizer.encode(input_text, return_tensors="pt", max_length=1024)
    output_ids = model.generate(input_ids, max_length=1024, num_beams=5, early_stopping=True)
    answer = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    return answer


def bart_summ(text):
    model_name = "facebook/bart-base"
    model = BartForConditionalGeneration.from_pretrained(model_name)
    tokenizer = BartTokenizer.from_pretrained(model_name)
    inputs = tokenizer(text, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = model.generate(inputs["input_ids"], max_length=150, min_length=50, length_penalty=2.0, num_beams=4,
                                 early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary


def bart_answer(question):
    model_name = "facebook/bart-base"   # "facebook/bart-large-cnn"
    model = BartForConditionalGeneration.from_pretrained(model_name)
    tokenizer = BartTokenizer.from_pretrained(model_name)
    input_text = f"question: {question}"
    input_ids = tokenizer.encode(input_text, return_tensors="pt")
    output_ids = model.generate(input_ids, max_length=50, num_beams=5, early_stopping=True)
    answer = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return answer
