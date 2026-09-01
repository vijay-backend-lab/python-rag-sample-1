from enum import Enum
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

class Route(str, Enum):
    STRUCTURED = "STRUCTURED"
    RAG = "RAG"
    BOTH = "BOTH"

class Entity(str, Enum):
    RECRUITMENT = "RECRUITMENT"
    STUDY = "STUDY"
    SITE = "SITE"
    MILESTONE = "MILESTONE"
    ISSUE = "ISSUE"

class Operation(str, Enum):
    COUNT_ENROLLED = "COUNT_ENROLLED"
    SEARCH_STUDIES = "SEARCH_STUDIES"
    LIST_MILESTONES = "LIST_MILESTONES"
    LIST_ISSUES = "LIST_ISSUES"

class QueryFilters(BaseModel):
    model_config = ConfigDict(extra="forbid")
    study_id: str | None = Field(None, max_length=64)
    study_name: str | None = Field(None, max_length=255)
    country: str | None = Field(None, max_length=100)
    region: str | None = Field(None, max_length=100)
    status: str | None = Field(None, max_length=30)
    phase: str | None = Field(None, max_length=30)
    therapeutic_area: str | None = Field(None, max_length=100)
    severity: str | None = Field(None, max_length=30)
    period: str | None = None

class StructuredQueryPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    entity: Entity
    operation: Operation
    filters: QueryFilters = Field(default_factory=QueryFilters)
    limit: int = Field(default=50, ge=1, le=100)

class SearchHit(BaseModel):
    id: str
    text: str
    score: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
