Give me the list of elementary schools within a 20km range from Trento

```sparql
BASE <http://knowdive.disi.unitn.it/etype#>
PREFIX df: <http://knowdive.disi.unitn.it/etype#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX ofn: <http://www.ontotext.com/sparql/functions/>

select distinct ?s ?distance_km_approx  where {
    ?m rdf:type df:Municipality;
    df:has_latitude ?lat0;
    df:has_longitude ?lon0;
    df:has_name "trento" .
    ?m1 rdf:type df:Municipality;
    df:has_latitude ?lat;
    df:has_longitude ?lon;
    BIND( (?lon - ?lon0) * ofn:cos( ((?lat + ?lat0)/2) * ofn:pi() / 180 ) AS ?dx ) .
    BIND(  ?lat - ?lat0  AS ?dy ) .
    BIND(ofn:sqrt( (?dx * ?dx) + (?dy * ?dy) ) * 111.32 AS ?distance_km_approx) .
    ?s rdf:type df:School;
    df:has_school_type "primaria";
    df:has_location ?m1 .
    FILTER( ?distance_km_approx <= 20 )
} ORDER BY ASC(?distance_km_approx)
```
