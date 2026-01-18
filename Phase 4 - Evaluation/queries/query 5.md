Give me the schools in the municipalities with the highest altitude

```sparql
BASE <http://knowdive.disi.unitn.it/etype#>
PREFIX df: <http://knowdive.disi.unitn.it/etype#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

select ?s ?altitude where {
    ?m rdf:type df:Municipality ;
    df:has_altitude ?altitude .
    ?s rdf:type df:School;
    df:has_location ?m
} ORDER BY DESC(?altitude) LIMIT 20
```
