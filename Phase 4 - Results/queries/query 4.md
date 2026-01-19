Give me the list of primary schools from Trento and nearby municipalities.

```sparql
BASE <http://knowdive.disi.unitn.it/etype#>
PREFIX df: <http://knowdive.disi.unitn.it/etype#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

select ?s where {
    ?m1 rdf:type df:Municipality ;
    df:has_name "trento" .
    ?m2 rdf:type df:Municipality ;
    df:has_bordering_municipality ?m1 .
    ?s rdf:type df:School;
    df:has_school_type "primaria" .
    {?s df:has_location ?m1  }
    UNION
    {?s df:has_location ?m2  }
}
```
