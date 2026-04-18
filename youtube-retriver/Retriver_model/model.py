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

load_dotenv()

llm=ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.3
)

prompt=PromptTemplate(
    template="Preapre 200 words of resposnse for the{query}from given {docs}",
    input_variables=["query","docs"]
)

parser=StrOutputParser()

embedding_model=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

documents_loader=PyPDFLoader("../Documents/kebo105.pdf")
documents=documents_loader.load()

#for x in documents:
 #   print("**********************************************************************************")
  #  print(x.page_content)

splitter=RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

chunks=splitter.split_documents(documents)
#for x in chunks:
 #   print(x)
 #   print("****************************************************************************")

#print(len(chunks))
vs=Chroma(
    #we can add documents directs here 
    #documents=chunks
    embedding_function=embedding_model,
    persist_directory="Mypdf",
    collection_name="flowers"
)
vs.add_documents(chunks)
#result=vs.get(include=["embeddings",'documents','metadatas'])
#for x in result:
#    print(result)
#    print("***************************************************")

retriver=vs.as_retriever(
    search_type="mmr",
    search_kwargs={"k":2,"lambda_mult":1})
query="Parts of flowers "
#result=retriver.invoke(query)
#for i,x in enumerate(result):
   # print(f"******************result{i+1}********************")
    #print(x.page_content) 

chain=retriver|parser|prompt|llm|parser