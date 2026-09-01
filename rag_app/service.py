from .models import Route
from .parser import StructuredParser
from .rag import ElasticsearchRAG
from .repository import ClinicalRepository
from .router import QueryRouter
from .validator import PlanValidator

class ClinicalTrialAssistant:
    def __init__(self, router, parser, validator, repository, rag):
        self.router, self.parser, self.validator, self.repository, self.rag = router, parser, validator, repository, rag

    @classmethod
    def from_settings(cls, s):
        return cls(QueryRouter(), StructuredParser(s.gemini_api_key, s.gemini_model), PlanValidator(), ClinicalRepository(s.mysql_url), ElasticsearchRAG(s.elasticsearch_url, s.elasticsearch_index, s.gemini_api_key, s.embedding_model, s.embedding_dimensions))

    def answer(self, question):
        route = self.router.route(question)
        response = {"question": question, "route": route.value}
        if route in (Route.STRUCTURED, Route.BOTH):
            plan = self.validator.validate(self.parser.parse(question))
            response["plan"] = plan.model_dump(mode="json", exclude_none=True)
            response["data"] = self.repository.execute(plan)
        if route in (Route.RAG, Route.BOTH):
            response["sources"] = self.rag.search(question)
        return response
