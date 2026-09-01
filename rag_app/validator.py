from .models import Entity, Operation, StructuredQueryPlan

ALLOWED = {Entity.RECRUITMENT: {Operation.COUNT_ENROLLED}, Entity.STUDY: {Operation.SEARCH_STUDIES}, Entity.SITE: {Operation.SEARCH_STUDIES}, Entity.MILESTONE: {Operation.LIST_MILESTONES}, Entity.ISSUE: {Operation.LIST_ISSUES}}
ENUM_FILTERS = {"period": {"CURRENT_QUARTER", "LAST_QUARTER"}, "status": {"PLANNED", "ACTIVE", "RECRUITING", "SUSPENDED", "COMPLETED", "CLOSED", "OPEN"}, "phase": {"PHASE_1", "PHASE_2", "PHASE_3", "PHASE_4", "PHASE_I", "PHASE_II", "PHASE_III", "PHASE_IV"}}

class PlanValidator:
    def validate(self, plan: StructuredQueryPlan) -> StructuredQueryPlan:
        if plan.operation not in ALLOWED[plan.entity]:
            raise ValueError(f"Operation {plan.operation} is not allowed for {plan.entity}")
        values = plan.filters.model_dump(exclude_none=True)
        for name, allowed in ENUM_FILTERS.items():
            if name in values and values[name].upper() not in allowed:
                raise ValueError(f"Unsupported {name}: {values[name]}")
        if plan.operation == Operation.COUNT_ENROLLED and not (plan.filters.study_id or plan.filters.study_name):
            raise ValueError("Recruitment counts require study_id or study_name")
        return plan
