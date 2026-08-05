"""数据结构层：各层之间固定的接口契约。"""

from .resume import ClarificationItem, DiagnosisResult, ResumeData, ResumeProfile
from .interview import InterviewState
from .report import DIMENSIONS, InterviewReport

__all__ = [
    "DiagnosisResult",
    "ResumeProfile",
    "ClarificationItem",
    "ResumeData",
    "InterviewState",
    "DIMENSIONS",
    "InterviewReport",
]
