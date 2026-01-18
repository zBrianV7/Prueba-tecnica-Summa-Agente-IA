import boto3
import asyncio
import nest_asyncio
from langchain_aws import ChatBedrock
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import Tool
from src.mcp_server import mcp
from src.config import Config
# Permitir anidación de bucles para MCP
nest_asyncio.apply()

class HRSmartAgent:
    def __init__(self):
        # Configurar Claude 3 (Bedrock)
        self.llm = ChatBedrock(
            model_id=Config.MODEL_ID,
            model_kwargs={"temperature": 0},
            region_name=Config.AWS_REGION
        )

        #Convertir herramientas MCP → LangChain con Wrapper Robusto
        self.tools = []
        try:
            raw_tools = mcp._tool_manager.list_tools()

            for t_info in raw_tools:
                tool_obj = mcp._tool_manager.get_tool(t_info.name)

                if tool_obj:
                    def make_wrapper(tool_name, tool_instance):
                        def wrapper(tool_input=None, **kwargs):
                            # Normalizar la entrada a un diccionario para MCP {"documento": "123..."}
                            mcp_args = {}
                            
                            if isinstance(tool_input, dict):
                                mcp_args = tool_input
                            elif tool_input:
                                key = "documento" if "cesantias" in tool_name else "query"
                                mcp_args = {key: str(tool_input)}
                            else:
                                mcp_args = kwargs

                            # Ejecutar de forma síncrona esperando el resultado real
                            try:
                                loop = asyncio.get_event_loop()
                                # Pasamos el diccionario mcp_args
                                result = loop.run_until_complete(tool_instance.run(mcp_args))
                                return str(result)
                            except Exception as e:
                                return f"Error ejecutando herramienta {tool_name}: {str(e)}"
                        return wrapper

                    lc_tool = Tool(
                        name=t_info.name,
                        description=t_info.description,
                        func=make_wrapper(t_info.name, tool_obj)
                    )
                    self.tools.append(lc_tool)

            print(f"✅ Agente cargado con {len(self.tools)} herramientas (Mapeo de dict corregido).")

        except Exception as e:
            print(f"Error al cargar herramientas: {e}")

        self.system_prompt = (
            "Eres el asistente de Gestión Humana de Summa.\n"
            "REGLAS:\n"
            "1. NO INVENTES DATOS. Si la herramienta dice que no hay resultados, informa eso.\n"
            "2. Usa 'search_hr_policies' para cultura y beneficios.\n"
            "3. Usa 'get_cesantias_balance' para saldos de empleados.\n"
            "4. Sé profesional y directo."
        )

        #Crear el Agente
        self.agent_executor = create_react_agent(
            self.llm,
            tools=self.tools,
            prompt=self.system_prompt
        )

    def ask(self, query, history):
        inputs = {"messages": history + [HumanMessage(content=query)]}
        result = self.agent_executor.invoke(inputs)
        return {
            "output": result["messages"][-1].content,
            "messages": result["messages"]
        }