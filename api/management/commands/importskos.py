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

from rdflib import Graph, RDF
from rdflib.namespace import SKOS, DC

from django.core.management.base import BaseCommand, CommandError

from api.models.message import message
from api.models.metadata import Thesaurus, Keyword



def get_one(what, gen):
    try:
        return list(gen)[0]
    except IndexError as ex:
        print('Failed at getting one of {}'.format(what))
        raise ex


def get_label(lang, plist):
    def f(t):
        l = t[1]
        lc = l.language
        return lc == lang
    _, lit = get_one('Label', filter(f, plist))
    return lit



        


class Command(BaseCommand):
    help = """Import keywords from a thesaurus in the form of an RDF file in the SKOS style
"""

    output_transaction = True

    def add_arguments(self, parser):
        parser.add_argument('file')

    def handle(self, *args, **options):
        file_path = options['file']
        store = Graph()
        store.parse(file_path)
        
        self.load_scheme(store)

        
    def load_keywords(self, store, scheme, thesaurus):
        for i, kw in enumerate(store.subjects(RDF.type, SKOS.Concept)):
            labels = store.preferredLabel(kw)
            fr = get_label('fr', labels).toPython()
            nl = get_label('nl', labels).toPython()
            code = kw.toPython()
            name = message(fr, nl)
            Keyword.objects.create(
                code=code,
                name=name,
                thesaurus=thesaurus,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    '#{}'.format(i+1)) + 
                    '  {} // {}'.format(fr, nl)) 


    def load_scheme(self, store):
        scheme = get_one('Concept Scheme',
        store.subjects(RDF.type, SKOS.ConceptScheme))

        title = get_one('title',
        store.objects(scheme, DC.title))
        
        uri = scheme.toPython()
        name = message(title, title)

        thesaurus = Thesaurus.objects.create(name=name, uri=uri)

        self.stdout.write('Thesaurus ' + self.style.SUCCESS(title))
        self.load_keywords(store, scheme, thesaurus)


