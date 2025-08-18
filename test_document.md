# Alnitak RAG Assistant

Alnitak is a personal Retrieval-Augmented Generation (RAG) assistant that helps you answer questions based on your own documents.

## Features

- **Local LLM Integration**: Uses Ollama for running local language models
- **Vector Database**: ChromaDB for efficient document storage and retrieval
- **Multiple File Formats**: Supports text, Markdown, and PDF files
- **RESTful API**: Flask-based API with `/ask` endpoint
- **Smart Chunking**: Intelligent text chunking with overlap for better retrieval
- **CPU-Friendly**: Uses sentence-transformers for embeddings (no GPU required)

## How it works

1. Documents are ingested and chunked into smaller pieces
2. Each chunk is embedded using sentence-transformers
3. When you ask a question, it finds the most relevant chunks
4. The LLM generates an answer based on the retrieved context

This ensures that answers are grounded in your actual documents rather than just general knowledge.

## Architecture

The system consists of three main components:

1. **Document Ingestion** (`ingest.py`): Handles loading and processing documents
2. **RAG Assistant** (`qa.py`): Core logic for retrieval and generation
3. **Flask API** (`app.py`): RESTful interface for asking questions

## Usage

1. Ingest your documents using the CLI
2. Start the Flask server
3. Ask questions via the API
4. Get grounded answers based on your documents
