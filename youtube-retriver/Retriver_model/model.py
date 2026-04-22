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
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import WebBaseLoader

load_dotenv()

llm=ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.3
)

prompt=PromptTemplate(
    template=
    "You are an AI assistant:TASK Prepare a response of approximately 200 words for the given Question using ONLY the information provided in the Documents section." \
    "STRICT RULES (MANDATORY):\
1. Use ONLY facts, statements, and data explicitly present in the Documents.\
2. DO NOT add background knowledge, assumptions, interpretations, or external information.\
3. DO NOT infer or extrapolate beyond what is written in the Documents.\
4. If the Documents do not contain enough information to fully answer the Question, clearly state:\
   The provided documents do not contain sufficient information to fully answer this question.\
5. Do NOT mention any sources, citations, or references outside the Documents.\
6. Do NOT include examples, explanations, or definitions unless they appear verbatim or clearly within the Documents.\
7. Maintain a neutral and factual tone.\
8. Limit the response to approximately 200 words (±10%).\
INPUT FORMAT:\
Question:\
{Question}\
Documents:\
{docs}\
OUTPUT FORMAT:\
- A single continuous response of approximately 200 words\
- Content must be strictly grounded in the Documents\
- No headings, bullet points, or additional commentary",
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
    chunks=splitter.split_documents(documents)
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

def get_answer(Question,url):
    documents=load_data(url)
    chunks=get_chunks(documents)
    retriver=get_retirver(chunks)
    chain = (
    {
        "docs": retriver | format_docs,
        "Question": RunnablePassthrough()
    }| prompt
    | llm
    | parser
    )
    result=chain.invoke(Question)
    return result