"""Orchestrator for the Neuquén routes agent."""
from .nodes import llm_call_node, tool_node, should_continue, reflection_node
from langgraph.graph import END, START, MessagesState, StateGraph


# Build the graph using the modular nodes (following generic-agent pattern)
builder = StateGraph(MessagesState)
builder.add_node("llm_call", llm_call_node)
builder.add_node("tools", tool_node)
builder.add_node("reflection", reflection_node)

builder.add_edge(START, "llm_call")
builder.add_conditional_edges(
    "llm_call",
    should_continue,
    {"tools": "tools", "end": END},
)
builder.add_edge("tools", "reflection")
builder.add_conditional_edges(
    "reflection",
    should_continue,
    {"tools": "tools", "end": END},
)
graph = builder.compile()
graph.name = "Routes Agent Workflow Graph"