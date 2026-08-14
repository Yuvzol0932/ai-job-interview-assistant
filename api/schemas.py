"""API 请求体契约。"""

from pydantic import BaseModel


class ClarifyRequest(BaseModel):
    resume_text: str


class DiagnoseRequest(BaseModel):
    resume_text: str
    items: list[dict] = []
    market_notes: str = ""
    target_job: str = ""
    target_location: str = ""


class JobMatchRequest(BaseModel):
    resume_text: str
    target_job: str = ""
    target_location: str = ""
    limit: int = 8


class InterviewStartRequest(BaseModel):
    job_label: str
    num_questions: int = 5
    resume_text: str = ""


class InterviewStateRequest(BaseModel):
    state: dict


class InterviewAnswerRequest(BaseModel):
    state: dict
    answer: str
