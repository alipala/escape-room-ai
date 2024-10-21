from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import JSONLoader
from langchain.text_splitter import CharacterTextSplitter
from app.utils.logger import setup_logger

import json

logger = setup_logger()

class RAGService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = None

    def load_data(self, file_path: str):
        try:
            # First, let's check if the file exists and has content
            with open(file_path, 'r') as file:
                data = json.load(file)
            
            if not data:
                logger.warning(f"The file {file_path} is empty.")
                return

            # Use JSONLoader instead of TextLoader
            loader = JSONLoader(file_path=file_path, jq_schema='.', text_content=False)
            documents = loader.load()

            if not documents:
                logger.warning(f"No documents were loaded from {file_path}")
                return

            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
            texts = text_splitter.split_documents(documents)
            
            if not texts:
                logger.warning("No texts were generated after splitting documents")
                return

            self.vector_store = FAISS.from_documents(texts, self.embeddings)
            logger.info(f"Data loaded successfully from {file_path}")
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in file: {file_path}")
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise