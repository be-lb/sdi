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
from layers.models import get_layer


def dictfetchall(cursor):
# from django docs
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


class Command(BaseCommand):

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('schema', nargs='+')

    def handle(self, *args, **options):
        schemas = options['schema']
        for schema in schemas:
            conn = connections[schema]
            # self.stdout.write(
            #     self.style.SUCCESS('Connected to {}'.format(schema)))
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM "public"."geometry_columns";')
                for r in dictfetchall(cursor):
                    r_schema = r['f_table_schema']
                    r_table = r['f_table_name']
                    if r_schema == schema:
                        # self.stdout.write(self.style.SQL_TABLE(r_table))
                        try:
                            model, geometry_field, geometry_field_type = get_layer(
                                r_schema, r_table)
                        except NoPKError:
                            err_msg = 'NoPrimaryKeyError on {}.{}'.format(
                                r_schema, r_table)
                            self.stdout.write(self.style.ERROR(err_msg))
                            continue
                        except Exception as e:
                            err_msg = 'ERROR\nget_layer({}, {}) \n{}'.format(
                                r_schema, r_table, e)
                            self.stdout.write(self.style.ERROR(err_msg))
                            continue

                        try:
                            model.objects.first()
                        except Exception as e:
                            err_msg = 'ERROR\nfirst({}, {}) \n{}'.format(
                                r_schema, r_table, e)
                            self.stdout.write(self.style.ERROR(err_msg))
                            continue

                        self.stdout.write(self.style.SQL_TABLE('{}.{}'.format(r_schema, r_table)))