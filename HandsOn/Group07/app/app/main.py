from fastapi import FastAPI, APIRouter, Query, HTTPException, Request
from fastapi.templating import Jinja2Templates

from pathlib import Path
from rdflib import Graph
from rdflib_endpoint import SparqlRouter
from rdflib.plugins.sparql import prepareQuery
from typing import Optional, Any


BASE_PATH = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))

app = FastAPI(title="Charging Station API", openapi_url="/openapi.json")

api_router = APIRouter()


@api_router.get("/", status_code=200)
def root(request: Request) -> dict:
    """
    Root GET
    """
    g = Graph().parse(str(BASE_PATH / "data" / "rdf-withlinks.ttl"), format="turtle")
    query = prepareQuery("""
            PREFIX ont: <https://www.chargeup.io/group07/ontology#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?station ?label ?address WHERE {
                ?station a ont:ChargingStation .
                ?station ont:hasStreetAddress ?address .
                ?station rdfs:label ?label .
            }
            """)
    results = g.query(query)
    output = [
        {"station": str(result[0]),
         "label": str(result[1]),
         "address": str(result[2]),
         }
        for result in results]
    return TEMPLATES.TemplateResponse(
        "index.html",
        {"request": request, "stations": output}
    )


@api_router.get("/search/", status_code=200)
def search_station(
        keyword: Optional[str] = Query(None, min_length=3, examples="BMW"),
        max_results: Optional[int] = 10
) -> dict:
    """
    To implement: Search for stations based on label keyword
    """
    pass


@api_router.get("/cities/", status_code=200)
def get_cities() -> any:
    """Get all the cities existing in the knowledge graph."""
    g = Graph().parse(str(BASE_PATH / "data" / "rdf-withlinks.ttl"), format="turtle")
    query = prepareQuery("""
    PREFIX ont: <https://www.chargeup.io/group07/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?city ?label ?dbpedia_city WHERE {
        ?city a ont:City .
        ?city rdfs:label ?label .
        ?city <http://www.w3.org/2002/07/owl#sameAs> ?dbpedia_city
    }
    """)
    results = g.query(query)
    output = [{"city": str(result[0]),
               "label": str(result[1]),
               "dbpedia_city": str(result[2])
               } for result in results]
    return output


@api_router.get("/stations/", status_code=200)
def get_stations() -> any:
    """Get all the stations and their street adresses"""
    g = Graph().parse(str(BASE_PATH / "data" / "rdf-withlinks.ttl"), format="turtle")
    query = prepareQuery("""
        PREFIX ont: <https://www.chargeup.io/group07/ontology#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?station ?label ?address WHERE {
            ?station a ont:ChargingStation .
            ?station ont:hasStreetAddress ?address .
            ?station rdfs:label ?label .
        }
        """)
    results = g.query(query)
    output = [
              {"station": str(result[0]),
               "label": str(result[1]),
               "address": str(result[2]),
               }
              for result in results]
    return output


@api_router.get("/station-by-city/", status_code=200)
def get_station_by_city(
        city: Optional[str] = Query(None, min_length=3, examples="Darien"),
        max_results: Optional[int] = 10
) -> dict:
    """To implement: lower case indifference"""
    g = Graph().parse(str(BASE_PATH / "data" / "rdf-withlinks.ttl"), format="turtle")
    query = prepareQuery(f"""
    PREFIX ont: <https://www.chargeup.io/group07/ontology#>
    SELECT ?station ?address ?city
    WHERE {{
        ?station a ont:ChargingStation .
        ?station ont:hasStreetAddress ?address .
        ?address ont:hasCity ?city .
        ?city rdfs:label "{city}" .
    }}
    LIMIT {max_results}
    """)
    results = g.query(query)
    output = [
        {"station": str(result[0]),
         "address": str(result[1]),
         "city": str(result[2]),
         }
        for result in results]
    return output


sparql_router = SparqlRouter(
    graph=Graph().parse(str(BASE_PATH / "data" / "rdf-withlinks.ttl"), format="turtle"),
    path="/chargy/",
    title="SPARQL endpoint for RDFLib graph",
    description='Our charger sparql endpoint',
    version="0.1.0",
    public_url='https://my-endpoint-url/',
    example_query="""
    PREFIX ont: <https://www.chargeup.io/group07/ontology#>
    SELECT ?city WHERE {
        ?city a ont:City .
    }
    LIMIT 5
    """
)
app.include_router(api_router)  # Basic router coming from FastAPI
app.include_router(sparql_router)  # Router taken from rdflib


if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="debug")
