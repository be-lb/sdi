from django.core.management.base import BaseCommand, CommandError
from django.db import connections


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
            self.stdout.write(
                self.style.SUCCESS('Connected to {}'.format(schema)))
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM "public"."geometry_columns";')
                for r in dictfetchall(cursor):
                    r_schema = r['f_table_schema']
                    r_table = r['f_table_name']
                    if r_schema == schema:
                        self.stdout.write(self.style.SQL_TABLE(r_table))
