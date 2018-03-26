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

from rest_framework import serializers

from ..models import (Thesaurus, MetaData, Topic, Keyword, BoundingBox,
                      PointOfContact, ResponsibleOrganisation, PointOfContact)
from .message import MessageRecordSerializer


class ThesaurusSerializer(serializers.ModelSerializer):
    name = MessageRecordSerializer()

    class Meta:
        model = Thesaurus
        fields = ('id', 'name', 'uri')


class TopicSerializer(serializers.ModelSerializer):
    name = MessageRecordSerializer()

    class Meta:
        model = Topic
        fields = ('id', 'code', 'name', 'thesaurus')


class KeywordSerializer(serializers.ModelSerializer):
    name = MessageRecordSerializer()
    thesaurus = ThesaurusSerializer()

    class Meta:
        model = Keyword
        fields = ('id', 'code', 'name', 'thesaurus')


class BoundingBoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoundingBox
        fields = ('west', 'north', 'east', 'south')


class ResponsibleOrgSerializer(serializers.ModelSerializer):
    organisationName = serializers.SerializerMethodField(
        method_name='get_org_name')
    contactName = serializers.SerializerMethodField(
        method_name='get_org_contact')
    email = serializers.SerializerMethodField(method_name='get_org_email')
    roleCode = serializers.SerializerMethodField(method_name='get_role')

    class Meta:
        model = ResponsibleOrganisation
        fields = ('id', 'organisationName', 'contactName', 'email', 'roleCode')

    def get_role(self, instance):
        return instance.role.code

    def get_org_name(self, instance):
        return MessageRecordSerializer(
            instance=instance.organisation.name).data

    def get_org_contact(self, instance):
        return instance.organisation.contact_name

    def get_org_email(self, instance):
        return instance.organisation.email


class PointOfContactSerializer(serializers.ModelSerializer):
    organisationName = serializers.SerializerMethodField(
        method_name='get_org_name')
    contactName = serializers.SerializerMethodField(method_name='get_name')
    email = serializers.SerializerMethodField()

    class Meta:
        model = PointOfContact
        fields = ('id', 'organisationName', 'contactName', 'email')

    def get_org_name(self, instance):
        return MessageRecordSerializer(
            instance=instance.organisation.name).data

    def get_name(self, instance):
        full_name = instance.user.get_full_name()
        if full_name:
            return full_name
        return instance.user.get_username()

    def get_email(self, instance):
        user = instance.user
        return getattr(user, user.get_email_field_name())


class MetaDataSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    resourceTitle = MessageRecordSerializer(source='title')
    resourceAbstract = MessageRecordSerializer(source='abstract')
    uniqueResourceIdentifier = serializers.CharField(
        source='resource_identifier', )
    geometryType = serializers.CharField(source='geometry_type')
    topicCategory = serializers.PrimaryKeyRelatedField(
        source='topics',
        required=False,
        many=True,
        default=[],
        pk_field=serializers.UUIDField(format='hex_verbose'),
        queryset=Topic.objects)
    keywords = serializers.PrimaryKeyRelatedField(
        required=False,
        many=True,
        default=[],
        pk_field=serializers.UUIDField(format='hex_verbose'),
        queryset=Keyword.objects)
    geographicBoundingBox = BoundingBoxSerializer(source='bounding_box')
    temporalReference = serializers.SerializerMethodField(
        method_name='get_temporal_ref')
    responsibleOrganisation = serializers.PrimaryKeyRelatedField(
        many=True, source='responsible_organisation', read_only=True)
    metadataPointOfContact = serializers.PrimaryKeyRelatedField(
        many=True, source='point_of_contact', read_only=True)
    # responsibleOrganisation = ResponsibleOrgSerializer(
    #     many=True,
    #     source='responsibleorganisation_set',
    #     read_only=True,
    # )
    # metadataPointOfContact = PointOfContactSerializer(
    #     many=True,
    #     source='point_of_contact',
    #     read_only=True,
    # )

    metadataDate = serializers.DateTimeField(source='revision')

    class Meta:
        model = MetaData
        fields = (
            'id',
            'geometryType',
            'resourceTitle',
            'resourceAbstract',
            'uniqueResourceIdentifier',
            'topicCategory',
            'keywords',
            'geographicBoundingBox',
            'temporalReference',
            'responsibleOrganisation',
            'metadataPointOfContact',
            'metadataDate',
            'published',
        )

    def get_id(self, instance):
        return str(instance.id)

    def get_temporal_ref(self, instance):
        return dict(
            creation=instance.creation,
            revision=instance.revision,
        )

    # def get_bounding_box(self, instance):
    #     return [BoundingBoxSerializer(
    #             instance=instance.bounding_box
    #             ).data]

    def update(self, instance, validated_data):
        print('validated_data {}'.format(validated_data))
        title_data = validated_data.get('title')
        abstract_data = validated_data.get('abstract')
        keywords_data = validated_data.get('keywords', [])
        topics_data = validated_data.get('topics', [])
        published_data = validated_data.get('published', False)

        instance.update_title(title_data)
        instance.update_abstract(abstract_data)
        instance.update_keywords(keywords_data)
        instance.update_topics(topics_data)
        instance.update_publication_state(published_data)

        return instance
