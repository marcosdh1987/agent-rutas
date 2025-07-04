"""Node implementations for the Neuquén routes agent's decision-making process."""
from langchain_core.messages import SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig

from ..tools import buscar_estado_rutas
from ..prompts import ROUTES_AGENT_PROMPT as system_prompt
from ..model.llm import ModelFactory
import os

TOOLS = [buscar_estado_rutas]

model_core = os.environ.get("MODEL_CORE", "gemini-2.0-flash")
factory = ModelFactory(model_name=model_core, temperature=0.5)
llm = factory.create_model()

def llm_call_node(state, *, config: RunnableConfig):
    """Node for calling the LLM with the available tools."""
    system_msg = SystemMessage(content=system_prompt)
    tools_by_name = {tool.name: tool for tool in TOOLS}
    llm_with_tools = llm.bind_tools(TOOLS)
    
    # Handle messages to ensure only one SystemMessage at the beginning
    messages = state["messages"]
    if messages and isinstance(messages[0], SystemMessage):
        # Replace the existing SystemMessage with our specialized one
        messages_for_llm = [system_msg] + messages[1:]
    else:
        # No SystemMessage found, add ours at the beginning
        messages_for_llm = [system_msg] + messages
    
    output = llm_with_tools.invoke(messages_for_llm)
    return {"messages": [output]}


def tool_node(state, *, config: RunnableConfig):
    """Node for executing the selected tool(s) and returning their results."""
    tools_by_name = {tool.name: tool for tool in TOOLS}
    results = []
    for tool_call in state["messages"][-1].tool_calls:
        name = tool_call["name"]
        tool = tools_by_name.get(name)
        if tool:
            obs = tool.invoke(tool_call["args"])
            results.append(ToolMessage(content=obs, tool_call_id=tool_call["id"]))
        else:
            results.append(
                ToolMessage(
                    content=f"Tool '{name}' not found.", tool_call_id=tool_call["id"]
                )
            )
    return {"messages": results}


def should_continue(state, *, config: RunnableConfig):
    """Node to decide whether to continue with tool execution or end the graph."""
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return "end"
 
def reflection_node(state, *, config: RunnableConfig):
    """Node para reflexionar sobre los resultados de herramientas y decidir si solicitar más datos o finalizar."""
    # Prompt de reflexión: evalúa si la información obtenida es suficiente
    reflection_prompt = (
        "Has recibido estos resultados de las herramientas.\n"
        "1. ¿Es suficiente esta información para responder la pregunta original?\n"
        "   - Si NO, genera un nuevo tool_call especificando el nombre de la herramienta y sus argumentos.\n"
        "   - Si SÍ, devuelve la respuesta final sin tool_calls."
    )
    system_msg = SystemMessage(content=reflection_prompt)
    # Habilitar herramientas para posibles nuevos llamados
    llm_with_tools = llm.bind_tools(TOOLS)
    
    # Handle messages to ensure only one SystemMessage at the beginning
    messages = state["messages"]
    if messages and isinstance(messages[0], SystemMessage):
        # Replace the existing SystemMessage with our specialized one
        messages_for_llm = [system_msg] + messages[1:]
    else:
        # No SystemMessage found, add ours at the beginning
        messages_for_llm = [system_msg] + messages
    
    # Incluir mensajes previos de herramientas en el input
    output = llm_with_tools.invoke(messages_for_llm)
    return {"messages": [output]}
