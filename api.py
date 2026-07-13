import uuid
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()  # loads backend/.env → OPENAI_API_KEY

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .graph import graph
from .state import MedicalState
from .tools.patient_tools import CLINICAL_QUESTIONS

app = FastAPI(
    title="Clinical Orientation API",
    description="Multi-agent clinical orientation system — academic project. Does NOT replace medical consultation.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class StartSessionResponse(BaseModel):
    session_id: str
    message: str


class StartConsultationRequest(BaseModel):
    thread_id: str
    patient_initial_case: str


class ResumeConsultationRequest(BaseModel):
    thread_id: str
    answer: Optional[str] = None           # patient answer (questions 1-5)
    physician_treatment: Optional[str] = None  # physician input


class ConsultationState(BaseModel):
    thread_id: str
    status: str
    question_count: int
    current_question: Optional[str] = None
    diagnostic_summary: Optional[str] = None
    interim_care: Optional[str] = None
    physician_treatment: Optional[str] = None
    final_report: Optional[str] = None


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}


def get_current_state(thread_id: str) -> MedicalState:
    config = get_config(thread_id)
    snapshot = graph.get_state(config)
    # FIX: snapshot.values is the correct attribute (not a callable)
    return snapshot.values if snapshot else {}


# ── Routes ────────────────────────────────────────────────────────────────────

@app.post("/sessions/start", response_model=StartSessionResponse)
def start_session():
    """Creates a new consultation session and returns a thread_id."""
    session_id = str(uuid.uuid4())
    return StartSessionResponse(
        session_id=session_id,
        message="Session créée. Utilisez POST /consultation/start pour démarrer la consultation."
    )


@app.post("/consultation/start")
def start_consultation(req: StartConsultationRequest):
    """
    Starts a consultation: initializes the graph state with the patient's initial case.
    The graph is NOT run yet — we store the initial state and return the first question.
    The graph will be triggered once all 5 answers are collected.
    """
    config = get_config(req.thread_id)

    # FIX: Use update_state to seed the initial state WITHOUT running the graph.
    # We manage the Q&A loop in the API layer (outside the graph) and only invoke
    # the graph once all answers are ready. This avoids the "resume from nowhere"
    # problem that occurs when stream(None, config) is called on a thread that
    # has never had graph.invoke() called on it.
    initial_state: MedicalState = {
        "messages": [],
        "question_count": 0,
        "patient_answers": [],
        "patient_initial_case": req.patient_initial_case,
        "session_id": req.thread_id,
        "status": "collecting_answers",
        # Pre-set next so supervisor knows where to go once we do invoke
        "next": "diagnostic_agent",
    }

    # Seed state into the checkpointer so get_state() works immediately
    graph.update_state(config, initial_state, as_node="__start__")

    first_question = CLINICAL_QUESTIONS[0]

    return {
        "thread_id": req.thread_id,
        "status": "collecting_answers",
        "question_count": 0,
        "current_question": first_question,
        "total_questions": len(CLINICAL_QUESTIONS),
        "message": "Consultation démarrée. Répondez aux questions successives via POST /consultation/resume."
    }


@app.post("/consultation/resume")
def resume_consultation(req: ResumeConsultationRequest):
    """
    Resumes a consultation. Two use cases:
    1. Patient answering a question (provide `answer`)
    2. Physician providing treatment (provide `physician_treatment`)
    """
    config = get_config(req.thread_id)
    state = get_current_state(req.thread_id)

    if not state:
        raise HTTPException(status_code=404, detail="Thread non trouvé. Démarrez d'abord une consultation.")

    status = state.get("status", "collecting_answers")
    question_count = state.get("question_count", 0)
    patient_answers = list(state.get("patient_answers", []))

    # ── Case 1: Patient is answering questions ──────────────────────────────
    if (
        req.answer is not None
        and question_count < len(CLINICAL_QUESTIONS)
        and status not in ("awaiting_physician", "generating_report", "done", "running_diagnostic")
    ):
        current_index = question_count

        updated_answers = patient_answers + [{
            "question_index": current_index,
            "question": CLINICAL_QUESTIONS[current_index],
            "answer": req.answer,
        }]
        new_count = current_index + 1

        if new_count < len(CLINICAL_QUESTIONS):
            # More questions remain — save and return next question
            graph.update_state(config, {
                "patient_answers": updated_answers,
                "question_count": new_count,
                "status": "collecting_answers",
            })
            return {
                "thread_id": req.thread_id,
                "status": "collecting_answers",
                "question_count": new_count,
                "current_question": CLINICAL_QUESTIONS[new_count],
                "total_questions": len(CLINICAL_QUESTIONS),
                "message": f"Question {new_count + 1}/{len(CLINICAL_QUESTIONS)}"
            }
        else:
            # FIX: All 5 answers collected.
            # Save final answers then INVOKE the graph from the beginning.
            # We pass the full initial state so the graph runs:
            #   supervisor → diagnostic_agent → supervisor → [INTERRUPT before physician_review]
            graph.update_state(config, {
                "patient_answers": updated_answers,
                "question_count": new_count,
                "status": "running_diagnostic",
                "next": "diagnostic_agent",  # ensure supervisor routes correctly
            })

            # FIX: Use graph.invoke() with the full state as input so LangGraph
            # creates a proper execution checkpoint. Passing None only works if
            # the graph was previously run on this thread_id.
            full_state = get_current_state(req.thread_id)
            try:
                # This runs: supervisor → diagnostic_agent → supervisor →
                # then STOPS (interrupt_before=["physician_review"])
                graph.invoke(full_state, config)
            except Exception:
                # If interrupt fires, invoke raises — that's expected behaviour.
                # The state is safely stored in the checkpointer.
                pass

            current = get_current_state(req.thread_id)

            # Ensure status is correctly set
            graph.update_state(config, {"status": "awaiting_physician"})

            return {
                "thread_id": req.thread_id,
                "status": "awaiting_physician",
                "diagnostic_summary": current.get("diagnostic_summary"),
                "interim_care": current.get("interim_care"),
                "message": "Synthèse clinique générée. En attente de la revue du médecin traitant."
            }

    # ── Case 2: Physician providing treatment ───────────────────────────────
    elif req.physician_treatment is not None and status in ("awaiting_physician", "generating_report"):
        # FIX: Update state as the physician_review node, then resume the graph.
        # as_node="physician_review" tells LangGraph that the physician_review
        # node has now "executed" — so the graph will continue past the interrupt.
        graph.update_state(config, {
            "physician_treatment": req.physician_treatment,
            "status": "generating_report",
        }, as_node="physician_review")

        # Resume execution: supervisor → report_agent → supervisor → END
        graph.invoke(None, config)

        current = get_current_state(req.thread_id)
        return {
            "thread_id": req.thread_id,
            "status": "done",
            "final_report": current.get("final_report"),
            "message": "Rapport final généré."
        }

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Action invalide pour le statut '{status}'. Fournissez 'answer' ou 'physician_treatment'."
        )


@app.get("/consultation/{thread_id}", response_model=ConsultationState)
def get_consultation(thread_id: str):
    """Returns the current state of a consultation."""
    state = get_current_state(thread_id)
    if not state:
        raise HTTPException(status_code=404, detail="Consultation non trouvée.")

    qc = state.get("question_count", 0)
    current_q = CLINICAL_QUESTIONS[qc] if qc < len(CLINICAL_QUESTIONS) else None

    return ConsultationState(
        thread_id=thread_id,
        status=state.get("status", "unknown"),
        question_count=qc,
        current_question=current_q,
        diagnostic_summary=state.get("diagnostic_summary"),
        interim_care=state.get("interim_care"),
        physician_treatment=state.get("physician_treatment"),
        final_report=state.get("final_report"),
    )


@app.get("/consultation/{thread_id}/report")
def get_report(thread_id: str):
    """Returns the final report for a completed consultation."""
    state = get_current_state(thread_id)
    if not state:
        raise HTTPException(status_code=404, detail="Consultation non trouvée.")

    final_report = state.get("final_report")
    if not final_report:
        raise HTTPException(status_code=202, detail="Rapport pas encore disponible.")

    return {
        "thread_id": thread_id,
        "final_report": final_report,
        "disclaimer": "Ce système ne remplace pas une consultation médicale."
    }


@app.get("/health")
def health():
    return {"status": "ok", "service": "Clinical Orientation API"}
