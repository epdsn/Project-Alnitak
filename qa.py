import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import requests
import json
from typing import List, Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGAssistant:
    """
    Main RAG assistant that combines document retrieval with LLM generation.
    Uses ChromaDB for retrieval and Ollama for text generation.
    """
    
    def __init__(self, 
                 ollama_url: str = "http://localhost:11434",
                 model_name: str = "llama3:8b",
                 persist_directory: str = "./chroma_db",
                 top_k: int = 5):
        """
        Initialize the RAG assistant.
        
        Args:
            ollama_url: URL of the Ollama server
            model_name: Name of the model to use (must be available in Ollama)
            persist_directory: Directory where ChromaDB data is stored
            top_k: Number of most relevant documents to retrieve
        """
        self.ollama_url = ollama_url
        self.model_name = model_name
        self.top_k = top_k
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get the collection
        try:
            self.collection = self.client.get_collection("alnitak_documents")
            logger.info(f"Connected to existing ChromaDB collection")
        except:
            logger.warning("No existing collection found. You'll need to ingest documents first.")
            self.collection = None
        
        # Test Ollama connection
        self._test_ollama_connection()
        
        logger.info(f"RAG Assistant initialized with model: {model_name}")
    
    def _test_ollama_connection(self):
        """Test connection to Ollama server."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                if self.model_name not in model_names:
                    logger.warning(f"Model '{self.model_name}' not found in Ollama. Available models: {model_names}")
                else:
                    logger.info(f"Successfully connected to Ollama with model: {self.model_name}")
            else:
                logger.error(f"Failed to connect to Ollama: {response.status_code}")
        except Exception as e:
            logger.error(f"Could not connect to Ollama at {self.ollama_url}: {e}")
            logger.error("Make sure Ollama is running and the model is available")
    
    def _get_embeddings(self, text: str) -> List[float]:
        """Get embeddings for a text using sentence-transformers."""
        return self.embedding_model.encode(text).tolist()
    
    def _retrieve_relevant_documents(self, question: str) -> List[Dict[str, Any]]:
        """
        Retrieve the most relevant documents for a given question.
        
        Args:
            question: The question to find relevant documents for
            
        Returns:
            List of relevant documents with their metadata
        """
        if not self.collection:
            logger.warning("No documents available for retrieval. Please ingest documents first.")
            return []
        
        try:
            # Get embeddings for the question
            question_embeddings = self._get_embeddings(question)
            
            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[question_embeddings],
                n_results=self.top_k,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            documents = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    documents.append({
                        'content': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {},
                        'distance': results['distances'][0][i] if results['distances'] and results['distances'][0] else 0.0
                    })
            
            logger.info(f"Retrieved {len(documents)} relevant documents")
            return documents
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []
    
    def _generate_answer(self, question: str, context_documents: List[Dict[str, Any]]) -> str:
        """
        Generate an answer using Ollama based on the question and retrieved context.
        
        Args:
            question: The user's question
            context_documents: List of relevant documents retrieved from the vector database
            
        Returns:
            Generated answer
        """
        if not context_documents:
            return "I don't have enough information to answer that question. Please make sure you have ingested relevant documents."
        
        # Prepare context from retrieved documents
        context = "\n\n".join([doc['content'] for doc in context_documents])
        
        # Create the prompt
        prompt = f"""You are Alnitak, a helpful AI assistant. Answer the user's question based on the provided context. 
If the context doesn't contain enough information to answer the question, say so clearly.

Context:
{context}

Question: {question}

Answer:"""
        
        try:
            # Call Ollama API
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 1000
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get('response', '').strip()
                return answer
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return f"Error generating answer: {response.status_code}"
                
        except requests.exceptions.Timeout:
            logger.error("Timeout while calling Ollama API")
            return "Sorry, the request timed out. Please try again."
        except Exception as e:
            logger.error(f"Error calling Ollama API: {e}")
            return f"Error generating answer: {str(e)}"
    
    def ask(self, question: str) -> str:
        """
        Main method to ask a question and get an answer.
        
        Args:
            question: The question to ask
            
        Returns:
            The generated answer
        """
        if not question.strip():
            return "Please provide a question."
        
        logger.info(f"Processing question: {question}")
        
        # Step 1: Retrieve relevant documents
        relevant_docs = self._retrieve_relevant_documents(question)
        
        # Step 2: Generate answer using the retrieved context
        answer = self._generate_answer(question, relevant_docs)
        
        return answer
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the current document collection."""
        if not self.collection:
            return {"error": "No collection available"}
        
        try:
            count = self.collection.count()
            return {
                'total_documents': count,
                'collection_name': self.collection.name,
                'model_name': self.model_name,
                'ollama_url': self.ollama_url
            }
        except Exception as e:
            return {"error": f"Could not get collection info: {e}"}
    
    def list_available_models(self) -> List[str]:
        """List available models in Ollama."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [model['name'] for model in models]
            else:
                return []
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []

# Convenience function for quick testing
def test_rag_assistant(question: str = "What is this project about?") -> str:
    """
    Quick test function for the RAG assistant.
    
    Args:
        question: Test question to ask
        
    Returns:
        The answer
    """
    assistant = RAGAssistant()
    return assistant.ask(question)
