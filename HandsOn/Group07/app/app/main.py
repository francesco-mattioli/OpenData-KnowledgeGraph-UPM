from fastapi import FastAPI, APIRouter, Query, HTTPException, Request
from fastapi.templating import Jinja2Templates

from pathlib import Path
from rdflib_endpoint import SparqlRouter
from typing import Optional, Any

from app.schemas import ChargingStation, StationSearchResults
from app.data.station_data import STATIONS
from app.chargerGraph import chargerGraph


BASE_PATH = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))

app = FastAPI(title="Charging Station API", openapi_url="/openapi.json")

api_router = APIRouter()


@api_router.get("/", status_code=200)
def root(request: Request) -> dict:
    """
    Root GET
    """
    return TEMPLATES.TemplateResponse(
        "index.html",
        {"request": request, "stations": STATIONS}
    )


@api_router.get("/station/{station_id}", status_code=200, response_model=ChargingStation)
def fetch_station(*, station_id: int) -> Any:
    """
    Fetch a single station by ID
    :param station_id: number of the recipe
    :return:
    """

    result = [station for station in STATIONS if station["id"] == station_id]
    if not result:
        raise HTTPException(
            status_code=404, detail=f"Station with ID {station_id} not found"
        )
    return result[0]


@api_router.get("/search/", status_code=200, response_model=StationSearchResults)
def search_station(
        keyword: Optional[str] = Query(None, min_length=3, examples="BMW"),
        max_results: Optional[int] = 10
) -> dict:
    """
    Search for stations based on label keyword
    :param keyword:
    :param max_results:
    :return:
    """
    if not keyword:
        return {"results": STATIONS[:max_results]}
    results = filter(lambda station: keyword.lower() in station["charging_station"].lower(), STATIONS)
    return {"results": list(results)[:max_results]}


@api_router.get("/search-city/", status_code=200, response_model=StationSearchResults)
def search_city(
        keyword: Optional[str] = None, max_results: Optional[int] = 10
) -> dict:
    """
    Search for stations based on label keyword
    :param keyword:
    :param max_results:
    :return:
    """
    if not keyword:
        return {"results": STATIONS[:max_results]}
    results = filter(lambda station: keyword.lower() in station["city"].lower(), STATIONS)
    return {"results": list(results)[:max_results]}


sparql_router = SparqlRouter(
    graph=chargerGraph,
    path="/chargy/",
    title="SPARQL endpoint for RDFLib graph",
    description='Our charger sparql endpoint',
    version="0.1.0",
    public_url='https://my-endpoint-url/',
)
app.include_router(api_router)  # Basic router coming from FastAPI
app.include_router(sparql_router)  # Router taken from rdflib


if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="debug")
