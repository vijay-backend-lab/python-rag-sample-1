from datetime import date
from sqlalchemy import MetaData, Table, and_, func, select
from .database import create_read_only_mysql_engine
from .models import Operation, StructuredQueryPlan

class ClinicalRepository:
    def __init__(self, mysql_url: str):
        self.engine = create_read_only_mysql_engine(mysql_url)
        metadata = MetaData()
        self.study = Table("study", metadata, autoload_with=self.engine)
        self.site = Table("site", metadata, autoload_with=self.engine)
        self.participant = Table("participant", metadata, autoload_with=self.engine)

    @staticmethod
    def _quarter(period):
        if not period: return None
        today, quarter, year = date.today(), (date.today().month - 1) // 3, date.today().year
        if period == "LAST_QUARTER":
            quarter -= 1
            if quarter < 0: quarter, year = 3, year - 1
        start = date(year, quarter * 3 + 1, 1)
        end = date(year + (quarter == 3), ((quarter + 1) % 4) * 3 + 1, 1)
        return start, end

    def execute(self, plan: StructuredQueryPlan):
        f = plan.filters
        if plan.operation == Operation.COUNT_ENROLLED:
            stmt = select(func.count(func.distinct(self.participant.c.participant_id)).label("enrolled_count")).select_from(self.participant.join(self.study).join(self.site))
            clauses = [self.participant.c.enrollment_date.is_not(None)]
            if f.study_id: clauses.append(self.study.c.study_id == f.study_id)
            if f.study_name: clauses.append(self.study.c.study_name == f.study_name)
            if f.country: clauses.append(self.site.c.country == f.country)
            if f.region: clauses.append(self.site.c.region == f.region)
            window = self._quarter(f.period)
            if window: clauses += [self.participant.c.enrollment_date >= window[0], self.participant.c.enrollment_date < window[1]]
            stmt = stmt.where(and_(*clauses))
        else:
            stmt, clauses = select(self.study).distinct().limit(plan.limit), []
            if f.country or f.region: stmt = stmt.select_from(self.study.join(self.site))
            for attr in ("study_id", "study_name", "status", "phase"):
                if getattr(f, attr): clauses.append(getattr(self.study.c, attr) == getattr(f, attr))
            if f.therapeutic_area: clauses.append(self.study.c.therapeutic_area.ilike(f"%{f.therapeutic_area}%"))
            if f.country: clauses.append(self.site.c.country == f.country)
            if f.region: clauses.append(self.site.c.region == f.region)
            if clauses: stmt = stmt.where(and_(*clauses))
        with self.engine.connect() as conn:
            return [dict(row._mapping) for row in conn.execute(stmt)]
