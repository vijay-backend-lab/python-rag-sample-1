import re
from .models import Route

class QueryRouter:
    structured = re.compile(r"\b(how many|count|show|list|find|enrolled|recruited|screened|status|phase|milestone|issue|trial|site|this quarter|last quarter)\b", re.I)
    rag = re.compile(r"\b(why|explain|summarize|describe|protocol|policy|guideline|document|risk|context)\b", re.I)

    def route(self, question: str) -> Route:
        structured, rag = bool(self.structured.search(question)), bool(self.rag.search(question))
        if structured and rag:
            return Route.BOTH
        return Route.STRUCTURED if structured else Route.RAG
