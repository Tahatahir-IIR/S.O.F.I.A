import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

# Utilisation des modèles locaux via Ollama pour le RAG
Settings.llm = Ollama(model="llama3.2:1b", request_timeout=300.0)
Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")

def setup_rag_pipeline(data_dir="c:/S.O.F.I.A/data"):
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    # 1. Ingestion : Chargement des documents locaux
    print("[RAG] Ingestion des documents depuis la base de données...")
    documents = SimpleDirectoryReader(data_dir).load_data()
    
    # 2. Indexation : Création de l'index vectoriel
    print("[RAG] Indexation des documents en cours...")
    index = VectorStoreIndex.from_documents(documents)
    
    # 3. Retrieval & Augmentation : Création du moteur de recherche
    query_engine = index.as_query_engine()
    print("[RAG] Pipeline RAG prêt.")
    return query_engine

def query_rag(query_str: str) -> str:
    """Tool function to query the private knowledge base (RAG)."""
    engine = setup_rag_pipeline()
    response = engine.query(query_str)
    return str(response)

if __name__ == "__main__":
    # Test unitaire rapide
    print(query_rag("Quels sont les agents de SOFIA ?"))
