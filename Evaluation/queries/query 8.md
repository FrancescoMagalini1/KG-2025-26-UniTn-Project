Give me the list of private high schools from Pergine Valsugana, ordered by graduation rates

```sparql
BASE <http://knowdive.disi.unitn.it/etype#>
PREFIX df: <http://knowdive.disi.unitn.it/etype#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

select ?s ?admission_rate where {
    ?m rdf:type df:Municipality;
    df:has_name "pergine valsugana" .
    ?s rdf:type df:School;
    df:has_admission_rate ?admission_rate;
    df:has_location ?m;
    df:has_school_type "secondaria di secondo grado"
} ORDER BY DESC(?admission_rate)
```
