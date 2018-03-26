from api.models.metadata import MetaData
from django.db.models import F, Value as V
from django.db.models.functions import Concat


def md_to_csw(md):
    return type('Record', (),
                dict(
                    uuid=str(md.id),
                    csw_typename='gmd:MD_Metadata',
                    metadata_xml=None,
                    language='fr',
                    csw_type='gmd:MD_Metadata',
                    title=md.title.fr,
                    abstract=md.abstract.fr,
                    date=md.revision,
                    wkt_bbox=md.bounding_box.to_polygon_wkt()))


class Repository:
    """
    from http://docs.pycsw.org/en/latest/repositories.html
    """

    dbtype = 'not-your-business'

    def __init__(self, context, repo_filter):
        self.context = context
        self.filter = repo_filter
        self.fts = False

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

    def query_domain(self, domain, typenames, domainquerytype, count=False):
        print('csw#query_domain {}'.format(domain))
        pass

    def query_ids(self, ids):
        print('csw#query_ids {}'.format(ids))
        return map(md_to_csw, MetaData.objects.filter(pk__in=ids))

    def query_source(self, source):
        print('csw#query_source {}'.format(source))
        return map(md_to_csw, MetaData.objects.filter(source=source))

    def get_queryset(self):
        ws = V(' ')

        def message(fname):
            fr = '{}__fr'.format(fname)
            nl = '{}__nl'.format(fname)
            return Concat(fr, ws, nl)

        def bf(f):
            return 'bounding_box__{}'.format(f)

        bbox = Concat(
            V('POLYGON(('), ws, bf('west'), ws, bf('south'), ws,
            bf('west'), ws, bf('north'), ws, bf('east'), ws, bf('north'), ws,
            bf('east'), ws, bf('south'), ws, bf('west'), ws, bf('south'),
            V('))'))

        return MetaData.objects.annotate(
            csw_anytext=message('abstract'),
            # csw_typename=V('gmd:MD_Metadata'),
            # csw_schema=V('http://www.isotc211.org/2005/gmd'),
            # wkt_bbox=bbox,
        ).order_by('id')

    def query(self,
              constraint,
              sortby=None,
              typenames=None,
              maxrecords=10,
              startposition=0):
        ''' Query records from underlying repository '''

        # q_type = constraint['type']
        # q_values = constraint['values']
        # q_where = constraint['where']
        print('[{}]'.format(constraint))

        try:
            # # run the raw query and get total
            # if 'where' in constraint:  # GetRecords with constraint
            #     query = self.get_queryset().extra(
            #         where=[constraint['where']], params=constraint['values'])

            # else:  # GetRecords sans constraint
            #     query = self.get_queryset().all()
            query = self.get_queryset()
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
                    return [
                        str(total),
                        list(results)[startposition:
                                      startposition + int(maxrecords)]
                    ]
            else:  # no sort
                return [
                    str(total),
                    list(map(md_to_csw, query.all()))[
                        startposition:startposition + int(maxrecords)]
                ]

        except Exception as ex:
            print('Exception {}'.format(ex))
            return []