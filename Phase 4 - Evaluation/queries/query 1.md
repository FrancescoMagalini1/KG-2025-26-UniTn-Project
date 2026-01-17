Give me the complete list of schools from the Rovereto municipality

```sparql
BASE <http://knowdive.disi.unitn.it/etype#>
PREFIX df: <http://knowdive.disi.unitn.it/etype#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

select ?s where {
    ?s rdf:type df:School .
    ?m rdf:type df:Municipality .
    ?m df:has_name "rovereto" .
    ?s df:has_location ?m
} limit 100
```
