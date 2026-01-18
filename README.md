# Prueba-tecnica-Summa-Agente-IA
Prueba tecnica para la empresa summa Agente IA
=======
Este proyecto es un Agente de Inteligencia Artificial especializado en Gestión Humana para **Summa**. Utiliza **Claude 3 Haiku** a través de **AWS Bedrock** y una arquitectura de **MCP (Model Context Protocol)** para consultar políticas internas (RAG) y saldos de cesantías (SQL).

## Características
- **Razonamiento ReAct:** El agente decide cuándo buscar en manuales o cuándo consultar bases de datos.
- **RAG (Retrieval Augmented Generation):** Consulta de beneficios y cultura desde documentos PDF usando ChromaDB.
- **SQL Querying:** Consulta de saldos de cesantías en tiempo real desde bases de datos estructuradas.
- **Interfaz Streamlit:** Chat interactivo con visualización del proceso de pensamiento del agente.
- **Pruebas Unitarias:** Suite de tests para validar la integridad del RAG y la limpieza de datos SQL.

## A tener en cuenta:
Los costos asociados a AWS son para realizar la vectorización de la información del pdf y uso del modelo Haiku para entrega de respuestas y razonamiento del agento.

---

## Requisitos Previos
- **Python 3.13** (Compatible con versiones 3.10+)
- **Credenciales de AWS:** Acceso configurado a Bedrock con el modelo `anthropic.claude-3-haiku-20240307-v1:0` habilitado.
- **Librerías:** Instalación vía `requirements.txt`.

---

## Instalación y Configuración

1. **Clonar el repositorio:**
   ```bash
   git clone <url-del-repositorio>
   cd Prueba-tecnica
2. **Crear y activar entorno virtual:**

    ```Bash
    python -m venv venv
    # En Windows:
    .\venv\Scripts\activate

3. **Instalar dependencias:**

    ```Bash
    pip install -r requirements.txt

4. **Configurar variables de entorno:** Crea un archivo .env en la raíz con lo siguiente:

    ```Fragmento de código

    AWS_ACCESS_KEY_ID=tu_access_key
    AWS_SECRET_ACCESS_KEY=tu_secret_key
    AWS_REGION=us-east-1
    MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0


5. **🖥️ Ejecución:** Interfaz de Usuario (Streamlit). Para lanzar el chat interactivo:

    ```Bash
    streamlit run app.py

6. **Pruebas Unitarias:** Para validar el funcionamiento de los módulos de base de datos y RAG:

    ```Bash
    python -m pytest tests/


**Estructura del Proyecto**
src/: Lógica central (Agente, Base de Datos, RAG, MCP Server).

data/: Contiene el manual de beneficios (PDF) y el consolidado de cesantías (Excel/DB).

tests/: Pruebas unitarias para asegurar la calidad de la data.

app.py: Punto de entrada de la interfaz gráfica.

**Flujo de Pensamiento del Agente**
El agente utiliza un ciclo de Pensamiento -> Acción -> Observación.

1. El usuario pregunta: "¿Cuál es mi saldo?".

2. El agente identifica que necesita la herramienta get_cesantias_balance.

3. El agente solicita el ID al usuario o lo toma del contexto.

4. El agente ejecuta la consulta y devuelve una respuesta natural basada en datos reales.

Desarrollado por: Brian - Prueba Técnica de IA
>>>>>>> 5d5285b (feat: versión inicial del Agente HR con MCP y RAG)
