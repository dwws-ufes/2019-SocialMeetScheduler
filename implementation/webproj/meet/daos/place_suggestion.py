# -*- encoding: utf-8 -*-

from typing import List
import SPARQLWrapper

from ..adts import PlaceSuggestion
from ...mwt import MWT


class PlaceSuggestionDAO:
    @staticmethod
    @MWT(1800)
    def get(namehint: str) -> List[PlaceSuggestion]:
        if namehint == '':
            return list()
        escapednamehint = (
            namehint
            .lower()
            .replace('\n', '\\n')
            .replace('\"', '\\\"')
            .replace('\t', '\\t')
        )
        sw = SPARQLWrapper.SPARQLWrapper(
            "http://dbpedia.org/sparql",
            returnFormat=SPARQLWrapper.JSON
        )
        q = f"""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX dbp: <http://dbpedia.org/property/>
            PREFIX dbr: <http://dbpedia.org/resource/>
            PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>

            SELECT DISTINCT
                ?plc (LANG(?nm) as ?lang) ?lat ?long ?nm ?abs
            WHERE {{
                ?plc rdfs:label ?nm ;
                dbo:abstract ?abs ;
                (dbp:latitude|geo:lat) ?lat ;
                (dbp:longitude|geo:long) ?long .
                FILTER(
                    LANG(?nm)=LANG(?abs)
                ) .
                FILTER(
                    STRSTARTS(
                        LCASE(STR(
                            ?nm
                        )),
                        "{escapednamehint}"
                    )
                ) .
            }}
            LIMIT 15
        """
        # sw.setTimeout(30)
        sw.setQuery(q)
        results = sw.query().convert()
        return [
            PlaceSuggestion(
                result["lang"]["value"],
                result["lat"]["value"],
                result["long"]["value"],
                result["nm"]["value"],
                result["abs"]["value"],
                result["plc"]["value"]
            )
            for result in results["results"]["bindings"]
        ]
