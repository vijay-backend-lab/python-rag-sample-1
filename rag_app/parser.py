import re
from google import genai
from google.genai import types
from .models import StructuredQueryPlan

SYSTEM_PROMPT = """Translate clinical-trial questions to a JSON query plan. Allowed entities: RECRUITMENT, STUDY, SITE, MILESTONE, ISSUE. Allowed operations: COUNT_ENROLLED, SEARCH_STUDIES, LIST_MILESTONES, LIST_ISSUES. Allowed filters: study_id, study_name, country, region, status, phase, therapeutic_area, severity, period. period is CURRENT_QUARTER or LAST_QUARTER. Return JSON only; never SQL. Use study_name for a human name."""

class StructuredParser:
    def __init__(self, api_key: str | None, model: str):
        self.client = genai.Client(api_key=api_key) if api_key else None
        self.model = model

    def parse(self, question: str) -> StructuredQueryPlan:
        if self.client:
            response = self.client.models.generate_content(
                model=self.model,
                contents=question,
                config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT, temperature=0,
                    response_mime_type="application/json", response_schema=StructuredQueryPlan),
            )
            return StructuredQueryPlan.model_validate_json(response.text)
        return self._rules(question)

    def _rules(self, question: str) -> StructuredQueryPlan:
        q, filters = question.lower(), {}
        country = re.search(r"\b(?:in|from)\s+([A-Z][A-Za-z .'-]+?)(?:\s+for\b|\s+this\b|\s+last\b|[?.]|$)", question)
        study = re.search(r"\b(?:study|trial)\s+([A-Za-z0-9_-]+)", question, re.I)
        if country: filters["country"] = country.group(1).strip()
        if study: filters["study_name"] = study.group(1).strip()
        if "this quarter" in q: filters["period"] = "CURRENT_QUARTER"
        elif "last quarter" in q: filters["period"] = "LAST_QUARTER"
        phase = re.search(r"phase\s*(?:_|-)?\s*([1-4ivx]+)", q)
        if phase: filters["phase"] = f"PHASE_{phase.group(1).upper()}"
        if "recruiting" in q: filters["status"] = "RECRUITING"
        if "oncology" in q: filters["therapeutic_area"] = "oncology"
        if any(x in q for x in ("how many", "count", "recruited", "enrolled")):
            return StructuredQueryPlan(entity="RECRUITMENT", operation="COUNT_ENROLLED", filters=filters)
        return StructuredQueryPlan(entity="STUDY", operation="SEARCH_STUDIES", filters=filters)
