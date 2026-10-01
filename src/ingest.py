"""Ingere um PDF no PostgreSQL usando LangChain + pgVector."""
from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter
from search import get_embeddings
ROOT_DIR=Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")
PDF_PATH=ROOT_DIR / os.getenv("PDF_PATH","document.pdf")
DATABASE_URL=os.getenv("DATABASE_URL","postgresql+psycopg://postgres:postgres@localhost:5432/rag")
COLLECTION_NAME=os.getenv("PG_VECTOR_COLLECTION_NAME","pdf_documents")
RESET_COLLECTION=os.getenv("RESET_COLLECTION","true").lower()=="true"
def ingest()->None:
    if not PDF_PATH.exists(): raise FileNotFoundError(f"PDF não encontrado: {PDF_PATH}")
    pages=PyPDFLoader(str(PDF_PATH)).load()
    splitter=RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=150,length_function=len)
    chunks=splitter.split_documents(pages)
    if not chunks: raise ValueError("O PDF não contém texto que possa ser ingerido.")
    for i,chunk in enumerate(chunks):
        chunk.metadata["chunk_index"]=i; chunk.metadata["source"]=PDF_PATH.name
    print(f"Páginas carregadas: {len(pages)}")
    print(f"Chunks gerados: {len(chunks)} (1000 chars / overlap 150)")
    store=PGVector(embeddings=get_embeddings(),collection_name=COLLECTION_NAME,connection=DATABASE_URL,use_jsonb=True)
    if RESET_COLLECTION:
        store.delete_collection()
        store=PGVector(embeddings=get_embeddings(),collection_name=COLLECTION_NAME,connection=DATABASE_URL,use_jsonb=True)
    store.add_documents(chunks)
    print("Ingestão concluída com sucesso.")
if __name__=="__main__": ingest()
