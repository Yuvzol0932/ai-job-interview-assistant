"""面试流程 API：状态快照往返，状态机逻辑保留在 Python。"""

from fastapi import APIRouter, Depends, HTTPException

from api.deps import get_client
from api.schemas import (
    InterviewAnswerRequest,
    InterviewStartRequest,
    InterviewStateRequest,
)
from models.interview import InterviewState
from services.interview_service import (
    InterviewError,
    finish_early,
    next_question,
    request_follow_up,
    start_interview,
    submit_follow_up_answer,
    submit_main_answer,
)

router = APIRouter(prefix="/api/interview", tags=["interview"])


def _state_response(state: InterviewState) -> dict:
    data = state.to_dict()
    data["total"] = state.total
    data["answered_count"] = state.answered_count
    data["current_question"] = state.current_question
    data["current_follow_up_question"] = state.current_follow_up_question
    return data


@router.post("/start")
def start(req: InterviewStartRequest, client=Depends(get_client)) -> dict:
    if not req.job_label.strip():
        raise HTTPException(status_code=400, detail="请先选择或填写岗位方向。")
    try:
        state = start_interview(
            client,
            req.job_label,
            resume_text=req.resume_text,
            num_questions=req.num_questions,
        )
        return _state_response(state)
    except InterviewError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/answer")
def answer(req: InterviewAnswerRequest, _client=Depends(get_client)) -> dict:
    try:
        state = InterviewState.from_dict(req.state)
        submit_main_answer(state, req.answer)
        return _state_response(state)
    except InterviewError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/followup-answer")
def followup_answer(req: InterviewAnswerRequest, _client=Depends(get_client)) -> dict:
    try:
        state = InterviewState.from_dict(req.state)
        submit_follow_up_answer(state, req.answer)
        return _state_response(state)
    except InterviewError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/followup")
def followup(req: InterviewStateRequest, client=Depends(get_client)) -> dict:
    try:
        state = InterviewState.from_dict(req.state)
        request_follow_up(client, state)
        return _state_response(state)
    except InterviewError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/next")
def next_step(req: InterviewStateRequest, _client=Depends(get_client)) -> dict:
    try:
        state = InterviewState.from_dict(req.state)
        next_question(state)
        return _state_response(state)
    except InterviewError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/finish")
def finish(req: InterviewStateRequest, _client=Depends(get_client)) -> dict:
    try:
        state = InterviewState.from_dict(req.state)
        finish_early(state)
        return _state_response(state)
    except InterviewError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
