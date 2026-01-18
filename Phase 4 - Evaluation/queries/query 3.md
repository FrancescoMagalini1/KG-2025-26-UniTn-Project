Give me the list of kindergartens from Lavis

```sparql
BASE <http://knowdive.disi.unitn.it/etype#>
PREFIX df: <http://knowdive.disi.unitn.it/etype#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

select ?s where {
    ?m rdf:type df:Municipality ;
    df:has_name "lavis" .
    ?s rdf:type df:School;
    df:has_location ?m .
    ?s df:has_school_type "infanzia"
}
```
