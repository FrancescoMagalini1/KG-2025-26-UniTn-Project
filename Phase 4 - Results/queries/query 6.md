Give me the schools from the least populated municipalities

```sparql
BASE <http://knowdive.disi.unitn.it/etype#>
PREFIX df: <http://knowdive.disi.unitn.it/etype#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

select ?s ?population where {
    ?m rdf:type df:Municipality ;
    df:has_population ?population .
    ?s rdf:type df:School;
    df:has_location ?m
} ORDER BY ASC(?population) LIMIT 20
```
