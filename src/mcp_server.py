from mcp.server.fastmcp import FastMCP
from src.database import Database
from .rag_engine import CompanyRAG
from src.config import Config

# Inicializamos el servidor MCP llamado "SummaHR"
mcp = FastMCP("SummaHR")

# Instancias de datos
db = Database(excel_path=Config.EXCEL_PATH)
rag = CompanyRAG(Config.PDF_PATH)

@mcp.tool()
def get_cesantias_balance(documento: int) -> str:
    """Consulta el saldo de cesantías usando el ID del empleado."""
    query_sql = f"SELECT cesantias, mes FROM cesantias WHERE documento = {documento} LIMIT 1"
    res = db.query(query_sql)
    if res and len(res) > 0:
        return f"Saldo: {res[0]['cesantias']} (Corte: {res[0]['mes']})"
    return "Empleado no encontrado."

@mcp.tool()
def search_hr_policies(query: str) -> str:
    """CONSULTA OBLIGATORIA para cualquier duda sobre Summa, beneficios, 
    modelo de trabajo, cultura, vacaciones y políticas de recursos humanos. 
    Usa lenguaje natural para la búsqueda."""
    return rag.search(query)