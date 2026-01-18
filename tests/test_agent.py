from src.agent_logic import HRSmartAgent
from langchain_core.messages import HumanMessage, AIMessage

def chat_local():
    agent = HRSmartAgent()
    history = []

    while True:
        user_input = input("\n👤 Tú: ")
        if user_input.lower() in ["salir", "exit"]: break
        
        response = agent.ask(user_input, history)
        
        # --- BLOQUE PARA VER RAZONAMIENTO ---
        print("\n--- 🧠 RAZONAMIENTO DEL AGENTE ---")
        for msg in response['messages']:
            # Si el mensaje tiene tool_calls, es el LLM decidiendo usar una herramienta
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                print(f"🔍 [LLM decidió usar herramienta]: {msg.tool_calls[0]['name']}")
                print(f"📥 [Argumentos]: {msg.tool_calls[0]['args']}")
            # Si el mensaje es de tipo Tool, es la respuesta de la base de datos o RAG
            elif msg.type == 'tool':
                print(f"📤 [Respuesta de la Herramienta]: {msg.content}")
        print("----------------------------------\n")

        print(f"🤖 Agente: {response['output']}")
        history = response["messages"]

if __name__ == "__main__":
    chat_local()