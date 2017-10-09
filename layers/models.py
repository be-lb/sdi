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

from django.contrib.gis.db import models
from django.db import models as django_models
from django.conf import settings

import keyword
import re
from collections import OrderedDict
from functools import partial

from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.models.constants import LOOKUP_SEP

requires_system_checks = False


def get_manager(schema):
    m = models.Manager().db_manager(schema)
    # print('Created Manager On DB: {} {}'.format(schema, m.uuid))
    return m


def inspect_table(schema, table_name):
    connection = connections[schema]

    # 'table_name_filter' is a stealth option

    def table2model(table_name):
        return re.sub(r'[^a-zA-Z0-9]', '', table_name.title())

    def strip_prefix(s):
        return s[1:] if s.startswith("u'") else s

    with connection.cursor() as cursor:
        known_models = []
        try:
            try:
                relations = connection.introspection.get_relations(cursor,
                                                                   table_name)
            except NotImplementedError:
                relations = {}
            try:
                constraints = connection.introspection.get_constraints(
                    cursor, table_name)
            except NotImplementedError:
                constraints = {}
            primary_key_column = connection.introspection.get_primary_key_column(
                cursor, table_name)
            unique_columns = [
                c['columns'][0] for c in constraints.values()
                if c['unique'] and len(c['columns']) == 1
            ]
            table_description = connection.introspection.get_table_description(
                cursor, table_name)
        except Exception as e:
            # yield "# Unable to inspect table '%s'" % table_name
            # yield "# The error was: %s" % e
            raise e

        # yield 'class %s(models.Model):' % table2model(table_name)
        known_models.append(table2model(table_name))
        used_column_names = []  # Holds column names used in the table so far
        column_to_field_name = {}  # Maps column names to names of model fields

        model_fields = dict()
        geometry_field = None
        geometry_type = None
        for row in table_description:
            comment_notes = []
            # Holds Field notes, to be displayed in a Python comment.
            extra_params = OrderedDict()
            # Holds Field parameters such as
            # 'db_column'.
            column_name = row[0]
            is_relation = column_name in relations

            att_name, params, notes = normalize_col_name(
                column_name, used_column_names, is_relation)
            extra_params.update(params)
            comment_notes.extend(notes)

            used_column_names.append(att_name)
            column_to_field_name[column_name] = att_name

            # Add primary_key and unique, if necessary.
            if column_name == primary_key_column:
                extra_params['primary_key'] = True
            elif column_name in unique_columns:
                extra_params['unique'] = True

            if is_relation:
                rel_to = ("self" if relations[column_name][1] == table_name
                          else table2model(relations[column_name][1]))
                if rel_to in known_models:
                    field_type = 'ForeignKey(%s' % rel_to
                else:
                    field_type = "ForeignKey('%s'" % rel_to
            else:
                # Calling `get_field_type` to get the field type string and any
                # additional parameters and notes.
                field_type, field_params, is_geometry = get_field_type(
                    connection, table_name, row)
                extra_params.update(field_params)

            print('>> {}: {}'.format(att_name, field_type))

            if (not geometry_field) and is_geometry:
                geometry_field = att_name
                geometry_type = field_type

            # Don't output 'id = meta.AutoField(primary_key=True)', because
            # that's assumed if it doesn't exist.
            if att_name == 'id' and extra_params == {'primary_key': True}:
                if field_type == 'AutoField':
                    continue
                elif field_type == 'IntegerField' and not connection.features.can_introspect_autofield:
                    comment_notes.append('AutoField?')

            # Add 'null' and 'blank', if the 'null_ok' flag was present in the
            # table description.
            if row[6]:  # If it's NULL...
                if field_type == 'BooleanField':
                    field_type = 'NullBooleanField'
                else:
                    extra_params['blank'] = True
                    extra_params['null'] = True

            # field_desc = '%s = %s%s' % (
            #     att_name,
            # Custom fields will have a dotted path
            #     '' if '.' in field_type else 'models.',
            #     field_type,
            # )
            # if field_type.startswith('ForeignKey'):
            #     field_desc += ', models.DO_NOTHING'

            if field_type == 'DecimalField':
                # print('DecimalField {}'.format(extra_params))
                extra_params.pop('decimal_places')
                extra_params.pop('max_digits')
                extra_params['decimal_places'] = 16
                extra_params['max_digits'] = 32

            try:
                F = getattr(models.fields, field_type)
            except AttributeError:
                F = getattr(django_models.fields, field_type)

            model_fields[att_name] = F(**extra_params)

        meta_class = get_meta(table_name, constraints, column_to_field_name)
        model_fields.update(
            dict(
                Meta=meta_class,
                __module__='layers.models',
                objects=get_manager(schema)))

        T = type(table2model(table_name), (models.Model, ), model_fields)
        return T, geometry_field, geometry_type


def normalize_col_name(col_name, used_column_names, is_relation):
    """
    Modify the column name to make it Python-compatible as a field name
    """
    field_params = {}
    field_notes = []

    new_name = col_name.lower()
    if new_name != col_name:
        field_notes.append('Field name made lowercase.')

    if is_relation:
        if new_name.endswith('_id'):
            new_name = new_name[:-3]
        else:
            field_params['db_column'] = col_name

    new_name, num_repl = re.subn(r'\W', '_', new_name)
    if num_repl > 0:
        field_notes.append('Field renamed to remove unsuitable characters.')

    if new_name.find(LOOKUP_SEP) >= 0:
        while new_name.find(LOOKUP_SEP) >= 0:
            new_name = new_name.replace(LOOKUP_SEP, '_')
        if col_name.lower().find(LOOKUP_SEP) >= 0:
            # Only add the comment if the double underscore was in the original
            # name
            field_notes.append(
                "Field renamed because it contained more than one '_' in a row."
            )

    if new_name.startswith('_'):
        new_name = 'field%s' % new_name
        field_notes.append("Field renamed because it started with '_'.")

    if new_name.endswith('_'):
        new_name = '%sfield' % new_name
        field_notes.append("Field renamed because it ended with '_'.")

    if keyword.iskeyword(new_name):
        new_name += '_field'
        field_notes.append(
            'Field renamed because it was a Python reserved word.')

    if new_name[0].isdigit():
        new_name = 'number_%s' % new_name
        field_notes.append(
            "Field renamed because it wasn't a valid Python identifier.")

    if new_name in used_column_names:
        num = 0
        while '%s_%d' % (new_name, num) in used_column_names:
            num += 1
        new_name = '%s_%d' % (new_name, num)
        field_notes.append('Field renamed because of name conflict.')

    if col_name != new_name and field_notes:
        field_params['db_column'] = col_name

    return new_name, field_params, field_notes


def get_field_type(connection, table_name, row):
    """
    Given the database connection, the table name, and the cursor row
    description, this routine will return the given field type name, as
    well as any additional keyword parameters and notes for the field.
    """
    field_params = OrderedDict()
    field_notes = []
    is_geometry = False
    try:
        field_type = connection.introspection.get_field_type(row[1], row)
    except KeyError:
        field_type = 'TextField'
        field_notes.append('This field type is a guess.')

    # This is a hook for data_types_reverse to return a tuple of
    # (field_type, field_params_dict).
    if type(field_type) is tuple:
        field_type, new_params = field_type
        field_params.update(new_params)

    # Add max_length for all CharFields.
    if field_type == 'CharField' and row[3]:
        field_params['max_length'] = int(row[3])

    if field_type == 'DecimalField':
        if row[4] is None or row[5] is None:
            field_notes.append(
                'max_digits and decimal_places have been guessed, as this '
                'database handles decimal fields as float')
            field_params['max_digits'] = row[4] if row[4] is not None else 10
            field_params['decimal_places'] = row[
                5] if row[5] is not None else 5
        else:
            field_params['max_digits'] = row[4]
            field_params['decimal_places'] = row[5]

    if field_type == 'GeometryField':
        geo_col = row[0]
        # Getting a more specific field type and any additional parameters
        # from the `get_geometry_type` routine for the spatial backend.
        field_type, geo_params = connection.introspection.get_geometry_type(
            table_name, geo_col)
        field_params.update(geo_params)
        is_geometry = True

    return field_type, field_params, is_geometry
    # return getattr(models.fields, field_type), field_params


def get_meta(table_name, constraints, column_to_field_name):
    """
    Return a sequence comprising the lines of code necessary
    to construct the inner Meta class for the model corresponding
    to the given database table name.
    """
    # unique_together = []
    # for index, params in constraints.items():
    #     if params['unique']:
    #         columns = params['columns']
    #         if len(columns) > 1:
    # we do not want to include the u"" or u'' prefix
    # so we build the string rather than interpolate the tuple
    #             tup = '(' + ', '.join("'%s'" % column_to_field_name[c] for c in columns) + ')'
    #             unique_together.append(tup)

    return type(
        'Meta', (),
        dict(
            managed=False, db_table=table_name, app_label='layers'))
    # if unique_together:
    #     tup = '(' + ', '.join(unique_together) + ',)'
    #     meta += ["        unique_together = %s" % tup]
    # return meta


LAYER_MODELS = dict()


def get_layer(schema, table_name):
    """returns a tuple (Model, geometry_field, geometry_field_type) for a given table in given schema
    """
    fn = '{}.{}'.format(schema, table_name)
    if fn not in LAYER_MODELS:
        LAYER_MODELS[fn] = inspect_table(schema, table_name)

    return LAYER_MODELS.get(fn)
