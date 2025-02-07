from flask import Flask, request, render_template, jsonify
from models.vector_store import VectorStore
from services.storage_service import S3Storage
from services.llm_service import LLMService
from config import Config
import os
import shutil
import logging
import tempfile
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# ✅ Updated Import for ChromaDB
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings

app = Flask(__name__)

# ✅ Updated Vector Store Initialization
embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
vector_store = Chroma(persist_directory=Config.VECTOR_DB_PATH, embedding_function=embedding_function)

storage_service = S3Storage()
llm_service = LLMService(vector_store)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def process_document(file):
    """Process document based on file type and return text chunks"""
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, file.filename)
    
    try:
        # Save file temporarily
        file.save(temp_path)

        # Process based on file type
        if file.filename.endswith('.pdf'):
            loader = PyPDFLoader(temp_path)
        elif file.filename.endswith('.txt'):
            loader = TextLoader(temp_path)
        else:
            raise ValueError("Unsupported file type")

        documents = loader.load()

        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        raw_chunks = text_splitter.split_documents(documents)

        # Ensure each chunk is a proper LangChain Document
        text_chunks = [Document(page_content=chunk.page_content, metadata={"source": file.filename}) for chunk in raw_chunks]

        return text_chunks

    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise

    finally:
        # Clean up temp file and directory
        shutil.rmtree(temp_dir, ignore_errors=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_document():
    try:
        logger.debug("Upload endpoint called")

        if 'file' not in request.files:
            logger.warning("No file in request")
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            logger.warning("Empty filename")
            return jsonify({'error': 'No file selected'}), 400

        if not file.filename.endswith(('.txt', '.pdf')):
            logger.warning(f"Unsupported file type: {file.filename}")
            return jsonify({'error': 'Only .txt and .pdf files are supported'}), 400

        logger.debug(f"Processing file: {file.filename}")

        # Process the document
        try:
            text_chunks = process_document(file)
            logger.debug(f"Document processed into {len(text_chunks)} chunks")
        except ValueError as ve:
            logger.error(f"Unsupported file type error: {str(ve)}")
            return jsonify({'error': str(ve)}), 400
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            return jsonify({'error': f'Error processing document: {str(e)}'}), 500

        # Upload to S3
        try:
            file.seek(0)  # Reset file pointer before upload
            storage_service.upload_file(file, file.filename)
            logger.debug("File uploaded to S3")
        except Exception as e:
            logger.error(f"Error uploading to S3: {str(e)}")
            return jsonify({'error': f'Error uploading to S3: {str(e)}'}), 500

        # Add to ChromaDB
        try:
            vector_store.add_documents(text_chunks)
            logger.debug("Documents added to ChromaDB")
        except Exception as e:
            logger.error(f"Error adding to ChromaDB: {str(e)}")
            return jsonify({'error': f'Error adding to ChromaDB: {str(e)}'}), 500

        return jsonify({
            'message': 'File uploaded and processed successfully',
            'chunks_processed': len(text_chunks)
        })

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/query', methods=['POST'])
def query():
    data = request.json
    if 'question' not in data:
        return jsonify({'error': 'No question provided'}), 400

    try:
        response = llm_service.get_response(data['question'])
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
