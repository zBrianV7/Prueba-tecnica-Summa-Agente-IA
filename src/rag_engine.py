import os
import boto3
from langchain_aws import BedrockEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma 

class CompanyRAG:
    def __init__(self, pdf_path, persist_directory="./data/chroma_db"):
        self.pdf_path = pdf_path
        self.persist_directory = persist_directory
        
        self.bedrock_client = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")
        self.embeddings = BedrockEmbeddings(
            client=self.bedrock_client,
            model_id="amazon.titan-embed-text-v2:0"
        )
        self.vector_store = self._setup_vector_store()

    def _setup_vector_store(self):
        # Si la carpeta no tiene archivos reales, forzamos recreación
        if os.path.exists(self.persist_directory) and len(os.listdir(self.persist_directory)) > 0:
            return Chroma(persist_directory=self.persist_directory, embedding_function=self.embeddings)
        
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"No veo el PDF en {self.pdf_path}")

        loader = PyPDFLoader(self.pdf_path)
        documents = loader.load()
        
        if len(documents) == 0:
            print("ERROR: El PDF parece estar vacío o no tiene texto legible.")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
        chunks = text_splitter.split_documents(documents)
        print(f"Fragmentos creados: {len(chunks)}")

        return Chroma.from_documents(
            documents=chunks, 
            embedding=self.embeddings, 
            persist_directory=self.persist_directory
        )

    def search(self, query, k=3):
        try:
            results = self.vector_store.similarity_search(query, k=k)
            print(f"DEBUG: Buscando '{query}', encontrados: {len(results)}")
            return "\n---\n".join([doc.page_content for doc in results])
        except Exception as e:
            print(f"ERROR EN BÚSQUEDA AWS: {str(e)}")
            return ""