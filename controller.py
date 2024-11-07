import internet_search
import llm
import preprocess_text
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def controller(question, search_engine, ai_engine):
    question = preprocess_text.prepare_query(question)
    logging.info("Question: " + question)
    match search_engine:
        case "1":
            links = internet_search.search_google(question, 5)
        case "2":
            links = internet_search.search_scholar_links(question, 5)
        case "3":
            links = internet_search.search_duckduckgo(question, 5)
        case "4":
            links = internet_search.search_bing(question, 5)
        case "5":
            links = internet_search.search_brave(question, 5)
        case "6":
            links = internet_search.search_google_new(question, 5)
        case _:
            links = []
            logging.error("Not available search engine")
    logging.info(links)
    all_text = ''
    for link in links:
        logging.info("Parsing of " + link)
        all_text += internet_search.parsing_web_page(link, all_text)
    context = preprocess_text.clean_text(all_text)
    logging.info("Get context")
    match ai_engine:
        case 1:
            response = llm.gemini(question, context)
            ai_answer = llm.gemini_answer(question)
        case _:
            response = llm.gemini(question, context)
            ai_answer = llm.gemini_answer(question)

    return response.text, links, ai_answer.text


if __name__ == "__main__":
    print(controller('what is negative photo?', "6", 1))
