import os
import re
from typing import List, Optional
import traceback
from loguru import logger
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.vectorstores import FAISS
from langchain.document_loaders import TextLoader

# Search engine related. You don't really need to change this.
BING_SEARCH_V7_ENDPOINT = "https://api.bing.microsoft.com/v7.0/search"
BING_MKT = "en-US"
GOOGLE_SEARCH_ENDPOINT = "https://customsearch.googleapis.com/customsearch/v1"

# Specify the number of references from the search engine you want to use.
# 8 is usually a good number.
REFERENCE_COUNT = 8

# Specify the default timeout for the search engine. If the search engine
# does not respond within this time, we will return an error.
DEFAULT_SEARCH_ENGINE_TIMEOUT = 5

# If the user did not provide a query, we will use this default query.
_default_query = "Who said 'live long and prosper'?"

# This is really the most important part of the rag model. It gives instructions
# to the model on how to generate the answer. Of course, different models may
# behave differently, and we haven't tuned the prompt to make it optimal - this
# is left to you, application creators, as an open problem.
_rag_query_text = """You are a large language AI assistant. You are given a user question, and please write clean, concise and accurate answer to the question. You will be given a set of related contexts to the question, each starting with a reference number like [[citation:x]], where x is a number. Please use the context and cite the context at the end of each sentence if applicable.

Your answer must be correct, accurate and written by an expert using an unbiased and professional tone. Please limit to 1024 tokens. Do not give any information that is not related to the question, and do not repeat. Say "information is missing on" followed by the related topic, if the given context do not provide sufficient information.

Please cite the contexts with the reference numbers, in the format [citation:x]. If a sentence comes from multiple contexts, please list all applicable citations, like [citation:3][citation:5]. Other than code and specific names and citations, your answer must be written in the same language as the question.

Here are the set of contexts:
{context}

Remember, don't blindly repeat the contexts verbatim. And here is the user question:"""

# A set of stop words to use - this is not a complete set, and you may want to
# add more given your observation.
stop_words = [
    "<|im_end|>",
    "[End]",
    "[end]",
    "\nReferences:\n",
    "\nSources:\n",
    "End.",
]


def search_with_bing(query: str, subscription_key: str):
    """
    Search with bing and return the contexts.
    """
    # ... (Implementation similar to Lepton code)


def search_with_google(query: str, subscription_key: str, cx: str):
    """
    Search with google and return the contexts.
    """
    # ... (Implementation similar to Lepton code)


class RAG:
    """
    Retrieval-Augmented Generation Demo using LangChain.
    """
    
    def __init__(self):
        self.backend = os.environ.get("BACKEND", "BING").upper()
        if self.backend == "BING":
            self.search_api_key = os.environ["BING_SEARCH_V7_SUBSCRIPTION_KEY"]
            self.search_function = lambda query: search_with_bing(
                query, self.search_api_key
            )
        elif self.backend == "GOOGLE":
            self.search_api_key = os.environ["GOOGLE_SEARCH_API_KEY"]
            self.search_function = lambda query: search_with_google(
                query, self.search_api_key, os.environ["GOOGLE_SEARCH_CX"]
            )
        else:
            raise RuntimeError("Backend must be BING or GOOGLE.")

        self.llm = OpenAI(temperature=0.9)
        self.prompt = PromptTemplate(
            input_variables=["context", "query"], template=_rag_query_text
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def query(self, query: str, search_uuid: Optional[str] = None) -> str:
        """
        Query the search engine and returns the response.
        """
        # ... (Logic for checking search_uuid and using cached results)

        query = query or _default_query
        # Basic attack protection: remove "[INST]" or "[/INST]" from the query
        query = re.sub(r"\[/?INST\]", "", query)

        contexts = self.search_function(query)
        # Create documents from contexts
        documents = [
            {"text": c["snippet"], "metadata": {"citation": i + 1}}
            for i, c in enumerate(contexts)
        ]

        # Create vector store from documents
        vectorstore = FAISS.from_documents(documents, metadata={"source": "search"})

        # Run RAG query
        result = self.chain.run(query, vectorstore)

        return result


app = FastAPI()
rag = RAG()


@app.post("/query")
def query_function(query: str, search_uuid: Optional[str] = None):
    """
    Query the RAG model and return the response.
    """
    try:
        result = rag.query(query, search_uuid)
        return StreamingResponse(content=result, media_type="text/html")
    except Exception as e:
        logger.error(f"encountered error: {e}\n{traceback.format_exc()}")
        return HTMLResponse("Internal server error.", 503)


# ... (UI and index route implementation similar to Lepton code)
    
import os
import re
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.vectorstores import FAISS
from langchain.document_loaders import TextLoader, WebBaseLoader

# ... (Other constants and functions remain the same)


class RAG:
    """
    Retrieval-Augmented Generation Demo using LangChain with snippet ranking.
    """

    # ... (Other methods remain the same)

    def query(self, query: str, search_uuid: Optional[str] = None) -> str:
        """
        Query the search engine, rank snippets, and return the response.
        """
        # ... (Logic for checking search_uuid and using cached results)

        query = query or _default_query
        # Basic attack protection: remove "[INST]" or "[/INST]" from the query
        query = re.sub(r"\[/?INST\]", "", query)

        contexts = self.search_function(query)
        
        # Rank snippets based on relevance
        ranked_contexts = self.rank_snippets(query, contexts)

        # Load content of top N relevant URLs
        top_n = 3  # Adjust this value as needed
        documents = []
        for context in ranked_contexts[:top_n]:
            url = context["url"]
            try:
                loader = WebBaseLoader(url)
                document = loader.load()
                documents.append(document)
            except Exception as e:
                logger.error(f"Error loading URL {url}: {e}")

        # Create vector store from documents
        vectorstore = FAISS.from_documents(documents, metadata={"source": "web"})
        
        # Run RAG query
        result = self.chain.run(query, vectorstore)

        return result

    def rank_snippets(self, query: str, contexts: List[dict]) -> List[dict]:
        """
        Rank snippets based on relevance to the search query.
        """
        # You can implement your own ranking logic here.
        # For example, you could use a separate LLM to score each snippet
        # based on its relevance to the query.
        # For simplicity, this example just returns the contexts in their original order.
        return contexts


# ... (Rest of the code remains the same)