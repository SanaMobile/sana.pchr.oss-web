from django.db.models import Aggregate, FloatField
from django.db.models.sql.aggregates import Aggregate as SQLAggregate


class CastedSQLAggregate(SQLAggregate):
    sql_template = 'CAST( %(function)s ( CAST( %(field)s AS FLOAT) ) AS FLOAT)'

class CastedSQLAverage(CastedSQLAggregate):
    sql_function = 'AVG'

class CastedSQLMax(CastedSQLAggregate):
    sql_function = 'MAX'

class CastedSQLMin(CastedSQLAggregate):
    sql_function = 'MIN'

class CastedAggregate(Aggregate):
    function = ''

    def add_to_query(self, query, alias, col, source, is_summary):
        aggregate = self.sql_klass(col, source, is_summary,  **self.extra)
        query.aggregates[alias] = aggregate


class CastedAverage(CastedAggregate):
    sql_klass = CastedSQLAverage
    name = 'average'


class CastedMax(CastedAggregate):
    sql_klass = CastedSQLMax
    name = 'max'


class CastedMin(CastedAggregate):
    sql_klass = CastedSQLMin
    name = 'min'