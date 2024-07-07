import os
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import tool, Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain.tools.retriever import create_retriever_tool

from prompts import COT_LIMITS_PROMPT, QUESTION

load_dotenv(find_dotenv())


def create_retriever():
    # load the document and split it into chunks
    loader = TextLoader("data/rules.txt")
    documents = loader.load()

    # split it into chunks
    text_splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)

    # create the open-source embedding function
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    # load it into Chroma
    db = Chroma.from_documents(docs, embedding_function)
    # query = "Travel to New York"
    # docs = db.similarity_search(query)
    # print(docs[0].page_content)
    # print(docs)
    retriever = db.as_retriever()
    tool = create_retriever_tool(
        retriever,
        "search_travel_budget_rules",
        "Searches and returns excerpts from the travel budget policy",
    )
    tools = [tool]
    return tools


def initialize_agent_validator(retriever):
    llm = ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        # model="gpt-3.5-turbo",
        model="gpt-4o",
        temperature=0.7,
    )
    web_search_res_prompt = PromptTemplate.from_template(COT_LIMITS_PROMPT)
    agent = create_react_agent(llm=llm, prompt=web_search_res_prompt, tools=retriever)
    agent_executor = AgentExecutor(
        agent=agent,
        verbose=True,
        tools=retriever,
        handle_parsing_errors=True,
        max_iterations=5,
    )
    return agent_executor


PROCESS_SUMS = lambda x: x.replace("$", "").replace(",", "")


if __name__ == "__main__":
    tools = create_retriever()
    agent_executor = initialize_agent_validator(tools)
    # condition = "Client workshop in Silicon Valley"
    condition = "Sales training in Dubai during peak tourist season"
    given_sum = "$2,700"
    result = agent_executor.invoke({"input": QUESTION.format(conditions=condition)})
    result = result["output"]
    print(result)
    limit = PROCESS_SUMS(result.split(" ")[0])
    try:
        price = PROCESS_SUMS(given_sum)
        price = int(price)
    except:
        raise Exception("Error in price conversion to int. Check your file")
    if int(limit) < price:
        decision = f"Prohibited. Current cost limit: {result} which if lower than current price {price}"
    else:
        decision = f"Allowed. Current cost limit: {result} which if higher than current price {price}"
    print(decision)
