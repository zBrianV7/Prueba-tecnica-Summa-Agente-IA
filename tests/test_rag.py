import pytest
import os
from src.rag_engine import CompanyRAG

# Fixture para inicializar el RAG una sola vez para todas las pruebas
@pytest.fixture(scope="module")
def rag_instance():
    pdf_path = "data/kb_summa_rh.pdf"
    
    # Verificamos que el archivo exista antes de intentar la prueba
    if not os.path.exists(pdf_path):
        pytest.fail(f"El archivo necesario para la prueba no existe en {pdf_path}")
        
    return CompanyRAG(pdf_path)

# 1. Test: Verificar que la base de datos vectorial no esté vacía
def test_vector_store_is_not_empty(rag_instance):
    collection = rag_instance.vector_store._collection
    count = collection.count()
    
    assert count > 0, "La base de datos vectorial (ChromaDB) está vacía."
    print(f"\n[RAG TEST] Vectores encontrados: {count}")

# 2. Test: Verificar que la búsqueda devuelva fragmentos relevantes
def test_similarity_search_returns_results(rag_instance):
    query = "Beneficios de educación y vacaciones"
    # Buscamos k=2 fragmentos
    resultados = rag_instance.vector_store.similarity_search(query, k=2)
    
    assert len(resultados) > 0, f"La búsqueda para '{query}' no retornó resultados."
    assert len(resultados) <= 2, "La búsqueda retornó más resultados de los solicitados."
    
    # Validamos que el contenido no sea nulo o vacío
    for res in resultados:
        assert res.page_content.strip() != "", "Se recuperó un fragmento pero está vacío."

# 3. Test: Verificar la estructura del contenido recuperado
def test_result_content_structure(rag_instance):
    query = "Summa"
    resultados = rag_instance.vector_store.similarity_search(query, k=1)
    
    if resultados:
        doc = resultados[0]
        # Verificamos que tenga metadatos (como el número de página si lo configuraste)
        assert hasattr(doc, 'page_content'), "El resultado debe tener el atributo page_content"
        assert isinstance(doc.page_content, str), "El contenido debe ser una cadena de texto"