Give me the schools with the highest number of students

```sparql
BASE <http://knowdive.disi.unitn.it/etype#>
PREFIX df: <http://knowdive.disi.unitn.it/etype#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

select distinct ?s  where {
    ?i rdf:type df:Students_Information;
    df:has_number_of_students ?n .
    ?s rdf:type df:School;
    df:has_students_information ?i
} ORDER BY DESC(?n) LIMIT 20
```
