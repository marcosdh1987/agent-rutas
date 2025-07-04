#!/usr/bin/env python3
"""
CLI script to query the agent_rutas chatbot.
Usage:
  python main.py --question "¿Cuál es el estado de la ruta P040?"
"""
import os
import sys
import argparse

# Asegurar que el paquete src esté en el path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from agent_rutas.graph import graph


def main():
    parser = argparse.ArgumentParser(
        description="Agente de rutas Neuquén: consulta el estado de rutas."
    )
    parser.add_argument(
        "--question", "-q", required=True, help="Pregunta para el agente"
    )
    args = parser.parse_args()

    # Estado inicial con mensaje de usuario
    from langgraph.graph import MessagesState
    from langchain_core.messages import HumanMessage

    initial_state = MessagesState(messages=[HumanMessage(content=args.question)])
    # Invocar el grafo y obtener mensajes de respuesta
    result = graph.invoke(initial_state)
    messages = result.get("messages", [])
    # Imprimir cada mensaje de contenido
    for msg in messages:
        if hasattr(msg, "content"):
            print(msg.content)
    return


if __name__ == "__main__":
    main()
