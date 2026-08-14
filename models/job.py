"""岗位招聘信息的数据结构（契约）。"""

from dataclasses import dataclass, field

from .utils import str_list


@dataclass
class JobPosting:
    """一条岗位招聘信息。"""

    id: str
    title: str
    company: str
    category: str  # 对应 job_catalog 中的岗位方向
    location: str
    salary: str = ""
    education: str = ""
    experience: str = ""
    requirements: list[str] = field(default_factory=list)
    description: str = ""
    tags: list[str] = field(default_factory=list)
    source: str = "seed"
    source_label: str = "本地演示数据"
    url: str = ""
    posted_at: str = ""
    deadline: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "category": self.category,
            "location": self.location,
            "salary": self.salary,
            "education": self.education,
            "experience": self.experience,
            "requirements": self.requirements,
            "description": self.description,
            "tags": self.tags,
            "source": self.source,
            "source_label": self.source_label,
            "url": self.url,
            "posted_at": self.posted_at,
            "deadline": self.deadline,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "JobPosting":
        return cls(
            id=str(data.get("id", "")).strip(),
            title=str(data.get("title", "")).strip(),
            company=str(data.get("company", "")).strip(),
            category=str(data.get("category", "")).strip(),
            location=str(data.get("location", "")).strip(),
            salary=str(data.get("salary", "")).strip(),
            education=str(data.get("education", "")).strip(),
            experience=str(data.get("experience", "")).strip(),
            requirements=str_list(data.get("requirements")),
            description=str(data.get("description", "")).strip(),
            tags=str_list(data.get("tags")),
            source=str(data.get("source", "seed")).strip() or "seed",
            source_label=str(data.get("source_label", "")).strip(),
            url=str(data.get("url", "")).strip(),
            posted_at=str(data.get("posted_at", "")).strip(),
            deadline=str(data.get("deadline", "")).strip(),
        )
