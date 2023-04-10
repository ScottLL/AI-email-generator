import os
import requests
from bs4 import BeautifulSoup
# from dotenv import load_dotenv
import pinecone

from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.vectorstores import Pinecone

# Load environment variables
# Load environment variables
# load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_API_ENV = os.environ.get("PINECONE_API_ENV")


class Document:
    def __init__(self, page_content, metadata, doc_id):
        self.page_content = page_content
        self.metadata = metadata
        self.doc_id = doc_id


# Initialize Pinecone
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_API_ENV)
index_info = pinecone.list_indexes()
print(index_info)

# Collect web page content
introduction_url = "https://doc.rust-lang.org/stable/book/ch00-00-introduction.html"

page = requests.get(introduction_url)
soup = BeautifulSoup(page.content, "html.parser")
main_content = soup.find("div", class_="book-body")
if main_content is None:
    main_content = soup.find("body")
page_content = main_content.get_text()
doc = Document(page_content=page_content, metadata={"source": introduction_url}, doc_id=0)
documents = [doc]

# Extract chapter URLs
chapter_list = soup.find("nav", class_="sidebar")
chapter_links = chapter_list.find_all("a")
chapter_urls = ["https://doc.rust-lang.org/stable/book/" + link["href"] for link in chapter_links]

# Iterate through chapter URLs and collect the content
doc_id = 0
documents = []
for url in chapter_urls:
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    main_content = soup.find("div", class_="book-body")
    if main_content is None:
        main_content = soup.find("body")
    page_content = main_content.get_text()
    doc = Document(page_content=page_content, metadata={"source": url}, doc_id=doc_id)
    documents.append(doc)
    doc_id += 1

metadata_dict = {doc.doc_id: doc.metadata for doc in documents}

# Split documents into smaller chunks
max_len = 10000
splitter = RecursiveCharacterTextSplitter(chunk_size=max_len, chunk_overlap=0)
split_documents = splitter.split_documents(documents)

# Create embeddings and Pinecone indexes for each chunk
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
index_names = []
doc_chunks = []
for i, doc_chunk in enumerate(split_documents):
    index_name = f"langchain_{i}"
    index_names.append(index_name)
    chunk_data = [(doc.page_content, {"doc_id": doc.doc_id}) for doc in doc_chunk]
    doc_chunks.append(chunk_data)
    doc_texts = [doc.page_content for doc in doc_chunk]
    docsearch = Pinecone.from_texts(doc_texts, embeddings, index_name=index_name, include_metadata=True)

# Create language model object
llm = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)
chain = load_qa_chain(llm, chain_type="stuff")

# Define get_answer function
def get_answer(docsearch, chain, question, metadata_dict, top_n=20):
    docs = docsearch.similarity_search(question, top_n=top_n, include_metadata=False)
    docs_with_metadata = [Document(doc.page_content, metadata_dict[doc.doc_id], doc.doc_id) for doc in docs]
    result = chain.run(input_documents=docs_with_metadata, question=question)
    return result


# Example usage of get_answer function
question = "tell me rust for Students"
answer = get_answer(docsearch, chain, question, metadata_dict)
print(answer)
