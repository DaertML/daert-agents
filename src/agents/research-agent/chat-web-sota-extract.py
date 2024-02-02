import warnings
from langchain_core._api import LangChainDeprecationWarning

warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)

import asyncio

from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")

from langchain.utils.openai_functions import convert_pydantic_to_openai_function
from pydantic import BaseModel, Field
from typing import Optional
from typing import List
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain.output_parsers.openai_functions import JsonKeyOutputFunctionsParser
from langchain_experimental.llms.ollama_functions import OllamaFunctions
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema.runnable import RunnableLambda
from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

DEBUG=1
VERBOSE=0
def text_to_token_list(text, tokenizer, size):
  tokens = tokenizer.encode(text)
  num_tokens = len(tokens)
  token_list = []

  for i in range(0, num_tokens, size):
    sub_string = tokenizer.decode(tokens[i:i+size])
    token_list.append(sub_string)

  return token_list

def flatten(matrix):
    flat_list = []
    for row in matrix:
        flat_list += row
    return flat_list

class Overview(BaseModel):
    """Overview of a section of text."""
    summary: str = Field(description="Provide a concise summary of the content.")
    language: str = Field(description="Provide the language that the content is written in.")
    keywords: str = Field(description="Provide keywords related to the content.")

class Paper(BaseModel):
    """Information about papers mentioned."""
    title: str
    author: Optional[str]

class Info(BaseModel):
    """Information to extract"""
    papers: List[Paper]

class InfoStr(BaseModel):
    """Information to extract"""
    papers: str

model_extract = OllamaFunctions(model="mistrallim")

template = """A article will be passed to you. Extract from it all papers that are mentioned by this article. 

Do not extract the name of the article itself. If no papers are mentioned that's fine - you don't need to extract any! Just return an empty list.

Do not make up or guess ANY extra information. Only extract what exactly is in the text."""

paper_extraction_function = [
    convert_pydantic_to_openai_function(Info),
    convert_pydantic_to_openai_function(InfoStr)
]

prompt = ChatPromptTemplate.from_messages([
    ("system", template),
    ("human", "{input}")
])

def launch_chain(X):
   if DEBUG:
     print("[DBG] Launching Main Chain with another Text Chunk")
   return [{"input": X}]

def hydrate_prompt(k):
  if DEBUG:
    print("[DBG] Hydrating prompt with input data")
  return k

def start_extraction(i):
  if DEBUG:
    print("[DBG] Starting the Extraction Chain")
  return i

def model_run(i):
  if DEBUG:
    print("[DBG] Running LLM inference")
  return i

def extract_json(i):
  if DEBUG:
    print("[DBG] Extracting JSON data from the generation")
  return i

def print_result(i):
  if DEBUG:
    print("[DBG] Result of the generation")
    print(i)
  return i

#json_extraction_chain = hydrate_prompt | prompt | model_run | model_extract | extract_json | JsonKeyOutputFunctionsParser(key_name="papers") | print_result
extraction_chain = hydrate_prompt | prompt | model_run | model_extract | print_result

while True: 
  url = input("Let's hunt those SOTA papers! Where are we headed?")
  loader = WebBaseLoader(url)
  documents = loader.load()
  doc = documents[0]

  text_splitter = RecursiveCharacterTextSplitter(chunk_overlap=0)
  splits = text_splitter.split_text(doc.page_content)

  prep = RunnableLambda(
      lambda x: launch_chain(x)
  )

  chain = prep | start_extraction | extraction_chain.map() #| flatten

  import time
  async def run():
    for elem in splits:
      if DEBUG and VERBOSE:
        print("Launching with this text chunk\n", elem)

      tokens = tokenizer.encode(elem)
      num_tokens = len(tokens)

      res = await chain.ainvoke(elem)
      
      # Sleep in order to avoid hanging the Ollama server
      time.sleep(10)

  asyncio.run(run())