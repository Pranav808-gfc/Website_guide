from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
#from langchain_community.retrievers import vec
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser
from pyparsing import ParserElement
from torch import embedding
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import WebBaseLoader

load_dotenv()

llm=ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.3
)

prompt=PromptTemplate(
    template="Preapre 200 words of resposnse for the{query}from given {docs} only refere the data fom document dont provide other information ",
    input_variables=["query","docs"]
)

parser=StrOutputParser()

embedding_model=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def load_data(url):
    documents_loader=WebBaseLoader(url)
    documents=documents_loader.load()
    return documents

def get_chunks(documents):
    splitter=RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
    )
    chunks=splitter.split_text(documents)
    return chunks

def get_retirver(chunks):
    vs=Chroma(
    embedding_function=embedding_model,
    persist_directory="MyWebdata",
    collection_name="webdata"
    )
    vs.add_documents(chunks)
    retriver=vs.as_retriever(
    search_type="mmr",
    search_kwargs={"k":2,"lambda_mult":1})
    return retriver

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def get_answer(query,url):
    documents=load_data(url)
    chunks=get_chunks(documents)
    retriver=get_retirver(chunks)
    chain = (
    {
        "docs": retriver | format_docs,
        "query": RunnablePassthrough()
    }| prompt
    | llm
    | parser
    )
    result=chain.invoke(query)
    return result