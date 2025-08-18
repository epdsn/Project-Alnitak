from flask import Flask, request, jsonify
from qa import RAGAssistant
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize the RAG assistant
rag_assistant = RAGAssistant()

@app.route('/ask', methods=['POST'])
def ask():
    """
    Main endpoint for asking questions to the RAG assistant.
    Expects JSON with 'question' field.
    """
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({
                'error': 'Missing question in request body'
            }), 400
        
        question = data['question']
        
        if not question.strip():
            return jsonify({
                'error': 'Question cannot be empty'
            }), 400
        
        # Get answer from RAG assistant
        answer = rag_assistant.ask(question)
        
        return jsonify({
            'question': question,
            'answer': answer,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'An error occurred: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Alnitak RAG Assistant'
    })

@app.route('/', methods=['GET'])
def home():
    """Home endpoint with basic usage information"""
    return jsonify({
        'service': 'Alnitak RAG Assistant',
        'endpoints': {
            'POST /ask': 'Ask a question (send JSON with "question" field)',
            'GET /health': 'Health check',
            'GET /': 'This information'
        },
        'example': {
            'curl': 'curl -X POST http://localhost:5000/ask -H "Content-Type: application/json" -d \'{"question": "What is this project about?"}\''
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print("🚀 Starting Alnitak RAG Assistant...")
    print(f"📡 Server will run on http://localhost:{port}")
    print("💡 Use POST /ask to ask questions")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
