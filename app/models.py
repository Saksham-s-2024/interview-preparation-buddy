from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class StartSessionRequest(BaseModel):
    role: str = Field(..., description="Target role, e.g., 'backend engineer'")
    seniority: str = Field(..., description="Seniority level, e.g., 'junior', 'mid', 'senior'")
    preferred_language: Optional[str] = Field(None, description="Preferred programming language, e.g., 'python', 'java', 'javascript'")


class StartSessionResponse(BaseModel):
    session_id: str
    question: str
    audio_data: Optional[str] = None  # Base64 encoded audio


class AnswerRequest(BaseModel):
    session_id: str
    answer: str
    video_frame: Optional[str] = None  # Base64 encoded image
    code_solution: Optional[str] = None  # Code solution for coding questions


class EvaluationResult(BaseModel):
    feedback: str
    score: float


class SummaryResponse(BaseModel):
    total_questions: int
    average_score: float
    strengths: List[str]
    improvements: List[str]
    overall_feedback: str


class VideoAnalysisResult(BaseModel):
    eye_contact: Dict[str, float]
    posture: Dict[str, float]
    facial_expressions: Dict[str, float]
    hand_gestures: Dict[str, float]
    confidence_score: float

class CodingQuestion(BaseModel):
    problem_statement: str
    examples: List[str]
    constraints: List[str]
    difficulty: str  # "easy", "medium", "hard"
    category: str  # "arrays", "strings", "trees", etc.

class CodingResponse(BaseModel):
    feedback: str
    score: float
    test_cases_passed: int
    total_test_cases: int
    time_complexity: Optional[str]
    space_complexity: Optional[str]
    suggestions: List[str]

class AnswerResponse(BaseModel):
    feedback: str
    score: float
    next_question: Optional[str]
    finished: bool
    summary: Optional[SummaryResponse]
    video_analysis: Optional[VideoAnalysisResult]
    audio_data: Optional[str] = None  # Base64 encoded audio for next question
    coding_question: Optional[CodingQuestion] = None
    coding_response: Optional[CodingResponse] = None


