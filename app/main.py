from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from uuid import uuid4
from typing import Dict
import os

from .models import (
    StartSessionRequest,
    StartSessionResponse,
    AnswerRequest,
    AnswerResponse,
    SummaryResponse,
    VideoAnalysisResult,
)
from .ai import AIInterviewAssistant
from .scoring import aggregate_session_score
from .video_analysis import VideoAnalyzer
from .tts import TextToSpeech
from .coding_questions import CodingQuestionBank
from .code_assessment import CodeAssessor


SESSIONS: Dict[str, dict] = {}


def create_app() -> FastAPI:
    app = FastAPI(title="AI Interview Preparation Tool", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


    static_dir = os.path.join(os.path.dirname(__file__), "static")
    os.makedirs(static_dir, exist_ok=True)
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    ai = AIInterviewAssistant()
    video_analyzer = VideoAnalyzer()
    tts = TextToSpeech()
    coding_bank = CodingQuestionBank()
    code_assessor = CodeAssessor()

    @app.get("/")
    def read_root():
        index_path = os.path.join(static_dir, "index.html")
        if not os.path.exists(index_path):
            return {"message": "Backend is running. Static UI not found."}
        return FileResponse(index_path)

    @app.post("/api/session/start", response_model=StartSessionResponse)
    def start_session(payload: StartSessionRequest):
        session_id = str(uuid4())
        first_question = ai.generate_first_question(payload.role, payload.seniority)
        
        # Generate audio for the question
        audio_data = tts.speak_text(first_question)
        
        # Check if we should include coding questions
        coding_question = None
        if payload.preferred_language:
            coding_question = coding_bank.get_question_for_role(
                payload.role, payload.seniority, payload.preferred_language
            )
        
        SESSIONS[session_id] = {
            "role": payload.role,
            "seniority": payload.seniority,
            "preferred_language": payload.preferred_language,
            "questions": [first_question],
            "current_index": 0,
            "answers": [],
            "feedback": [],
            "scores": [],
            "coding_question": coding_question,
            "coding_completed": False,
        }
        return StartSessionResponse(session_id=session_id, question=first_question, audio_data=audio_data)

    @app.post("/api/session/answer", response_model=AnswerResponse)
    def answer_question(payload: AnswerRequest):
        session = SESSIONS.get(payload.session_id)
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found")

        current_index = session["current_index"]
        question = session["questions"][current_index]

        eval_result = ai.evaluate_answer(question, payload.answer, session)
        
        # Analyze video if provided
        video_analysis = None
        if payload.video_frame:
            try:
                analysis_result = video_analyzer.analyze_frame(payload.video_frame)
                video_analysis = VideoAnalysisResult(**analysis_result)
            except Exception as e:
                print(f"Video analysis error: {e}")
                video_analysis = None
        
        session["answers"].append(payload.answer)
        session["feedback"].append(eval_result.feedback)
        session["scores"].append(eval_result.score)
        
        # Handle coding assessment if code solution provided
        coding_response = None
        if payload.code_solution and session.get("coding_question") and not session.get("coding_completed"):
            coding_response = code_assessor.assess_code(
                payload.code_solution, 
                session["coding_question"].category,
                session.get("preferred_language", "python")
            )
            session["coding_completed"] = True

        next_question = ai.generate_followup_question(
            role=session["role"],
            seniority=session["seniority"],
            previous_question=question,
            answer=payload.answer,
            feedback=eval_result.feedback,
            asked_questions=session["questions"],
        )

        # Check if we should present coding question
        if (session.get("coding_question") and not session.get("coding_completed") and 
            len(session["questions"]) >= 3):  # After a few behavioral questions
            return AnswerResponse(
                feedback=eval_result.feedback,
                score=eval_result.score,
                next_question=None,
                finished=False,
                summary=None,
                video_analysis=video_analysis,
                audio_data=None,
                coding_question=session["coding_question"],
                coding_response=coding_response,
            )

        if next_question is None or len(session["questions"]) >= 8:
            summary = aggregate_session_score(
                session["questions"], session["answers"], session["scores"], session["feedback"]
            )
            return AnswerResponse(
                feedback=eval_result.feedback,
                score=eval_result.score,
                next_question=None,
                finished=True,
                summary=summary,
                video_analysis=video_analysis,
                audio_data=None,
                coding_question=None,
                coding_response=coding_response,
            )

        # Generate audio for next question
        next_audio_data = tts.speak_text(next_question)
        
        session["questions"].append(next_question)
        session["current_index"] = current_index + 1
        return AnswerResponse(
            feedback=eval_result.feedback,
            score=eval_result.score,
            next_question=next_question,
            finished=False,
            summary=None,
            video_analysis=video_analysis,
            audio_data=next_audio_data,
            coding_question=None,
            coding_response=coding_response,
        )

    @app.get("/api/session/summary", response_model=SummaryResponse)
    def get_summary(session_id: str):
        session = SESSIONS.get(session_id)
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found")
        summary = aggregate_session_score(
            session["questions"], session["answers"], session["scores"], session["feedback"]
        )
        return summary

    return app

app = create_app()


