
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

import uuid
from django.utils import timezone

from django.db import models
from django.contrib.auth.models import User

from .message import simple_message, message_field


class Thesaurus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = message_field('thesaurus_name')
    uri = models.URLField()

    def __str__(self):
        return str(self.uri)


class Topic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=124)
    name = message_field('topic_name')
    thesaurus = models.ForeignKey(Thesaurus)

    def __str__(self):
        return str(self.code)


class Keyword(Topic):
    pass


class BoundingBox(models.Model):
    west = models.FloatField(default=0)
    north = models.FloatField(default=0)
    east = models.FloatField(default=0)
    south = models.FloatField(default=0)

    def __str__(self):
        return '{}, {}, {}, {}'.format(
            self.west, self.south, self.east, self.north)


class Organisation(models.Model):
    name = message_field('org_name')
    email = models.EmailField()
    contact_name = models.TextField()

    def __str__(self):
        return '{}/{}'.format(self.name.fr, self.name.nl)


class PointOfContact(models.Model):
    user = models.ForeignKey(User)
    organisation = models.ForeignKey(
        Organisation,
        related_name='point_of_contact',
    )

    def __str__(self):
        return '{} @ {}'.format(self.user.get_username(), self.organisation)


class Role(models.Model):
    code = models.CharField(max_length=124)
    name = message_field('role')

    def __str__(self):
        return str(self.code)


class MetaDataManager(models.Manager):

    def create_draft(self, table_name, geometry_type, user):
        poc = user.pointofcontact_set.first()
        org = poc.organisation
        bb = BoundingBox.objects.create()
        title_rec = simple_message(table_name)
        abstract_rec = simple_message('An abstract for {}'.format(table_name))
        try:
            role = Role.objects.get(code='author')
        except Role.DoesNotExist:
            role_name = simple_message('author')
            role = Role.objects.create(code='author', name=role_name)

        md = MetaData.objects.create(
            title=title_rec,
            abstract=abstract_rec,
            resource_identifier=table_name,
            bounding_box=bb,
            geometry_type=geometry_type,
        )

        md.point_of_contact.add(poc)
        ResponsibleOrganisation.objects.create(
            organisation=org,
            md=md,
            role=role,
        )

        return md


class MetaData(models.Model):
    POINT = 'Point'
    POLYGON = 'Polygon'
    LINESTRING = 'LineString'
    MULTIPOINT = 'MultiPoint'
    MULTIPOLYGON = 'MultiPolygon'
    MULTILINESTRING = 'MultiLineString'

    GEOMETRY = (
        (POINT, POINT),
        (LINESTRING, LINESTRING),
        (POLYGON, POLYGON),
        (MULTIPOINT, MULTIPOINT),
        (MULTILINESTRING, MULTILINESTRING),
        (MULTIPOLYGON, MULTIPOLYGON),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = message_field('md_title')
    abstract = message_field('md_abstract')
    resource_identifier = models.CharField(max_length=1024)
    geometry_type = models.CharField(max_length=16, choices=GEOMETRY)
    published = models.BooleanField(default=False)

    topics = models.ManyToManyField(Topic, related_name='md_topic')
    keywords = models.ManyToManyField(Keyword, related_name='md_keyword')

    bounding_box = models.ForeignKey(BoundingBox)

    creation = models.DateTimeField(auto_now_add=True, editable=False)
    revision = models.DateTimeField(default=timezone.now, editable=False)

    responsible_organisation = models.ManyToManyField(
        Organisation,
        through='ResponsibleOrganisation',
        through_fields=('md', 'organisation'),
        related_name='md_responsible_org',
    )

    point_of_contact = models.ManyToManyField(
        PointOfContact,
        related_name='md_point_of_contact',
    )

    objects = MetaDataManager()

    def __str__(self):
        return '[{}], {}'.format(self.resource_identifier, self.title)

    def update_title(self, data):
        self.title.update_record(**data)

    def update_abstract(self, data):
        self.abstract.update_record(**data)


class ResponsibleOrganisation(models.Model):
    organisation = models.ForeignKey(Organisation)
    md = models.ForeignKey(MetaData)
    role = models.ForeignKey(Role)
