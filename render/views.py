
from pyproj import Proj

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.views import View
from django.db import connections

from api.models import UserMap, MetaData
from layers.models import get_layer
from .lingua import LinguaWMS, BoundingBox
from .render.base import render_image

def get_bounding_box(schema, table, geometry_column):
    sql = """
SELECT 
    ST_XMin(extent) as minx,
    ST_YMin(extent) as miny,
    ST_XMax(extent) as maxx,
    ST_YMax(extent) as maxy
FROM   
    ST_EstimatedExtent(%s, %s, %s) as extent;
    """

    with connections[schema].cursor() as cursor:
        cursor.execute(sql, [schema, table, geometry_column])
        row = cursor.fetchone()
        return BoundingBox(*row)



lambert_72 = Proj(init='epsg:31370')

def transform_bb(bb):
    if bb == None:
        return BoundingBox(0,0,0,0)

    low = lambert_72(bb.minx, bb.miny, inverse=True)
    high = lambert_72(bb.maxx, bb.maxy, inverse=True)
    t = low + high

    return BoundingBox(*t)

def merge_bb(a, b):
    if b == None:
        return a
    minx = min(a.minx, b.minx)
    miny = min(a.miny, b.miny)
    maxx = max(a.maxx, b.maxx)
    maxy = max(a.maxy, b.maxy)

    return BoundingBox(minx, miny, maxx, maxy)


def get_wms_layer(umap):
    bbox = None
    for l in umap.layers.all():
        try:
            md = l.metadata
            schema, table = md.resource_identifier.split('/')
            model, geometry_field, geometry_field_type = get_layer(schema, table)
            bbox= merge_bb(get_bounding_box(schema, table, geometry_field), bbox)
        except Exception as ex:
            print('Error {}'.format(ex))


    title = '{} - {}'.format(umap.title.fr, umap.title.nl)
    return dict(
        name=umap.id,
        title=title,
        srs='31370',
        bbox=bbox,
        geo=transform_bb(bbox),
    )



class WMS(View):

    cap_req_parms_m = [
        LinguaWMS.Request.service,
        # LinguaWMS.Request.request
    ]
    cap_req_parms_o = [
        LinguaWMS.Request.version,
        LinguaWMS.Request.format,
        LinguaWMS.Request.updatesequence
    ]
    map_req_parms_m = [
        LinguaWMS.Request.version,
        # LinguaWMS.Request.request,
        LinguaWMS.Request.layers,
        LinguaWMS.Request.styles,
        LinguaWMS.Request.crs,
        LinguaWMS.Request.bbox,
        LinguaWMS.Request.width,
        LinguaWMS.Request.height
    ]
    map_req_parms_o = [
        LinguaWMS.Request.transparent,
        LinguaWMS.Request.bgcolor,
        LinguaWMS.Request.exceptions,
        LinguaWMS.Request.time,
        LinguaWMS.Request.elevation
    ]

    def get_capabilities (self, request):
        query = request.GET
        params = LinguaWMS.Request.gets(query, WMS.cap_req_parms_m)
        params.update(
            LinguaWMS.Request.gets(query, WMS.cap_req_parms_o, False)
        )

        ctx = {
            'wms_url': 'http://127.0.0.1:8000/render/',
            'version': '1.3.0',
            'title': 'GeoData Render',
            'mime': 'image/png',
        }
        ctx['layers'] = [get_wms_layer(m) for m in UserMap.objects.all()]

        return render(request, 'render/wms_capabilities.xml', 
                    context=ctx, content_type='application/xml')


    def get_map (self, request):
        query = request.GET
        params = LinguaWMS.Request.gets(query, WMS.map_req_parms_m)

        # print(params)

        size = [params['WIDTH'], params['HEIGHT']]
        bbox = params['BBOX']
        map_id = params['LAYERS'][0]

        umap = UserMap.objects.get(pk=map_id)
        img = render_image(umap, size, bbox)

        return HttpResponse(img.tostring('png32'), content_type='image/png')
        

        # tile_req = proto.Request('tile', 'tile.get_tile',
        #                     request.session_id, params)

        # tile_response = yield from client.get(tile_req)
        # if proto.is_ok(tile_response):
        #     data = tile_response.data
        #     if 'png' in data:
        #         pack = b64decode(data['png'].encode())
        #         headers = MultiDict({
        #             # 'CONTENT-DISPOSITION': 'attachment; filename="{}-{}-{}.png"'
        #         })
        #         response = web.StreamResponse(headers=headers)
        #         response.content_type = config_tile.get('mime')
        #         response.content_length = len(pack)
        #         yield from response.prepare(request)
        #         response.write(pack)
        #         return response
        # return web.HTTPInternalServerError(
        #         text=proto.error_message(tile_response)
        #     )


    def get (self, request):
        wms_req = LinguaWMS.Request.get(request.GET,
                                        LinguaWMS.Request.request)

        if LinguaWMS.Token.GetCapabilities == wms_req:
            return self.get_capabilities(request)
        elif LinguaWMS.Token.GetMap == wms_req:
            return  self.get_map(request)

        return HttpResponseBadRequest(wms_req)
