# Agent Rutas

Agente especializado en informar sobre el estado de las rutas de la provincia de Neuquén.

## Descripción

- Proporciona un paquete Python (`agent_rutas`) con la lógica del agente (prompts, grafo, herramientas y estado).
- Incluye un servicio HTTP basado en FastAPI (`api.py`) para exponer endpoints de chat, health-check y protocolo A2A.
- Permite integrarse en proyectos como dependencia instalable.

## Instalación

> Requisitos: Python >= 3.8

### 1) Instalación local editable

```bash
cd agent-rutas
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -e .
```
>
> También usando Makefile:
>
> ```bash
> cd agent-rutas
> make install
> ```

### 2) Instalación desde repositorio Git

> En tu `requirements.txt` o directamente con pip:
>
> ```text
> git+https://<tu-repo>/agent-rutas.git@main#egg=agent-rutas
> ```
>
> o editable:
>
> ```text
> -e git+https://<tu-repo>/agent-rutas.git@main#egg=agent-rutas
> ```

## Uso como paquete

### Importar módulo

```python
from agent_rutas import graph, tools, utils
```

### Ejemplo de chat en código

```python
from agent_rutas.graph import graph as graph_tools
from langgraph.graph import MessagesState
from langchain_core.messages import SystemMessage, HumanMessage
#
state = MessagesState(messages=[
    SystemMessage(content="Eres un asistente especializado en rutas de Neuquén."),
    HumanMessage(content="¿Cuál es el estado de la Ruta 22?")
])
response = graph_tools.invoke(state)
# Extrae la última respuesta
for msg in response.get("messages", []):
    print(msg.content)
```

## Comandos disponibles (Makefile)

- `make install` : crea el virtualenv, instala `requirements.in` y registra el paquete en editable.
- `make generate-requirements` : genera `src/requirements.txt` congelado con `uv pip freeze`.
- `make run-dev` : inicia servidor de desarrollo LangGraph.
- `make run-api` : inicia FastAPI en `http://0.0.0.0:8000` con recarga (`uvicorn api:app --reload`).

## Endpoints de la API

| Método | URL                         | Descripción                             |
|-------:|-----------------------------|-----------------------------------------|
| POST   | `/api/chat`                 | Pregunta al chatbot sobre rutas         |
| GET    | `/.well-known/agent.json`   | Agent Card (metadatos del agente)      |
| POST   | `/tasks/send`               | Endpoint A2A para tareas                |
| GET    | `/health`                   | Estado de salud de la API               |

## Estructura del proyecto

```
agent-rutas/
├── api.py               # FastAPI app
├── langgraph.json       # Configuración de LangGraph
├── Makefile             # Comandos de configuración y ejecución
├── requirements.in      # Dependencias base
├── setup.py             # Configuración de setuptools
└── src/
    └── agent_rutas/     # Lógica del agente (paquete Python)
```
## Command-Line Interface (CLI)

In addition to the FastAPI service, this package provides a standalone CLI script `main.py` that allows you to query the Neuquén routes agent directly.

Usage:
```bash
python main.py --question "What is the status of route P013?"
```
The script will invoke the internal LangGraph workflow and print the agent's response to the console.

## API Usage with curl

Below are examples of how to interact with the running FastAPI server using `curl`.

### Chat Endpoint
Send a POST request to `/api/chat` with a JSON payload:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "input_question": "What is the status of route P013?",
    "user_id": "user123",
    "llm_model_core": "gpt4omini",
    "conversation_id": "",
    "chat_history": []
  }'
```

### Agent Card Endpoint
Retrieve the agent's metadata:
```bash
curl http://localhost:8000/.well-known/agent.json
```

### Health Check Endpoint
Verify the API is running:
```bash
curl http://localhost:8000/health
```