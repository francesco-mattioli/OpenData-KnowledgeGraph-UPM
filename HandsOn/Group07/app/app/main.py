from fastapi import FastAPI, APIRouter, Query, HTTPException, Request
from fastapi.templating import Jinja2Templates

from typing import Optional, Any
from pathlib import Path

from app.schemas import ChargingStation, StationSearchResults
from app.station_data import STATIONS


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


app.include_router(api_router)


if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="debug")
