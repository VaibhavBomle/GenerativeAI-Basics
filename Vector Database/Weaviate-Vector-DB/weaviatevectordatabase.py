# -*- coding: utf-8 -*-
"""WeaviateVectorDatabase.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/18Jtb34qWrsPkAkmbBs9ia2uuqG_-xCf-
"""

# install library
!pip install weaviate-client
!pip install langchain
!pip install openai

# https://console.weaviate.cloud/

from google.colab import userdata
OPENAI_API_KEY = userdata.get('OPENAI_API_KEY')

import os
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

WEAVIATE_API_KEY = "WEAVIATE_API_KEY"
WEAVIATE_CLUSTER = "https://test-2yjc7es1.weaviate.network"

"""# Data Reading"""

!pip install unstructured
!pip install "unstructured[pdf]"

!mkdir data

!pip install pypdf

!pip install pypdf

from langchain.document_loaders import PyPDFDirectoryLoader
loader = PyPDFDirectoryLoader("data") # import yolo.pdf  from data folder
data = loader.load()

data

"""# Text Spliting and Chunkins"""

from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
docs = text_splitter.split_documents(data)

docs # chunk docs

len(docs)

"""# Embedding Convertion"""

from langchain.embeddings.openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(openai_api_key = OPENAI_API_KEY) # we can use free embadding by using sentence transformer

embeddings

"""# Vector Database Storage"""

import weaviate
from langchain.vectorstores import Weaviate

#Connect to weaviate Cluster
auth_config = weaviate.auth.AuthApiKey(api_key = WEAVIATE_API_KEY)
WEAVIATE_URL = WEAVIATE_CLUSTER

client = weaviate.Client(
    url = WEAVIATE_URL,
    additional_headers = {"X-OpenAI-Api-key": OPENAI_API_KEY},
    auth_client_secret = auth_config,
    startup_period = 10
)

client.is_ready()

# define input structure
client.schema.delete_all()
client.schema.get()
schema = {
    "classes": [
        {
            "class": "Chatbot",
            "description": "Documents for chatbot",
            "vectorizer": "text2vec-openai",
            "moduleConfig": {"text2vec-openai": {"model": "ada", "type": "text"}},
            "properties": [
                {
                    "dataType": ["text"],
                    "description": "The content of the paragraph",
                    "moduleConfig": {
                        "text2vec-openai": {
                            "skip": False,
                            "vectorizePropertyName": False,
                        }
                    },
                    "name": "content",
                },
            ],
        },
    ]
}

client.schema.create(schema)
vectorstore = Weaviate(client, "Chatbot", "content", attributes=["source"])

# load text into the vectorstore
text_meta_pair = [(doc.page_content, doc.metadata) for doc in docs]
texts, meta = list(zip(*text_meta_pair))
vectorstore.add_texts(texts, meta)

"""# Similarity Measuerment"""

query = "what is a correlation?"

# retrieve text related to the query
docs = vectorstore.similarity_search(query, top_k=3)

docs

"""# Custom chatbot"""

from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI

# define chain
chain = load_qa_chain(
    OpenAI(),
    chain_type="stuff")

# create answer
chain.run(input_documents=docs, question=query)