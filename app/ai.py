import os
from typing import List, Optional, Dict, Tuple
from .models import EvaluationResult


OPENAI_ENABLED = bool(os.getenv("OPENAI_API_KEY"))


class AIInterviewAssistant:
    def __init__(self):
        self.use_openai = OPENAI_ENABLED
        self._init_openai_client()

    def _init_openai_client(self) -> None:
        if self.use_openai:
            try:
                from openai import OpenAI  # type: ignore
                self._client = OpenAI()
            except Exception:
                self.use_openai = False
                self._client = None
        else:
            self._client = None

    # Question Generation
    def generate_first_question(self, role: str, seniority: str) -> str:
        if self.use_openai:
            prompt = (
                f"You are an interviewer. Ask a single concise first question for a {seniority} {role}. "
                f"Focus on fundamentals. Output only the question."
            )
            return self._chat_single_turn(prompt)
        return self._mock_first_question(role, seniority)

    def generate_followup_question(
        self,
        role: str,
        seniority: str,
        previous_question: str,
        answer: str,
        feedback: str,
        asked_questions: List[str],
    ) -> Optional[str]:
        if self.use_openai:
            prompt = (
                "You are an interviewer. Based on the previous question and candidate's answer, ask the next question.\n"
                f"Role: {role}\nSeniority: {seniority}\n"
                f"Previous question: {previous_question}\n"
                f"Answer: {answer}\n"
                f"Your feedback: {feedback}\n"
                "Ask a single concise next question that probes a different area. If the interview should end, reply EXACTLY with: END."
            )
            next_q = self._chat_single_turn(prompt)
            if next_q.strip().upper() == "END":
                return None
            return next_q
        return self._mock_followup_question(role, seniority, asked_questions)

    # Evaluation
    def evaluate_answer(self, question: str, answer: str, session: Dict) -> EvaluationResult:
        if self.use_openai:
            prompt = (
                "Evaluate the candidate's answer to the interview question.\n"
                f"Question: {question}\n"
                f"Answer: {answer}\n"
                "Provide: concise feedback (2-4 sentences) and a numeric score 0-10.\n"
                "Respond as: FEEDBACK: <text>\nSCORE: <0-10>"
            )
            raw = self._chat_single_turn(prompt)
            feedback, score = self._parse_feedback_and_score(raw)
            return EvaluationResult(feedback=feedback, score=score)
        feedback, score = self._mock_evaluate(question, answer)
        return EvaluationResult(feedback=feedback, score=score)

    # OpenAI helpers
    def _chat_single_turn(self, user_prompt: str) -> str:
        try:
            resp = self._client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[{"role": "user", "content": user_prompt}],
                temperature=0.3,
                max_tokens=300,
            )
            return resp.choices[0].message.content.strip()
        except Exception:
            self.use_openai = False
            return (
                "Let's continue with a simpler next step: describe one concrete trade-off you made recently and why."
            )

    def _parse_feedback_and_score(self, raw: str) -> Tuple[str, float]:
        feedback: str = raw
        score: float = 5.0
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        for l in lines:
            if l.upper().startswith("FEEDBACK:"):
                feedback = l.split(":", 1)[1].strip()
            if l.upper().startswith("SCORE:"):
                val = l.split(":", 1)[1].strip()
                try:
                    score = float(val)
                except ValueError:
                    pass
        score = max(0.0, min(10.0, score))
        return feedback, score

    # Mock logic
    def _mock_first_question(self, role: str, seniority: str) -> str:
        role_norm = role.lower()
        if "backend" in role_norm:
            return "Explain how you would design a scalable REST API for a high-traffic service."
        if "frontend" in role_norm:
            return "How do you optimize performance in a large React application?"
        if "data" in role_norm:
            return "Describe how you would design a data pipeline for real-time analytics."
        return f"What are the core responsibilities of a {seniority} {role}?"

    def _mock_followup_question(self, role: str, seniority: str, asked_questions: List[str]) -> Optional[str]:
        bank = [
            "Can you discuss a trade-off you considered in a recent project?",
            "Walk me through your debugging process for a tricky issue.",
            "How do you ensure reliability and observability in your systems?",
            "Describe a time you mentored someone or were mentored.",
            "How do you prioritize tasks when facing conflicting deadlines?",
        ]
        for q in bank:
            if q not in asked_questions:
                return q
        return None

    def _mock_evaluate(self, question: str, answer: str) -> Tuple[str, float]:
        length_score = min(10.0, len(answer.split()) / 20.0 * 10.0)
        filler_penalty = sum(answer.lower().count(w) for w in ["umm", "uh", "like ", "you know"]) * 0.5
        clarity_bonus = 1.0 if any(k in answer.lower() for k in ["because", "therefore", "so that"]) else 0.0
        score = max(0.0, min(10.0, length_score - filler_penalty + clarity_bonus))
        feedback_bits: List[str] = []
        if length_score < 4:
            feedback_bits.append("Expand with more concrete details and examples.")
        if filler_penalty > 0:
            feedback_bits.append("Reduce filler words to improve clarity.")
        if clarity_bonus == 0:
            feedback_bits.append("Structure your answer with reasoning connectors (e.g., 'because').")
        if not feedback_bits:
            feedback_bits.append("Well-structured and sufficiently detailed answer.")
        return " ".join(feedback_bits), score


