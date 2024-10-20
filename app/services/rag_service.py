from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from app.utils.logger import setup_logger

logger = setup_logger()

class RAGService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = None

    def load_data(self, file_path: str):
        try:
            loader = TextLoader(file_path)
            documents = loader.load()
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
            texts = text_splitter.split_documents(documents)
            self.vector_store = FAISS.from_documents(texts, self.embeddings)
            logger.info(f"Data loaded from {file_path}")
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise

    def query(self, query: str, k: int = 4):
        try:
            if not self.vector_store:
                raise ValueError("Vector store not initialized. Please load data first.")
            docs = self.vector_store.similarity_search(query, k=k)
            return [doc.page_content for doc in docs]
        except Exception as e:
            logger.error(f"Error querying vector store: {str(e)}")
            raise