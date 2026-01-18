import streamlit as st
from src.agent_logic import HRSmartAgent
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

st.set_page_config(page_title="HR Smart Agent - Summa", layout="centered", page_icon="🤖")

st.title("🤖 Agente de Gestión Humana")
st.markdown("Consulta tus cesantías y políticas de **Summa (Grupo Argos)**.")

# 1. Inicializar el agente en la sesión
if "agent" not in st.session_state:
    st.session_state.agent = HRSmartAgent()

# 2. Inicializar historial de chat (formato LangChain para el agente)
if "langchain_messages" not in st.session_state:
    st.session_state.langchain_messages = []

# 3. Mostrar historial de chat en la UI
for msg in st.session_state.langchain_messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage) and msg.content:
        with st.chat_message("assistant"):
            st.markdown(msg.content)

# 4. Entrada del usuario
if prompt := st.chat_input("¿En qué puedo ayudarte hoy?"):
    # Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        thought_container = st.expander("🧠 Ver proceso de pensamiento...")
        response_placeholder = st.empty()
        
        try:
            # Ejecución del agente pasándole el historial acumulado
            # Nota: 'history' en tu clase agent_logic espera una lista de mensajes
            result = st.session_state.agent.ask(prompt, st.session_state.langchain_messages)
            
            # 5. Extraer y mostrar el razonamiento (ToolMessages e intermediate steps)
            # Buscamos en los mensajes nuevos generados en esta vuelta
            for msg in result["messages"]:
                # Si el mensaje tiene llamadas a herramientas
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for call in msg.tool_calls:
                        thought_container.status(f"🔨 Llamando a: {call['name']}", state="complete")
                        thought_container.write(f"**Input:** {call['args']}")
                
                # Si el mensaje es la respuesta de la herramienta
                if isinstance(msg, ToolMessage):
                    thought_container.write(f"**Resultado:** {msg.content}")

            # 6. Mostrar respuesta final y actualizar historial
            final_answer = result["output"]
            response_placeholder.markdown(final_answer)
            
            # Guardamos todo el hilo de mensajes (incluyendo razonamiento) para mantener el contexto
            st.session_state.langchain_messages = result["messages"]
            
        except Exception as e:
            st.error(f"Error en el agente: {str(e)}")
            st.exception(e) # Esto te ayudará a ver el traceback en desarrollo

# --- Sidebar ---
st.sidebar.header("Opciones")
if st.sidebar.button("Limpiar Conversación"):
    st.session_state.langchain_messages = []
    st.rerun()

if st.sidebar.button("Generar Reporte de Prueba"):
    with open("resultado_prueba.txt", "w", encoding="utf-8") as f:
        for m in st.session_state.langchain_messages:
            role = "USUARIO" if isinstance(m, HumanMessage) else "AGENTE"
            content = m.content if m.content else "[Llamada a Herramienta]"
            f.write(f"{role}: {content}\n")
    st.sidebar.success("Reporte 'resultado_prueba.txt' guardado.")