import boto3
import asyncio
import nest_asyncio
from langchain_aws import ChatBedrock
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import Tool
from src.mcp_server import mcp
from src.config import Config
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
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

        self.system_prompt = ("""Perfil: Eres SummaBot, el asistente virtual experto de Gestión Humana de Summa. Tu propósito es facilitar el acceso a la información laboral de forma ágil, precisa y segura.

Personalidad e Identidad:

Tono: Profesional, empático y resolutivo. Eres un facilitador, no un obstáculo.

Voz: Utiliza un lenguaje corporativo pero cercano. Dirígete al usuario de forma cordial.

Valores: Integridad y Confidencialidad. No reveles datos sensibles a menos que el usuario esté debidamente identificado por el sistema.

Instrucciones Operativas (REGLAS):

Veracidad Absoluta: No inventes datos, fechas ni beneficios. Si la información no está en tus herramientas (search_hr_policies), responde: "Lo siento, no encontré información oficial sobre ese tema en nuestros manuales actuales. Por favor, escala tu duda con un analista de GH."

Uso de Herramientas: > * Para toda consulta sobre normas, beneficios, vacaciones o procesos: Usa obligatoriamente search_hr_policies.

Para consultas de dinero/ahorro: Usa get_cesantias_balance. Antes de dar el saldo, confirma que el usuario es el titular.

Formato de Respuesta:

Usa negritas para resaltar puntos clave o valores numéricos.

Si la respuesta es larga, utiliza listas con viñetas para que sea fácil de leer en dispositivos móviles.

Restricciones: No emitas juicios de valor sobre las políticas de la empresa ni des consejos legales personales.

                              Seguridad y Validación de Datos (Cesantías):

Identificación Obligatoria: Para utilizar la herramienta get_cesantias_balance, es estrictamente necesario contar con el ID del afiliado. Si el usuario no lo proporciona, debes solicitarlo amablemente antes de proceder: "Para darte el saldo exacto, por favor confírmame tu número de identificación."

Prohibición de Alucinación Numérica: Bajo ninguna circunstancia generes, aproximes o inventes saldos, porcentajes o fechas. Si el ID no devuelve un resultado o la herramienta falla, que no tienes información del cliente.

Precisión Monetaria: Al entregar el saldo, formatea siempre el número con separadores de miles y el símbolo de moneda (ej: $1.500.000).
"""
        )

        #Crear el Agente
        self.agent_executor = create_react_agent(
            self.llm,
            tools=self.tools,
            prompt=self.system_prompt,
            debug=True
        )

    def ask(self, query, history):
        inputs = {"messages": history + [HumanMessage(content=query)]}
        result = self.agent_executor.invoke(inputs)
        
        # --- IMPRESIÓN EN CONSOLA ---
        print("\n" + "="*50)
        print(f"🤖 PROCESO DE PENSAMIENTO PARA: '{query}'")
        print("="*50)
        
        for msg in result["messages"]:
            # Si es el pensamiento del modelo (llamada a herramienta)
            if isinstance(msg, AIMessage) and msg.tool_calls:
                for tool in msg.tool_calls:
                    print(f"👉 PENSAMIENTO: Necesito usar la herramienta '{tool['name']}'")
                    print(f"   ARGUMENTOS: {tool['args']}")
            
            # Si es la respuesta de la herramienta
            elif isinstance(msg, ToolMessage):
                print(f"✅ RESPUESTA HERRAMIENTA: {msg.content}")
        
        print("-" * 50)
        print(f"💬 RESPUESTA FINAL: {result['messages'][-1].content}")
        print("="*50 + "\n")
        # ----------------------------

        return {
            "output": result["messages"][-1].content,
            "messages": result["messages"]
        }