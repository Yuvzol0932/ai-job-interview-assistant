"""数据结构层：各层之间固定的接口契约。"""

from .resume import DiagnosisResult, ResumeData
from .interview import InterviewState
from .report import DIMENSIONS, InterviewReport

__all__ = [
    "DiagnosisResult",
    "ResumeData",
    "InterviewState",
    "DIMENSIONS",
    "InterviewReport",
]
