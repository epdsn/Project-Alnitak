# 🌟 Alnitak - Your Personal RAG Assistant

> **"Alnitak"** - Named after the brightest star in Orion's Belt, your personal AI assistant that illuminates answers from your own knowledge base.

A powerful, local Retrieval-Augmented Generation (RAG) assistant that answers questions based on your documents using Ollama, ChromaDB, and sentence-transformers. **No cloud dependencies, no data leaks, just your documents and your local AI.**

## ✨ Features

### 🚀 **Core Capabilities**
- **🔒 100% Local** - Everything runs on your machine, no data leaves your system
- **📚 Multi-Format Support** - Handles text, Markdown, and PDF files seamlessly
- **🧠 Smart Retrieval** - Intelligent document chunking with semantic search
- **⚡ Fast & Efficient** - CPU-friendly embeddings with sentence-transformers
- **🔄 RESTful API** - Clean Flask API for easy integration

### 🛠 **Technical Stack**
- **Local LLM**: Ollama with llama3:8b (or any model you prefer)
- **Vector Database**: ChromaDB for lightning-fast document retrieval
- **Embeddings**: Sentence-transformers (all-MiniLM-L6-v2)
- **API Framework**: Flask with JSON endpoints
- **Document Processing**: Smart chunking with overlap for better context

### 📊 **What Makes Alnitak Special**
- **Grounded Answers** - Responses are based on your actual documents, not generic knowledge
- **Modular Design** - Easy to extend and customize
- **Production Ready** - Built with error handling and logging
- **Cross-Platform** - Works on macOS, Linux, and Windows

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+**
- **Ollama** - [Download from ollama.ai](https://ollama.ai)
- **4GB+ RAM** (for the 8B model)

### 1. Installation

```bash
# Clone the repository
git clone <your-repo>
cd Project-Alnitak

# Install dependencies
pip install -r requirements.txt

# Install and start Ollama
brew install ollama  # macOS
# or download from https://ollama.ai for other platforms
brew services start ollama

# Download a model
ollama pull llama3:8b
```

### 2. Add Your Documents

```bash
# Create a documents folder
mkdir documents

# Add your files (supports .txt, .md, .pdf)
# Example:
echo "# My Notes\nThis is important information." > documents/notes.md

# Ingest all documents
python3 ingest_cli.py --directory ./documents
```

### 3. Start the Assistant

```bash
# Start the API server (use port 5001 on macOS to avoid AirPlay conflicts)
PORT=5001 python3 app.py
```

### 4. Ask Questions

```bash
# Test the API
curl -X POST http://localhost:5001/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is in my documents?"}'
```

## 📖 Usage Guide

### Document Ingestion

**Ingest a single file:**
```bash
python3 ingest_cli.py --file document.pdf
```

**Ingest multiple files:**
```bash
python3 ingest_cli.py --file doc1.txt --file doc2.md --file doc3.pdf
```

**Ingest entire directory:**
```bash
python3 ingest_cli.py --directory ./documents
```

**Reset and re-ingest:**
```bash
python3 ingest_cli.py --reset --directory ./documents
```

**Check collection status:**
```bash
python3 ingest_cli.py --info
```

### API Endpoints

#### `POST /ask` - Ask a Question
```bash
curl -X POST http://localhost:5001/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the main topics in my documents?"}'
```

**Response:**
```json
{
  "question": "What are the main topics in my documents?",
  "answer": "Based on your documents, the main topics are...",
  "status": "success"
}
```

#### `GET /health` - Health Check
```bash
curl http://localhost:5001/health
```

#### `GET /` - API Information
```bash
curl http://localhost:5001/
```

### Testing Your Setup

Run the comprehensive test suite:
```bash
python3 test_alnitak.py
```

Or run a quick Ollama test:
```bash
python3 simple_test.py
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file for customization:

```env
# Flask settings
PORT=5001
FLASK_DEBUG=False

# Ollama settings
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3:8b

# ChromaDB settings
CHROMA_PERSIST_DIR=./chroma_db
```

### Model Selection

**Use a different Ollama model:**
```bash
# Download a different model
ollama pull mistral
ollama pull llama3.2:3b

# Update the model in code
# Edit qa.py and change model_name="mistral"
```

**Available models to try:**
- `llama3:8b` - Good balance of speed and quality
- `llama3.2:3b` - Faster, smaller model
- `mistral` - Excellent reasoning capabilities
- `codellama` - Great for code-related documents

## 📁 Project Structure

```
Project-Alnitak/
├── app.py              # 🚀 Flask API server
├── qa.py               # 🧠 RAG assistant core logic
├── ingest.py           # 📚 Document ingestion module
├── ingest_cli.py       # 💻 CLI for document ingestion
├── requirements.txt    # 📦 Python dependencies
├── test_alnitak.py     # 🧪 Comprehensive test suite
├── simple_test.py      # ⚡ Quick Ollama test
├── README.md          # 📖 This file
├── test_document.md   # 📄 Example document
├── .gitignore         # 🚫 Git exclusions
└── chroma_db/         # 🗄️ ChromaDB data (auto-created)
```

## 🎯 Use Cases

### 📚 **Research & Documentation**
- Ask questions about research papers
- Query technical documentation
- Search through meeting notes

### 💼 **Business & Productivity**
- Company knowledge base queries
- Policy and procedure lookups
- Project documentation search

### 🎓 **Learning & Education**
- Study material Q&A
- Textbook question answering
- Course note retrieval

### 💻 **Development**
- Code documentation search
- API reference queries
- Technical blog post analysis

## 🔍 How It Works

1. **📥 Document Ingestion**
   - Documents are loaded and processed
   - Text is intelligently chunked with overlap
   - Each chunk is embedded using sentence-transformers

2. **🗄️ Vector Storage**
   - Embeddings are stored in ChromaDB
   - Metadata is preserved for context
   - Fast similarity search enabled

3. **❓ Question Processing**
   - Your question is embedded
   - Similar document chunks are retrieved
   - Context is prepared for the LLM

4. **🤖 Answer Generation**
   - Ollama generates grounded responses
   - Answers are based on your actual documents
   - No hallucination, just your knowledge

## 🛠️ Development

### Running Tests
```bash
# Full test suite
python3 test_alnitak.py

# Quick Ollama test
python3 simple_test.py

# Manual RAG test
python3 -c "from qa import RAGAssistant; a = RAGAssistant(); print(a.ask('Test question'))"
```

### Debugging
```bash
# Enable debug mode
FLASK_DEBUG=true python3 app.py

# Check logs for detailed information
# All components use Python logging
```

### Extending Alnitak

**Add new file formats:**
- Edit `ingest.py` and add new file handlers
- Implement `load_<format>_file()` method

**Customize the RAG pipeline:**
- Modify `qa.py` for different retrieval strategies
- Adjust chunking parameters in `ingest.py`

**Add new API endpoints:**
- Extend `app.py` with new Flask routes
- Integrate with external services

## 🆘 Troubleshooting

### Common Issues

**❌ Ollama connection failed**
```bash
# Check if Ollama is running
ollama list

# Start Ollama service
brew services start ollama  # macOS
ollama serve               # Manual start
```

**❌ Port 5000 in use (macOS)**
```bash
# Use a different port
PORT=5001 python3 app.py

# Or disable AirPlay Receiver in System Preferences
```

**❌ Model not found**
```bash
# Check available models
ollama list

# Download the model
ollama pull llama3:8b
```

**❌ Import errors**
```bash
# Reinstall dependencies
pip3 install -r requirements.txt

# Check Python version (needs 3.11+)
python3 --version
```

**❌ No documents found**
```bash
# Check collection status
python3 ingest_cli.py --info

# Ingest documents first
python3 ingest_cli.py --directory ./documents
```

### Performance Tips

- **Use smaller models** for faster responses
- **Reduce `top_k`** parameter for faster retrieval
- **Use SSD storage** for better ChromaDB performance
- **Consider GPU** for sentence-transformers if available

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is open source. Feel free to use and modify as needed.

## 🙏 Acknowledgments

- **Ollama** - For making local LLMs accessible
- **ChromaDB** - For the excellent vector database
- **Sentence-Transformers** - For CPU-friendly embeddings
- **Flask** - For the simple, powerful web framework

---

## 🌟 **Ready to Illuminate Your Knowledge?**

Your Alnitak RAG assistant is ready to help you find answers in your documents. Start by adding your files and asking questions - you'll be amazed at how much knowledge is hidden in your documents!

**Happy querying! 🚀**

---

*Alnitak - Shining light on your knowledge, one question at a time.*