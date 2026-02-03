import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
from bs4 import BeautifulSoup
# import markdown
from typing import List, Dict
import hashlib
from dotenv import load_dotenv
import sys

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
INDEX_NAME = os.getenv("INDEX_NAME", "terraform-aws-docs-1")


def batch(iterable,size):
    for i in range(0,len(iterable),size):
        yield(iterable[i:i+size])





def Pinecone_embedding(content):
    """
    Docstring for Pinecone_embedding
    This function convert text into pinecone embeddings 
    :param content: Description
    """
   
    pc = Pinecone(api_key=PINECONE_API_KEY)
    if not pc.has_index(INDEX_NAME):
        pc.create_index_for_model(
        name=INDEX_NAME,
        cloud="aws",
        region=PINECONE_ENVIRONMENT,
        embed={
            "model":"llama-text-embed-v2",
            "field_map":{"text": "chunk_text"}
        }
    )
    dense_index = pc.Index(INDEX_NAME)
    BATCH_SIZE = 50

    for chunk in batch(content,BATCH_SIZE):
        print(chunk)
        break
        # dense_index.upsert_records(
        #                         namespace="example-namespace", 
        #                            records=chunk)



def embed_and_upload(DOCS_FOLDER:str):
    """
    Docstring for embed_and_uploadd
    This function goes through the folder and convert it into embedding


    :param DOCS_FOLDER: Description
    :type DOCS_FOLDER: str
    """
  
    source_dir = Path(DOCS_FOLDER+"/r")
    files = source_dir.glob("**.html")

    file_patterns = ['**/*.html', '**/*.htm', '**/*.md', '**/*.markdown']
    all_files = []
    
    for pattern in file_patterns:
        all_files.extend(source_dir.glob(pattern))

    print(f"Found {len(all_files)} are files for process")
    
    All_data_from_file = []

    for i,file in enumerate(all_files):
        with file.open('r', encoding='utf-8') as file_handle:
            id= str(file)
            content = {"_id":id[49:],
                       "chunk_text":file_handle.read()}
            
            All_data_from_file.append(content)
    

    Pinecone_embedding(All_data_from_file)

    pass



if __name__=="__main__":

    DOCS_FOLDER =  "D:/RAG_IaC/terraform-provider-aws/website/docs"

    embed_and_upload(DOCS_FOLDER)