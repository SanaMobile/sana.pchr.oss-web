from django.db.models import Lookup, CharField

class CastedLookup(Lookup):
    lookup_name = ''
    lookup_seq = ''

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        lookup_string = 'CAST( %s AS float) ' + self.lookup_seq + ' %s'
        return lookup_string % (lhs, rhs), params

@CharField.register_lookup
class CastedGreaterLookup(CastedLookup):
    lookup_seq = '>'
    lookup_name = 'cgt'

@CharField.register_lookup
class CastedLessLookup(CastedLookup):
    lookup_seq = '<'
    lookup_name = 'clt'


@CharField.register_lookup
class CastedGreaterEqLookup(CastedLookup):
    lookup_seq = '>='
    lookup_name = 'cgte'

@CharField.register_lookup
class CastedLessEqLookup(CastedLookup):
    lookup_seq = '<='
    lookup_name = 'clte'
