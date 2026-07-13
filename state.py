from typing import Annotated, Optional
from typing_extensions import TypedDict, Literal
from langgraph.graph.message import add_messages


class MedicalState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    next: Literal[
        "diagnostic_agent",
        "physician_review",
        "report_agent",
        "FINISH"
    ]
    question_count: int
    patient_answers: list[dict]
    interim_care: str
    diagnostic_summary: str
    physician_treatment: str
    final_report: str
    patient_initial_case: str
    session_id: str
    status: str  # "collecting_answers" | "awaiting_physician" | "generating_report" | "done"
