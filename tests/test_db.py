import pytest
import pandas as pd
import os
from src.database import Database

# El "Fixture" prepara el entorno antes de cada prueba
@pytest.fixture
def mock_db():
    # 1. SETUP: Crear un Excel temporal para pruebas
    test_file = "data/cesantias_test_temp.xlsx"
    data = {
        'Documento': [123, 456],
        'Cesantias': ['$ 1.000.000,00', '$ 2.500,50'],
        'Mes': ['1/05/2025', '1/06/2025']
    }
    pd.DataFrame(data).to_excel(test_file, index=False)
    
    # Instanciar la base de datos
    db = Database(test_file)
    
    yield db  # Aquí es donde ocurre la prueba
    
    # 2. TEARDOWN: Borrar el archivo temporal al terminar
    if os.path.exists(test_file):
        os.remove(test_file)

# Prueba: Verificar que la limpieza de datos convierta a números
def test_cesantias_conversion_is_numeric(mock_db):
    res = mock_db.query("SELECT SUM(cesantias) as total FROM cesantias")
    total = res[0]['total']
    
    # Verificamos que sea un número y que la suma sea correcta
    assert isinstance(total, (int, float)), "El valor debe ser numérico"
    assert total == 1002500.5, f"La suma esperada era 1002500.5, pero dio {total}"

# Prueba: Verificar búsqueda por documento específico
def test_query_by_document(mock_db):
    res = mock_db.query("SELECT cesantias FROM cesantias WHERE documento = 123")
    assert len(res) == 1
    assert res[0]['cesantias'] == 1000000.0