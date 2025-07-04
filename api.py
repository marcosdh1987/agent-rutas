import logging
from typing import Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import MessagesState
from fastapi import Request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(override=True)

# Añadir carpeta local 'src' al inicio de sys.path para priorizar este paquete
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# workflow chatbot tools
from agent_rutas.graph import graph as graph_tools

# Definición de Agent Card para protocolo A2A
AGENT_CARD = {
    "name": "Artemis AI Chatbot Agent",
    "description": "Agente que responde preguntas sobre rutas de la provincia de Neuquén",
    "url": "http://localhost:8000",
    "version": "1.0",
    "capabilities": {
        "streaming": False,
        "pushNotifications": False
    }
}

app = FastAPI(
    title="Artemis AI Chatbot API",
    description="API for interacting with the Artemis route information chatbot",
    version="1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


class ChatRequest(BaseModel):
    input_question: str = Field(
        description="Question to ask the chatbot about routes in Neuquén.",
        example="¿Cuál es el estado de la ruta P013?",
    )
    user_id: str = Field(
        description="Unique identifier for the user. Used for tracking and personalization."
    )
    llm_model_core: str = Field(
        default="nemotron",
        description="The Large Language Model to use for processing. Available options: nemotron, llama31, gpt4omini.",
    )
    conversation_id: Optional[str] = Field(
        default="",
        description="Optional: ID for continuing an existing conversation. Used for follow-up questions.",
    )
    chat_history: Optional[list] = Field(
        default=[],
        description="Optional: List of previous interactions in the conversation. Used for context in follow-up questions.",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "input_question": "¿Cuál es el estado de la ruta P013?",
                "user_id": "user123",
                "llm_model_core": "nemotron",
                "conversation_id": "c6f2bd59-b43a-4558-bec5-e938c247db24",
                "chat_history": [],
            }
        }


class ChatResponse(BaseModel):
    bot_answer: str = Field(description="The chatbot's response to the question")
    identifiers: Dict = Field(description="Conversation tracking identifiers", default={})
    answer_details: Dict = Field(description="Additional details about the answer", default={})
    metadata: Dict = Field(description="Additional metadata about the request and response", default={})


@app.post(
    "/api/chat",
    response_model=ChatResponse,
    summary="Get chatbot response",
    description="Send a question about routes and get a response from the AI",
    tags=["Chatbot"],
)
async def chat(request: ChatRequest):
    """Process chat request and return response"""
    try:
        logger.info(f"Processing request for user: {request.user_id}")
        
        # Create the initial state with the user's question
        initial_state = MessagesState(messages=[
            SystemMessage(content="Eres un asistente especializado en informar sobre el estado de las rutas de la provincia de Neuquén."),
            HumanMessage(content=request.input_question)
        ])
        
        # Process the message through the graph
        messages = graph_tools.invoke(initial_state)
        
        # Extract the bot's answer from the messages
        # The last message should be the assistant's response
        bot_answer = ""
        for msg in messages["messages"]:
            if hasattr(msg, "content"):
                bot_answer = msg.content
        
        # Prepare the response
        response = ChatResponse(
            bot_answer=bot_answer,
            identifiers={
                "user_id": request.user_id,
                "conversation_id": request.conversation_id,
                "model": request.llm_model_core
            },
            answer_details={},
            metadata={
                "model_used": request.llm_model_core,
                "timestamp": messages.get("timestamp", "")
            }
        )
        
        return response

    except Exception as e:
        logger.error(f"Error processing chat request for user {request.user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/.well-known/agent.json")
async def get_agent_card():
    """Endpoint para proporcionar la Agent Card (metadatos del agente)"""
    return AGENT_CARD


@app.post("/tasks/send")
async def handle_task(request: Request):
    """Endpoint A2A para recibir tareas (tasks/send) y responder siguiendo el protocolo Google A2A"""
    try:
        task_request = await request.json()
        task_id = task_request.get("id")
        # Extraer mensaje de usuario (primer TextPart)
        try:
            user_message = task_request["message"]["parts"][0]["text"]
        except Exception:
            raise HTTPException(status_code=400, detail="Formato de solicitud inválido")
        # Procesar con LangGraph
        initial_state = MessagesState(messages=[
            SystemMessage(content="Eres un asistente especializado en informar sobre el estado de las rutas de la provincia de Neuquén."),
            HumanMessage(content=user_message)
        ])
        messages = graph_tools.invoke(initial_state)
        # Extraer respuesta del agente
        bot_answer = ""
        for msg in messages.get("messages", []):
            if hasattr(msg, "content"):
                bot_answer = msg.content
        # Construir respuesta en formato Task
        response_task = {
            "id": task_id,
            "status": {"state": "completed"},
            "messages": [
                task_request.get("message", {}),
                {"role": "agent", "parts": [{"text": bot_answer}]}
            ]
        }
        return response_task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en /tasks/send: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Check API health status
    Returns:
        dict: Status message indicating the API is healthy
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
