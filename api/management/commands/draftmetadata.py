#
#  Copyright (C) 2017 Atelier Cartographique <contact@atelier-cartographique.be>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, version 3 of the License.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.contrib.auth.models import User

from api.models import MetaData


def dictfetchall(cursor):
# from django docs
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

GEOMETRY = dict(
    POINT='Point',
    POLYGON='Polygon',
    LINESTRING='LineString',
    MULTIPOINT='MultiPoint',
    MULTIPOLYGON='MultiPolygon',
    MULTILINESTRING='MultiLineString',
)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('schema', nargs=1)
        parser.add_argument('user_name', nargs=1)

    def handle(self, *args, **options):
        schema = options['schema'][0]
        user_name = options['user_name'][0]
        try:
            user = User.objects.get(username=user_name)
        except User.DoesNotExist:
            self.stderr.write(
                self.style.ERROR(
                    'User {} does not exists'.format(user_name)))
            return

        conn = connections[schema]

        self.stdout.write(
            self.style.SUCCESS('Connected to {}'.format(schema)))

        with conn.cursor() as cursor:
            cursor.execute('''
            SELECT f_table_name, type
            FROM "public"."geometry_columns"
            WHERE f_table_schema = %s
            ''', [schema])
            for r in cursor.fetchall():
                try:
                    table_name = '{}/{}'.format(schema, r[0])
                    geometry_type = GEOMETRY[r[1]]
                    try:
                        md = MetaData.objects.get(
                            resource_identifier=table_name)
                        self.stdout.write(
                            '{} already in catalog => {}'.format(
                                table_name, md.id))
                    except MetaData.DoesNotExist:
                        try:
                            md = MetaData.objects.create_draft(
                                table_name, geometry_type, user)
                            self.stdout.write(
                                self.style.SUCCESS(
                                    'Create {} {} {}'.format(
                                        table_name, geometry_type, md.id)))
                        except Exception as e:
                            self.stderr.write(
                                self.style.ERROR(
                                    'Failed to create metadata for {}: {}'.format(table_name, e)))

                except Exception as e:
                    self.stderr.write(
                        self.style.ERROR(
                            'Failed On {}: {}'.format(table_name, e)))
