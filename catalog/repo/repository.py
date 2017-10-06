
from api.models.metadata import MetaData


def md_to_csw(md):
    return type(
        'Record',
        (),
        dict(
            uuid=str(md.id),
            csw_typename='',
            metadata_xml=None,
            language='fr',
            csw_type=None,
            title=md.title.fr,
            abstract=md.abstract.fr,
            date=md.revision,
        ))


class Repository:

    """
    from http://docs.pycsw.org/en/latest/repositories.html
    """

    dbtype = 'not-your-business'

    def __init__(self, context, repo_filter):
        self.context = context
        self.filter = repo_filter
        # generate core queryables db and obj bindings
        self.queryables = {}

        for tname in self.context.model['typenames']:
            for qname in self.context.model['typenames'][tname]['queryables']:
                self.queryables[qname] = {}

                for qkey, qvalue in \
                        self.context.model['typenames'][tname]['queryables'][qname].items():
                    self.queryables[qname][qkey] = qvalue

        # flatten all queryables
        # TODO smarter way of doing this
        self.queryables['_all'] = {}
        for qbl in self.queryables:
            self.queryables['_all'].update(self.queryables[qbl])

        self.queryables['_all'].update(self.context.md_core_model['mappings'])

    def query_insert(self):
        pass

    def query_domain(self, domain, typenames, domainquerytype,
                     count=False):
        pass

    def query_ids(self, ids):
        return map(md_to_csw, MetaData.objects.filter(pk__in=ids).all())

    def query_source(self, source):
        return map(md_to_csw, MetaData.objects.filter(source=source).all())

    def query(self, constraint, sortby=None, typenames=None,
              maxrecords=10, startposition=0):
        ''' Query records from underlying repository '''

        print('QA {} {}'.format(maxrecords, startposition))
        # run the raw query and get total
        if 'where' in constraint:  # GetRecords with constraint
            query = MetaData.objects.extra(
                where=[constraint['where']], params=constraint['values'])

        else:  # GetRecords sans constraint
            query = MetaData.objects

        total = query.count()
        # apply sorting, limit and offset
        if sortby is not None:
            if False:
                print('False')
            # if 'spatial' in sortby and sortby['spatial']:  # spatial sort
            #     desc = False
            #     if sortby['order'] == 'DESC':
            #         desc = True
            #     query = query.all()
            # return [str(total), sorted(query, key=lambda x:
            # float(util.get_geometry_area(getattr(x,
            # sortby['propertyname']))),
            # reverse=desc)[startposition:startposition+int(maxrecords)]]
            else:
                if sortby['order'] == 'DESC':
                    pname = '-%s' % sortby['propertyname']
                else:
                    pname = sortby['propertyname']
                results = map(md_to_csw, query.order_by(pname))
                return [str(total),
                        list(results)[startposition:startposition + int(maxrecords)]]
        else:  # no sort
            return [str(total), list(map(md_to_csw, query.all()))[startposition:startposition + int(maxrecords)]]
