"""Busca semântica no PostgreSQL/pgVector."""
from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_core.documents import Document
ROOT_DIR=Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")
DATABASE_URL=os.getenv("DATABASE_URL","postgresql+psycopg://postgres:postgres@localhost:5432/rag")
COLLECTION_NAME=os.getenv("PG_VECTOR_COLLECTION_NAME","pdf_documents")
EMBEDDING_MODEL=os.getenv("OPENAI_EMBEDDING_MODEL","text-embedding-3-small")
def get_embeddings()->OpenAIEmbeddings: return OpenAIEmbeddings(model=EMBEDDING_MODEL)
def get_vector_store()->PGVector:
    return PGVector(embeddings=get_embeddings(),collection_name=COLLECTION_NAME,connection=DATABASE_URL,use_jsonb=True)
def search(query:str,k:int=10)->list[tuple[Document,float]]:
    return get_vector_store().similarity_search_with_score(query,k=k)
