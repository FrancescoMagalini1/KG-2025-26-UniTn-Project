Give me the number of high schools in San Michele All'Adige

```sparql
BASE <http://knowdive.disi.unitn.it/etype#>
PREFIX df: <http://knowdive.disi.unitn.it/etype#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

select (COUNT(?s) As ?count) where {
    ?m rdf:type df:Municipality ;
    df:has_name "san michele all'adige" .
    ?s rdf:type df:School;
    df:has_location ?m .
    ?s df:has_school_type "secondaria di secondo grado"
}
```
