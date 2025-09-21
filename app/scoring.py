from typing import List
from .models import SummaryResponse


def aggregate_session_score(questions: List[str], answers: List[str], scores: List[float], feedback: List[str]) -> SummaryResponse:
    total_questions = len(questions)
    if total_questions == 0:
        return SummaryResponse(
            total_questions=0,
            average_score=0.0,
            strengths=[],
            improvements=[],
            overall_feedback="No questions answered.",
        )

    average_score = round(sum(scores) / max(1, len(scores)), 2)

    strengths = []
    improvements = []
    for q, f, s in zip(questions, feedback, scores):
        if s >= 7.5:
            strengths.append(q)
        elif s <= 4.0:
            improvements.append(q)

    if average_score >= 7.5:
        overall = "Strong performance. You are well-prepared; refine advanced topics."
    elif average_score >= 5.0:
        overall = "Moderate performance. Strengthen fundamentals and practice structured answers."
    else:
        overall = "Needs improvement. Focus on foundations and practice mock interviews."

    return SummaryResponse(
        total_questions=total_questions,
        average_score=average_score,
        strengths=strengths[:5],
        improvements=improvements[:5],
        overall_feedback=overall,
    )


