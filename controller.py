import internet_search
import llm
import preprocess_text
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def search_in_search_engine(question, search_engine, ai_engine, result_num):
    logging.info("Preprocess query")
    if len(question.split()) > 5:
        question = preprocess_text.prepare_query(question)
    logging.info("Question: " + question)
    # Find in search engine
    num_results = 5
    match search_engine:
        case "1":
            links = internet_search.search_google(question, num_results)
            all_text, articles = internet_search.links_parsing(links, ai_engine)
        case "2":
            links = internet_search.search_duckduckgo(question, result_num)
            all_text, articles = internet_search.links_parsing(links, ai_engine)
        case "3":
            links = internet_search.search_bing(question, result_num)
            all_text, articles = internet_search.links_parsing(links, ai_engine)
        case "4":
            links = internet_search.search_brave(question, result_num)
            all_text, articles = internet_search.links_parsing(links, ai_engine)
        case "5":
            articles, links, all_text = internet_search.search_scholar_links(question, result_num)
            links = internet_search.parsing_doc_db(articles, ai_engine)
        case "6":
            articles, links, all_text = internet_search.search_pub_med(question, result_num)
            links = internet_search.parsing_doc_db(articles, ai_engine)
        case _:
            links = []
            articles = []
            all_text = ""
            logging.error("Not available search engine")
    logging.info(links)
    context = preprocess_text.clean_text(all_text)
    print(context)
    logging.info("Get context")
    with open("context.txt", "w") as file:
        file.write(context)
    with open("context.txt", "r") as file:
        context = file.read()
    match ai_engine:
        case "1":
            response = llm.gemini(question, context)
            ai_answer = llm.gemini_answer(question)
        case "2":
            response = llm.pegasus_summ(context)
            ai_answer = llm.gemini_answer(question)
        case "3":
            response = llm.t5(question, context)
            ai_answer = llm.t5_answer(question)
        case "4":
            response = llm.bart(question, context)
            ai_answer = llm.bart_answer(question)
        case _:
            response = llm.gemini(question, context)
            ai_answer = llm.gemini_answer(question)
    return response, links, articles, ai_answer


def search_in_db(question, db, ai_engine, result_num):
    links = []
    match db:
        case 1:
            articles, links = internet_search.search_scholar_links(question, result_num)
            print(articles)
            # all_text = internet_search.links_parsing(links, ai_engine)
            links = internet_search.parsing_doc_db(articles, ai_engine)
        case 2:
            articles, links = internet_search.search_pub_med(question, result_num)
            links = internet_search.parsing_doc_db(articles, ai_engine)
        case _:
            logging.error("Not available db")
    return links


def controller(question, search_engine, ai_engine):
    links = []
    articles = []
    response = ""
    ai_answer = ""
    result_num = 15
    if search_engine is not None:
        response, links, articles, ai_answer = search_in_search_engine(question, search_engine, ai_engine, result_num)
    print("Response " + response)
    print("AI Answer " + ai_answer)
    for link in links:
        print("L " + link)
    for article in articles:
        print("A " + str(article))
    return response, links, articles, ai_answer


if __name__ == "__main__":
    controller('Indicate ibuprofen', "6", "1",)
