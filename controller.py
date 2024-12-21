import internet_search
import llm
import preprocess_text
from loguru import logger


def process_download_document(document):
    model = llm.gemini_config()
    return llm.gemini_summ(model, document)


def controller(question, search_engine, num_results, file_content):
    question_keywords = question
    if len(question.split()) > 5:
        logger.info("Question too long, start preprocessing")
        question, question_keywords = preprocess_text.prepare_query(question)

    logger.info("Start searching " + question)
    match search_engine:
        case "1":
            links = internet_search.search_google(question, num_results)
            all_text, articles, links = internet_search.links_parsing(links, question)
        case "2":
            links = internet_search.search_duckduckgo(question, num_results)
            all_text, articles, links = internet_search.links_parsing(links, question)
        case "3":
            links = internet_search.search_bing(question, num_results)
            all_text, articles, links = internet_search.links_parsing(links, question)
        case "4":
            links = internet_search.search_brave(question, num_results)
            all_text, articles, links = internet_search.links_parsing(links, question)
        case "5":
            articles, links, all_text = internet_search.search_scholar_links(question_keywords, num_results)
            links = internet_search.parsing_doc_db(articles)
        case "6":
            articles, links, all_text = internet_search.search_pub_med(question_keywords, num_results)
            links = internet_search.parsing_doc_db(articles)
        case _:
            links = []
            articles = []
            all_text = ""
            logger.error("Not available search engine")

    logger.info("Create context")
    if file_content:
        if len(file_content[0]) > 10:
            logger.info("Add file content")
            file = (f"Content from uploaded file: \n{file_content[0]}\n"
                    f"----------------------------------------------------------\n")
            articles.append({
                "title": "Uploaded content",
                "link": '',
                "abstract": file,
                "year": '',
                "author": ''
            })
            all_text += file
    context = all_text
    # context = preprocess_text.clean_text(all_text)
    with open("context.txt", "w") as file:
        file.write(context)
    with open("context.txt", "r") as file:
        context = file.read()

    logger.info("Get answers")
    response = llm.gemini(question, context)
    ai_answer = llm.gemini_answer(question)
    return response, links, articles, ai_answer


if __name__ == "__main__":
    r, urls, a, ai = controller('Can you find similar articles to Happy ending programme?',
                                "2", 10, "")
    for i in range(len(urls)):
        logger.info("Link " + urls[i])
        logger.info("Article " + str(a[i]))
    logger.info("Response " + r)
    # logger.info("AI Answer " + ai)
