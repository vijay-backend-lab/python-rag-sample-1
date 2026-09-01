import pytest
from rag_app.models import Route, StructuredQueryPlan
from rag_app.parser import StructuredParser
from rag_app.router import QueryRouter
from rag_app.validator import PlanValidator
from rag_app.ingestion import ThirdPartyIngestionService

def test_routes_structured_question():
    assert QueryRouter().route("How many participants were recruited in Germany for Study ABC this quarter?") == Route.STRUCTURED

def test_rules_parser_recruitment_example():
    plan = StructuredParser(None, "unused").parse("How many participants were recruited in Germany for Study ABC this quarter?")
    assert (plan.operation.value, plan.filters.country, plan.filters.study_name, plan.filters.period) == ("COUNT_ENROLLED", "Germany", "ABC", "CURRENT_QUARTER")

def test_validator_rejects_bad_pair():
    plan = StructuredQueryPlan(entity="STUDY", operation="COUNT_ENROLLED", filters={"study_id": "ABC"})
    with pytest.raises(ValueError):
        PlanValidator().validate(plan)

def test_third_party_documents_are_validated():
    class Client:
        def pages(self):
            yield [{"id": "doc-1", "text": "Protocol guidance", "metadata": {"study_id": "ABC"}}]
    docs = list(ThirdPartyIngestionService(Client(), None, "vendor").documents())
    assert docs == [{"id": "doc-1", "text": "Protocol guidance", "metadata": {"study_id": "ABC"}}]
