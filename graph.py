import os
from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import MedicalState
from .nodes.supervisor import supervisor_node
from .nodes.diagnostic_agent import diagnostic_agent_node
from .nodes.physician_review import physician_review_node
from .nodes.report_agent import report_agent_node


def route_supervisor(state: MedicalState) -> str:
    """Routes from supervisor to the next node based on state.next."""
    next_step = state.get("next", "diagnostic_agent")
    if next_step == "FINISH":
        return END
    return next_step


def build_graph():
    """Builds and compiles the LangGraph clinical orientation workflow."""
    builder = StateGraph(MedicalState)

    # Add nodes
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("diagnostic_agent", diagnostic_agent_node)
    builder.add_node("physician_review", physician_review_node)
    builder.add_node("report_agent", report_agent_node)

    # Entry point
    builder.set_entry_point("supervisor")

    # Supervisor routes to appropriate agent
    builder.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {
            "diagnostic_agent": "diagnostic_agent",
            "physician_review": "physician_review",
            "report_agent": "report_agent",
            END: END,
        }
    )

    # All agents return to supervisor
    builder.add_edge("diagnostic_agent", "supervisor")
    builder.add_edge("physician_review", "supervisor")
    builder.add_edge("report_agent", "supervisor")

    # Compile with memory checkpointing and physician_review interrupt
    memory = MemorySaver()
    graph = builder.compile(
        checkpointer=memory,
        interrupt_before=["physician_review"]
    )

    return graph


# Singleton graph instance
graph = build_graph()
