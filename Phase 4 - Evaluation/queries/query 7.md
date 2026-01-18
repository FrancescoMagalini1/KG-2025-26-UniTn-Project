Give me the list of schools with the highest admission rates to the next year

```sparql
BASE <http://knowdive.disi.unitn.it/etype#>
PREFIX df: <http://knowdive.disi.unitn.it/etype#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

select ?s ?admission_rate where {
    ?s rdf:type df:School;
    df:has_admission_rate ?admission_rate
} ORDER BY DESC(?admission_rate) LIMIT 50
```
