import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import pypdf
import markdown
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentIngester:
    """
    Handles ingestion of documents into ChromaDB for the RAG system.
    Supports text, Markdown, and PDF files.
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize the document ingester.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        self.persist_directory = persist_directory
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="alnitak_documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"Initialized DocumentIngester with ChromaDB at {persist_directory}")
    
    def load_text_file(self, file_path: str) -> str:
        """Load content from a text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error loading text file {file_path}: {e}")
            raise
    
    def load_markdown_file(self, file_path: str) -> str:
        """Load content from a Markdown file and convert to plain text."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                md_content = file.read()
                # Convert markdown to HTML, then extract text
                html = markdown.markdown(md_content)
                # Simple HTML tag removal (for basic cases)
                import re
                text = re.sub(r'<[^>]+>', '', html)
                return text
        except Exception as e:
            logger.error(f"Error loading markdown file {file_path}: {e}")
            raise
    
    def load_pdf_file(self, file_path: str) -> str:
        """Load content from a PDF file."""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error loading PDF file {file_path}: {e}")
            raise
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks for better retrieval.
        
        Args:
            text: The text to chunk
            chunk_size: Maximum size of each chunk
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # If this isn't the last chunk, try to break at a sentence boundary
            if end < len(text):
                # Look for sentence endings near the end
                for i in range(end, max(start + chunk_size - 100, start), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position, accounting for overlap
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    def ingest_file(self, file_path: str, metadata: Dict[str, Any] = None) -> int:
        """
        Ingest a single file into the vector database.
        
        Args:
            file_path: Path to the file to ingest
            metadata: Optional metadata to associate with the document
            
        Returns:
            Number of chunks created
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Determine file type and load content
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.txt':
            content = self.load_text_file(file_path)
        elif file_ext in ['.md', '.markdown']:
            content = self.load_markdown_file(file_path)
        elif file_ext == '.pdf':
            content = self.load_pdf_file(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
        
        # Chunk the content
        chunks = self.chunk_text(content)
        
        # Prepare metadata
        if metadata is None:
            metadata = {}
        
        base_metadata = {
            'source': file_path,
            'file_type': file_ext,
            'total_chunks': len(chunks)
        }
        base_metadata.update(metadata)
        
        # Add chunks to ChromaDB
        for i, chunk in enumerate(chunks):
            chunk_metadata = base_metadata.copy()
            chunk_metadata['chunk_index'] = i
            
            self.collection.add(
                documents=[chunk],
                metadatas=[chunk_metadata],
                ids=[f"{os.path.basename(file_path)}_{i}"]
            )
        
        logger.info(f"Ingested {len(chunks)} chunks from {file_path}")
        return len(chunks)
    
    def ingest_directory(self, directory_path: str, file_extensions: List[str] = None) -> Dict[str, int]:
        """
        Ingest all supported files from a directory.
        
        Args:
            directory_path: Path to the directory
            file_extensions: List of file extensions to process (default: all supported)
            
        Returns:
            Dictionary mapping file paths to number of chunks created
        """
        if file_extensions is None:
            file_extensions = ['.txt', '.md', '.markdown', '.pdf']
        
        results = {}
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                
                if file_ext in file_extensions:
                    try:
                        chunks_count = self.ingest_file(file_path)
                        results[file_path] = chunks_count
                    except Exception as e:
                        logger.error(f"Failed to ingest {file_path}: {e}")
                        results[file_path] = 0
        
        return results
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the current collection."""
        count = self.collection.count()
        return {
            'total_documents': count,
            'collection_name': self.collection.name,
            'persist_directory': self.persist_directory
        }
    
    def reset_collection(self):
        """Reset the collection (delete all documents)."""
        self.client.delete_collection("alnitak_documents")
        self.collection = self.client.create_collection(
            name="alnitak_documents",
            metadata={"hnsw:space": "cosine"}
        )
        logger.info("Collection reset successfully")

# Convenience function for quick ingestion
def ingest_documents(file_paths: List[str] = None, directory_path: str = None) -> DocumentIngester:
    """
    Convenience function to quickly ingest documents.
    
    Args:
        file_paths: List of specific file paths to ingest
        directory_path: Directory path to ingest all supported files from
        
    Returns:
        Initialized DocumentIngester instance
    """
    ingester = DocumentIngester()
    
    if file_paths:
        for file_path in file_paths:
            try:
                ingester.ingest_file(file_path)
            except Exception as e:
                logger.error(f"Failed to ingest {file_path}: {e}")
    
    if directory_path:
        ingester.ingest_directory(directory_path)
    
    return ingester
