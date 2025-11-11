"""
Build FAISS Index for NovaCRM Knowledge Base

This script:
1. Loads all markdown documents from data/kb/
2. Splits them into chunks using RecursiveCharacterTextSplitter
3. Creates embeddings using OpenAI
4. Builds and saves a FAISS index for semantic search
"""

import os
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

BASE_DIR = Path(__file__).resolve().parent.parent
KB_PATH = BASE_DIR / "data" / "kb"
INDEX_PATH = BASE_DIR / "index"

def build_index():
    """
    Build FAISS index from knowledge base markdown files
    """
    print("=" * 60)
    print("Building FAISS Index for NovaCRM Knowledge Base")
    print("=" * 60)
    
    if not KB_PATH.exists():
        print(f"ERROR: Knowledge base path not found: {KB_PATH}")
        return
    
    print(f"Loading documents from: {KB_PATH}")
    
    loader = DirectoryLoader(
        str(KB_PATH),
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    documents = loader.load()
    
    print(f"Loaded {len(documents)} documents")
    
    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    
    print(f"Created {len(chunks)} chunks")
    
    print("Creating embeddings and building FAISS index...")
    embeddings = OpenAIEmbeddings()
    
    vectorstore = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings
    )
    
    INDEX_PATH.mkdir(parents=True, exist_ok=True)
    index_file = INDEX_PATH / "faiss_index"
    
    print(f"Saving index to: {index_file}")
    vectorstore.save_local(str(index_file))
    
    print("=" * 60)
    print("FAISS Index built successfully!")
    print(f"Index location: {index_file}")
    print(f"Total chunks indexed: {len(chunks)}")
    print("=" * 60)

if __name__ == "__main__":
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv())
    
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not found in environment")
        print("Please set it in .env file or environment variables")
        exit(1)
    
    build_index()

